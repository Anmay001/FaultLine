import os
import re
from pathlib import Path
from typing import Optional
from git import Repo, GitCommandError

from app.sandbox.types import SandboxConfig, SandboxMetadata
from datetime import datetime, timezone


class RepositoryClonerError(Exception):
    """Base exception for cloning failures."""
    pass


class InvalidRepositoryURLError(RepositoryClonerError):
    """Raised when repository URL fails security checks."""
    pass


class CloneTimeoutError(RepositoryClonerError):
    """Raised when cloning exceeds the allocated timeout."""
    pass


class RepositoryCloner:
    # Allowed URL formats: https, http, or ssh for GitHub/GitLab/Bitbucket or standard git hosts
    # Also allows file paths if explicitly testing locally
    ALLOWED_URL_REGEX = re.compile(
        r'^(https?://|git@)[a-zA-Z0-9_\-\.]+(/|:)[a-zA-Z0-9_\-\./]+\.git/?$|'
        r'^(https?://)github\.com/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+/?$'
    )

    @classmethod
    def validate_url(cls, url: str, allow_local_paths: bool = False) -> str:
        """
        Validate URL for security, preventing SSRF, command injection, and unexpected protocols.
        """
        url = url.strip()
        if not url:
            raise InvalidRepositoryURLError("Repository URL cannot be empty.")

        # Check for dangerous shell metacharacters
        dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "\n", "\r", "\0"]
        if any(char in url for char in dangerous_chars):
            raise InvalidRepositoryURLError(f"Repository URL contains illegal characters: {url}")

        if allow_local_paths and (Path(url).exists() or url.startswith("file://")):
            return url

        if not cls.ALLOWED_URL_REGEX.match(url):
            # Also support standard github repo urls without .git suffix
            if url.startswith("https://github.com/") or url.startswith("https://gitlab.com/"):
                return url
            raise InvalidRepositoryURLError(
                f"Invalid or unsupported repository URL format: {url}. "
                "Only standard HTTPS/SSH Git URLs are allowed."
            )

        return url

    @classmethod
    def get_sanitized_env(cls) -> dict:
        """
        Sanitize environment to prevent leaking host secrets or arbitrary SSH execution.
        """
        sanitized = os.environ.copy()
        # Remove potential secret tokens or sensitive SSH bindings
        keys_to_remove = [
            "AWS_SECRET_ACCESS_KEY",
            "AWS_ACCESS_KEY_ID",
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "GITHUB_TOKEN",
            "GH_TOKEN",
            "GIT_SSH_COMMAND",
            "SSH_AUTH_SOCK",
        ]
        for key in keys_to_remove:
            sanitized.pop(key, None)
        
        # Ensure non-interactive Git
        sanitized["GIT_TERMINAL_PROMPT"] = "0"
        return sanitized

    @classmethod
    def clone(cls, config: SandboxConfig, allow_local_paths: bool = False) -> Path:
        """
        Clones repository into the destination directory within the sandbox.
        """
        valid_url = cls.validate_url(config.repo_url, allow_local_paths=allow_local_paths)
        target_dir = Path(config.custom_sandbox_dir).resolve()
        if not target_dir:
            raise RepositoryClonerError("Target sandbox destination path must be provided.")

        # Ensure parent directory exists
        target_dir.parent.mkdir(parents=True, exist_ok=True)

        # If target directory already exists and contains files, clean it up first
        if target_dir.exists() and any(target_dir.iterdir()):
            import shutil
            import stat
            def _remove_readonly(func, path, exc_info):
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception:
                    pass
            shutil.rmtree(target_dir, onerror=_remove_readonly)

        clone_kwargs = {
            "env": cls.get_sanitized_env(),
        }
        if config.depth > 0:
            clone_kwargs["depth"] = config.depth
        if config.target_branch:
            clone_kwargs["branch"] = config.target_branch

        try:
            repo = Repo.clone_from(
                valid_url,
                to_path=str(target_dir),
                **clone_kwargs
            )
            repo.close()
            return target_dir
        except GitCommandError as e:
            err_msg = str(e.stderr or str(e))
            if "could not read Username" in err_msg or "Authentication failed" in err_msg or "Repository not found" in err_msg:
                raise RepositoryClonerError(
                    f"Repository '{valid_url}' is private or does not exist. Please ensure the repository is public."
                )
            # If specified branch does not exist on remote, retry with repository default branch
            if config.target_branch and ("Remote branch" in err_msg or "not found in upstream" in err_msg):
                try:
                    if target_dir.exists():
                        import shutil
                        shutil.rmtree(target_dir, onerror=_remove_readonly)
                    clone_kwargs.pop("branch", None)
                    repo = Repo.clone_from(
                        valid_url,
                        to_path=str(target_dir),
                        **clone_kwargs
                    )
                    repo.close()
                    return target_dir
                except Exception as retry_err:
                    raise RepositoryClonerError(f"Git clone operation failed: {str(retry_err)}")
            raise RepositoryClonerError(f"Git clone operation failed: {err_msg}")
        except Exception as e:
            raise RepositoryClonerError(f"Unexpected error during repository clone: {str(e)}")
