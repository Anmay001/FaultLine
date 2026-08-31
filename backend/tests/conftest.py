import os
import sys
import tempfile
import pytest
import pytest_asyncio
from pathlib import Path
from typing import AsyncGenerator
from git import Repo
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Add backend directory to sys.path so 'app' imports work
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import Base, get_db
from app.main import app
from app.sandbox.manager import SandboxManager


@pytest.fixture(scope="session")
def temp_sandbox_base():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture(scope="session")
def sample_local_git_repo():
    """Creates a temporary initialized git repository for safe offline testing."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        repo_path = Path(tmp_dir)
        repo = Repo.init(str(repo_path))
        
        # Create sample files
        readme = repo_path / "README.md"
        readme.write_text("# Test Repo\nA test repository for FaultLine verification.", encoding="utf-8")
        
        src_dir = repo_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("def hello():\n    return 'world'\n", encoding="utf-8")
        
        test_dir = repo_path / "tests"
        test_dir.mkdir()
        test_py = test_dir / "test_main.py"
        test_py.write_text("from src.main import hello\ndef test_hello():\n    assert hello() == 'world'\n", encoding="utf-8")

        # Commit files
        repo.index.add(["README.md", "src/main.py", "tests/test_main.py"])
        repo.index.commit("Initial commit for testing")
        repo.close()
        
        yield repo_path


@pytest_asyncio.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides an isolated in-memory or temp SQLite async database for tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient for FastAPI endpoint testing with overridden database dependency."""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
