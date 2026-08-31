from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SandboxConfig:
    analysis_id: str
    repo_url: str
    target_branch: Optional[str] = None
    depth: int = 100
    timeout_seconds: int = 120
    custom_sandbox_dir: Optional[Path] = None


@dataclass
class SandboxMetadata:
    analysis_id: str
    repo_url: str
    sandbox_path: Path
    commit_hash: str
    branch: str
    total_files: int
    total_size_bytes: int
    created_at: datetime
    is_active: bool = True
    file_extensions: Dict[str, int] = field(default_factory=dict)
