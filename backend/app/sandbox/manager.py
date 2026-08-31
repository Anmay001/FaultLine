import os
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from git import Repo

from app.core.config import settings
from app.sandbox.cloner import RepositoryCloner, RepositoryClonerError
from app.sandbox.types import SandboxConfig, SandboxMetadata


def _remove_readonly(func, path, exc_info):
    """Clear readonly bit and retry removal (handles Windows git repo delete locks)."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


class SandboxManager:
    """Manages creation, inspection, path-traversal safety, and teardown of isolated sandboxes."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir or settings.SANDBOX_BASE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_sandbox_path(self, analysis_id: str, custom_sandbox_path: Optional[Path] = None) -> Path:
        if custom_sandbox_path and Path(custom_sandbox_path).exists():
            return Path(custom_sandbox_path).resolve()

        primary = (self.base_dir / analysis_id).resolve()
        if primary.exists():
            return primary

        # Fallback locations for previous runs
        legacy_candidates = [
            Path(tempfile.gettempdir()) / "faultline" / analysis_id,
            Path(tempfile.gettempdir()) / "repoguard" / analysis_id,
            Path("/tmp/faultline") / analysis_id,
            Path("/tmp/repoguard") / analysis_id,
        ]
        for candidate in legacy_candidates:
            if candidate.exists():
                return candidate.resolve()

        return primary

    def create_sandbox(
        self,
        analysis_id: str,
        repo_url: str,
        target_branch: Optional[str] = None,
        depth: int = 100,
        allow_local_paths: bool = False,
    ) -> SandboxMetadata:
        """
        Creates an isolated sandbox directory and clones the repository into it.
        """
        sandbox_path = self.get_sandbox_path(analysis_id)

        # If directory already exists, clean it up first
        if sandbox_path.exists():
            self.cleanup_sandbox(analysis_id)

        config = SandboxConfig(
            analysis_id=analysis_id,
            repo_url=repo_url,
            target_branch=target_branch,
            depth=depth,
            timeout_seconds=settings.SANDBOX_TIMEOUT_SECONDS,
            custom_sandbox_dir=sandbox_path,
        )

        # Clone repository
        RepositoryCloner.clone(config, allow_local_paths=allow_local_paths)

        # Inspect and generate metadata
        return self.inspect_sandbox(analysis_id, repo_url)

    def inspect_sandbox(self, analysis_id: str, repo_url: str, custom_sandbox_path: Optional[Path] = None) -> SandboxMetadata:
        """
        Inspects an existing sandbox and extracts branch, commit hash, file counts, and byte sizes.
        """
        sandbox_path = self.get_sandbox_path(analysis_id, custom_sandbox_path=custom_sandbox_path)
        if not sandbox_path.exists():
            raise FileNotFoundError(f"Sandbox not found for analysis {analysis_id}")

        commit_hash = "unknown"
        branch_name = "unknown"

        repo = None
        try:
            repo = Repo(str(sandbox_path))
            commit_hash = repo.head.commit.hexsha
            try:
                branch_name = repo.active_branch.name
            except TypeError:
                branch_name = "detached"
        except Exception:
            pass
        finally:
            if repo:
                repo.close()

        total_files = 0
        total_size = 0
        extension_counts: Dict[str, int] = {}

        for root, dirs, files in os.walk(sandbox_path):
            # Skip .git directory to keep file counts focused on code
            if ".git" in dirs:
                dirs.remove(".git")

            for file in files:
                total_files += 1
                file_path = Path(root) / file
                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                except OSError:
                    pass

                ext = file_path.suffix.lower() or "no_ext"
                extension_counts[ext] = extension_counts.get(ext, 0) + 1

        return SandboxMetadata(
            analysis_id=analysis_id,
            repo_url=repo_url,
            sandbox_path=sandbox_path,
            commit_hash=commit_hash,
            branch=branch_name,
            total_files=total_files,
            total_size_bytes=total_size,
            created_at=datetime.now(timezone.utc),
            is_active=True,
            file_extensions=extension_counts,
        )

    def get_safe_file_path(self, analysis_id: str, relative_path: str, custom_sandbox_path: Optional[Path] = None) -> Path:
        """
        Resolves a relative file path safely inside the sandbox, preventing directory traversal.
        """
        sandbox_path = self.get_sandbox_path(analysis_id, custom_sandbox_path=custom_sandbox_path).resolve()
        target = (sandbox_path / relative_path.lstrip("/\\")).resolve()

        is_safe = False
        try:
            is_safe = target.is_relative_to(sandbox_path)
        except (AttributeError, ValueError):
            pass

        if not is_safe:
            norm_target = str(target).lower().replace("\\", "/")
            norm_sandbox = str(sandbox_path).lower().replace("\\", "/")
            is_safe = norm_target.startswith(norm_sandbox)

        if not is_safe:
            raise PermissionError(f"Directory traversal attack detected: {relative_path}")

        return target

    def read_file(self, analysis_id: str, relative_path: str, max_bytes: int = 200_000, custom_sandbox_path: Optional[Path] = None) -> str:
        """
        Safely reads a file inside the sandbox.
        """
        target = self.get_safe_file_path(analysis_id, relative_path, custom_sandbox_path=custom_sandbox_path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found in sandbox: {relative_path}")

        with open(target, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)

    def list_files(self, analysis_id: str, max_depth: int = 10, custom_sandbox_path: Optional[Path] = None) -> List[str]:
        """
        Lists relative paths of all files in the sandbox, ignoring .git.
        """
        sandbox_path = self.get_sandbox_path(analysis_id, custom_sandbox_path=custom_sandbox_path)
        if not sandbox_path.exists():
            return []

        rel_paths = []
        sandbox_str = str(sandbox_path.resolve())
        for root, dirs, files in os.walk(sandbox_str):
            if ".git" in dirs:
                dirs.remove(".git")
            
            # Check depth
            rel_dir = os.path.relpath(root, sandbox_str)
            if rel_dir != "." and len(Path(rel_dir).parts) > max_depth:
                continue

            for file in files:
                full_path = os.path.join(root, file)
                rel_file = os.path.relpath(full_path, sandbox_str).replace("\\", "/").lstrip("./")
                rel_paths.append(rel_file)

        return sorted(rel_paths)

    def cleanup_sandbox(self, analysis_id: str, custom_sandbox_path: Optional[Path] = None) -> bool:
        """
        Safely deletes the sandbox directory and all its contents.
        """
        import gc
        import time

        sandbox_path = self.get_sandbox_path(analysis_id, custom_sandbox_path=custom_sandbox_path)
        if not sandbox_path.exists():
            return False

        gc.collect()

        for _ in range(5):
            try:
                shutil.rmtree(sandbox_path, onerror=_remove_readonly)
                if not sandbox_path.exists():
                    return True
            except Exception:
                time.sleep(0.05)

        return not sandbox_path.exists()


sandbox_manager = SandboxManager()
