import pytest
from pathlib import Path
from app.sandbox.cloner import RepositoryCloner, InvalidRepositoryURLError
from app.sandbox.manager import SandboxManager


def test_url_validation_valid():
    valid_urls = [
        "https://github.com/fastapi/fastapi.git",
        "https://github.com/tiangolo/fastapi",
        "https://gitlab.com/gitlab-org/gitlab.git",
        "git@github.com:octocat/Hello-World.git",
    ]
    for url in valid_urls:
        validated = RepositoryCloner.validate_url(url)
        assert validated is not None


def test_url_validation_invalid_and_malicious():
    invalid_urls = [
        "",
        "https://github.com/foo/bar; rm -rf /",
        "https://github.com/foo/bar | cat /etc/passwd",
        "ftp://malicious.domain/repo.git",
        "file:///etc/shadow",
    ]
    for url in invalid_urls:
        with pytest.raises(InvalidRepositoryURLError):
            RepositoryCloner.validate_url(url)


def test_sandbox_lifecycle_with_local_git_repo(sample_local_git_repo: Path, temp_sandbox_base: Path):
    manager = SandboxManager(base_dir=temp_sandbox_base)
    analysis_id = "test-analysis-123"

    # 1. Create sandbox
    metadata = manager.create_sandbox(
        analysis_id=analysis_id,
        repo_url=str(sample_local_git_repo),
        allow_local_paths=True,
    )

    assert metadata.analysis_id == analysis_id
    assert metadata.sandbox_path.exists()
    assert metadata.total_files == 3
    assert ".py" in metadata.file_extensions
    assert ".md" in metadata.file_extensions
    assert len(metadata.commit_hash) == 40

    # 2. List files
    files = manager.list_files(analysis_id)
    assert "README.md" in files
    assert "src/main.py" in files
    assert "tests/test_main.py" in files

    # 3. Read file safely
    content = manager.read_file(analysis_id, "src/main.py")
    assert "def hello():" in content

    # 4. Path traversal prevention
    with pytest.raises(PermissionError):
        manager.read_file(analysis_id, "../../etc/passwd")

    with pytest.raises(PermissionError):
        manager.read_file(analysis_id, "../outside.txt")

    # 5. Cleanup
    assert manager.cleanup_sandbox(analysis_id) is True
    assert not metadata.sandbox_path.exists()
