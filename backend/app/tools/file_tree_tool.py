import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ManifestFile:
    relative_path: str
    file_type: str
    size_bytes: int
    content: str


@dataclass
class FileTreeSummary:
    formatted_tree: str
    total_files: int
    total_dirs: int
    total_loc: int
    languages: Dict[str, float]  # extension -> percentage
    manifests: List[ManifestFile]
    has_tests: bool
    has_documentation: bool
    has_docker: bool
    has_ci: bool


class FileTreeTool:
    """Tool for scanning repository topography, extracting file trees, and identifying manifests."""

    EXCLUDED_DIRS: Set[str] = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".next",
        "dist",
        "build",
        "coverage",
        ".turbo",
    }

    MANIFEST_PATTERNS: Dict[str, str] = {
        "package.json": "npm/node",
        "package-lock.json": "npm/node-lock",
        "pnpm-lock.yaml": "pnpm-lock",
        "yarn.lock": "yarn-lock",
        "pyproject.toml": "python-project",
        "requirements.txt": "python-requirements",
        "Pipfile": "pipenv",
        "poetry.lock": "poetry-lock",
        "Cargo.toml": "rust-cargo",
        "Cargo.lock": "rust-lock",
        "go.mod": "golang-module",
        "go.sum": "golang-sum",
        "pom.xml": "java-maven",
        "build.gradle": "java-gradle",
        "Dockerfile": "docker",
        "docker-compose.yml": "docker-compose",
        "docker-compose.yaml": "docker-compose",
        "README.md": "documentation",
        "README": "documentation",
        "CONTRIBUTING.md": "documentation",
        "tsconfig.json": "typescript-config",
        "pytest.ini": "python-pytest",
        "setup.py": "python-setup",
    }

    LANGUAGE_MAP: Dict[str, str] = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript (React)",
        ".ts": "TypeScript",
        ".tsx": "TypeScript (React)",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".c": "C",
        ".cpp": "C++",
        ".h": "C/C++ Header",
        ".rb": "Ruby",
        ".php": "PHP",
        ".html": "HTML",
        ".css": "CSS",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".md": "Markdown",
        ".sql": "SQL",
        ".sh": "Shell",
    }

    @classmethod
    def analyze_tree(
        cls,
        repo_path: Path,
        max_depth: int = 4,
        max_files_in_tree: int = 150,
        max_manifest_bytes: int = 15_000,
    ) -> FileTreeSummary:
        """
        Analyzes directory structure, extracts formatted ASCII tree, detects manifests and language distribution.
        """
        repo_path = Path(repo_path)
        if not repo_path.exists():
            return FileTreeSummary(
                formatted_tree="",
                total_files=0,
                total_dirs=0,
                total_loc=0,
                languages={},
                manifests=[],
                has_tests=False,
                has_documentation=False,
                has_docker=False,
                has_ci=False,
            )

        tree_lines: List[str] = [f"{repo_path.name}/"]
        total_files = 0
        total_dirs = 0
        total_loc = 0
        ext_counts: Dict[str, int] = {}
        manifests: List[ManifestFile] = []

        has_tests = False
        has_documentation = False
        has_docker = False
        has_ci = False

        def _walk(current_dir: Path, prefix: str = "", depth: int = 0):
            nonlocal total_files, total_dirs, total_loc, has_tests, has_documentation, has_docker, has_ci

            if depth > max_depth or total_files >= max_files_in_tree:
                return

            try:
                entries = sorted(list(current_dir.iterdir()), key=lambda e: (not e.is_dir(), e.name.lower()))
            except (PermissionError, OSError):
                return

            # Filter excluded dirs
            filtered_entries = [
                e for e in entries if e.name not in cls.EXCLUDED_DIRS and not e.name.startswith(".")
            ]

            # Special check for .github
            if (current_dir / ".github").exists():
                has_ci = True

            count = len(filtered_entries)
            for i, entry in enumerate(filtered_entries):
                is_last = (i == count - 1)
                connector = "└── " if is_last else "├── "
                sub_prefix = "    " if is_last else "│   "

                if entry.is_dir():
                    total_dirs += 1
                    lower_name = entry.name.lower()
                    if "test" in lower_name or "spec" in lower_name:
                        has_tests = True

                    tree_lines.append(f"{prefix}{connector}{entry.name}/")
                    _walk(entry, prefix + sub_prefix, depth + 1)
                else:
                    total_files += 1
                    file_name = entry.name
                    lower_name = file_name.lower()

                    if "test" in lower_name or "spec" in lower_name:
                        has_tests = True
                    if "readme" in lower_name or "doc" in lower_name:
                        has_documentation = True
                    if "docker" in lower_name:
                        has_docker = True

                    ext = entry.suffix.lower() or "no_ext"
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1

                    # Check for manifest match
                    if file_name in cls.MANIFEST_PATTERNS or lower_name in cls.MANIFEST_PATTERNS:
                        m_type = cls.MANIFEST_PATTERNS.get(file_name) or cls.MANIFEST_PATTERNS.get(lower_name, "manifest")
                        try:
                            content = entry.read_text(encoding="utf-8", errors="replace")[:max_manifest_bytes]
                            rel_p = entry.relative_to(repo_path).as_posix()
                            manifests.append(
                                ManifestFile(
                                    relative_path=rel_p,
                                    file_type=m_type,
                                    size_bytes=entry.stat().st_size,
                                    content=content,
                                )
                            )
                        except Exception:
                            pass

                    # Rough LOC calculation for code files
                    if ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".c", ".cpp"]:
                        try:
                            with open(entry, "rb") as f:
                                lines = sum(1 for _ in f)
                                total_loc += lines
                        except Exception:
                            pass

                    tree_lines.append(f"{prefix}{connector}{entry.name}")

        _walk(repo_path)

        # Calculate language percentages
        total_ext_files = sum(ext_counts.values()) or 1
        languages: Dict[str, float] = {
            cls.LANGUAGE_MAP.get(ext, ext): round((count / total_ext_files) * 100, 1)
            for ext, count in ext_counts.items()
        }

        return FileTreeSummary(
            formatted_tree="\n".join(tree_lines),
            total_files=total_files,
            total_dirs=total_dirs,
            total_loc=total_loc,
            languages=languages,
            manifests=manifests,
            has_tests=has_tests,
            has_documentation=has_documentation,
            has_docker=has_docker,
            has_ci=has_ci,
        )
