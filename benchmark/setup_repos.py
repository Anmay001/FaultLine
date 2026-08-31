import os
import stat
import shutil
from pathlib import Path
from git import Repo

BENCHMARK_DIR = Path(__file__).resolve().parent / "repos"


def safe_rmtree(path: Path):
    if not path.exists():
        return
    def _remove_readonly(func, file_path, exc_info):
        try:
            os.chmod(file_path, stat.S_IWRITE)
            func(file_path)
        except Exception:
            pass
    shutil.rmtree(path, onerror=_remove_readonly)


def setup_healthy_repo(base_dir: Path) -> Path:
    repo_path = base_dir / "repo_healthy"
    safe_rmtree(repo_path)
    repo_path.mkdir(parents=True, exist_ok=True)

    # 1. README
    (repo_path / "README.md").write_text(
        "# Healthy Service\n\n"
        "A robust, fully tested microservice.\n\n"
        "## Installation\n```bash\npip install -r requirements.txt\n```\n\n"
        "## Testing\n```bash\npytest\n```\n",
        encoding="utf-8"
    )

    # 2. Pinned Requirements
    (repo_path / "requirements.txt").write_text(
        "fastapi==0.115.0\n"
        "uvicorn==0.30.0\n"
        "pydantic==2.8.2\n"
        "pytest==8.3.2\n",
        encoding="utf-8"
    )

    # 3. Clean source code
    src = repo_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "calculator.py").write_text(
        "def add(a: int, b: int) -> int:\n"
        "    \"\"\"Return the sum of two integers.\"\"\"\n"
        "    return a + b\n\n"
        "def multiply(a: int, b: int) -> int:\n"
        "    \"\"\"Return the product of two integers.\"\"\"\n"
        "    return a * b\n",
        encoding="utf-8"
    )

    # 4. Complete Test Suite
    tests = repo_path / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("", encoding="utf-8")
    (tests / "test_calculator.py").write_text(
        "from src.calculator import add, multiply\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n"
        "    assert add(-1, 1) == 0\n\n"
        "def test_multiply():\n"
        "    assert multiply(3, 4) == 12\n",
        encoding="utf-8"
    )

    # 5. CI / GitHub Actions
    gh = repo_path / ".github" / "workflows"
    gh.mkdir(parents=True)
    (gh / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: pytest\n",
        encoding="utf-8"
    )

    # Init Git and Commit
    repo = Repo.init(str(repo_path))
    repo.index.add(["README.md", "requirements.txt", "src/calculator.py", "tests/test_calculator.py", ".github/workflows/ci.yml"])
    repo.index.commit("Initial clean release with 100% test coverage and CI")
    repo.close()

    return repo_path


def setup_dependency_risk_repo(base_dir: Path) -> Path:
    repo_path = base_dir / "repo_dependency_risk"
    safe_rmtree(repo_path)
    repo_path.mkdir(parents=True, exist_ok=True)

    # 1. Package.json with unpinned wildcard & vulnerable express
    (repo_path / "package.json").write_text(
        '{\n'
        '  "name": "insecure-gateway",\n'
        '  "version": "1.0.0",\n'
        '  "dependencies": {\n'
        '    "express": "4.16.0",\n'
        '    "lodash": "*",\n'
        '    "axios": "0.21.1"\n'
        '  }\n'
        '}\n',
        encoding="utf-8"
    )

    # 2. Missing lockfile intentional
    # 3. Unpinned requirements.txt
    (repo_path / "requirements.txt").write_text(
        "requests\n"
        "flask>=0.12\n"
        "django\n",
        encoding="utf-8"
    )

    # 4. Minimal README
    (repo_path / "README.md").write_text(
        "# Insecure Gateway\n"
        "Installation: npm install\n",
        encoding="utf-8"
    )

    # 5. App entrypoint
    src = repo_path / "src"
    src.mkdir()
    (src / "app.js").write_text(
        "const express = require('express');\n"
        "const app = express();\n"
        "app.get('/', (req, res) => res.send('ok'));\n",
        encoding="utf-8"
    )

    repo = Repo.init(str(repo_path))
    repo.index.add(["package.json", "requirements.txt", "README.md", "src/app.js"])
    repo.index.commit("Initial gateway with unpinned and outdated dependencies")
    repo.close()

    return repo_path


def setup_high_churn_no_tests_repo(base_dir: Path) -> Path:
    repo_path = base_dir / "repo_high_churn_no_tests"
    safe_rmtree(repo_path)
    repo_path.mkdir(parents=True, exist_ok=True)

    # 1. High complexity core module with dangerous patterns, swallowed exceptions & TODOs
    payment_py_content = """
import os

def process_transaction(amount, payment_type, user_auth):
    # TODO: Add transaction logging
    # TODO: Implement circuit breaker
    # TODO: Fix concurrent balance update race condition
    # TODO: Handle currency rounding bugs
    # TODO: Add audit trail

    # Dangerous pattern: Hardcoded secret credential
    secret_key = "sk_live_999888777666555444333"

    # Swallowed exception
    try:
        if amount <= 0:
            raise ValueError("Invalid amount")
    except Exception:
        pass

    # Arbitrary code execution vulnerability
    if user_auth.get("eval_hook"):
        eval(user_auth["eval_hook"])

    # Cyclomatic complexity > 20
    if payment_type == 1:
        if amount > 1000:
            return "tier1_large"
        else:
            return "tier1_small"
    elif payment_type == 2:
        if amount > 500:
            return "tier2_large"
        else:
            return "tier2_small"
    elif payment_type == 3:
        return "tier3"
    elif payment_type == 4:
        return "tier4"
    elif payment_type == 5:
        return "tier5"
    elif payment_type == 6:
        return "tier6"
    elif payment_type == 7:
        return "tier7"
    elif payment_type == 8:
        return "tier8"
    elif payment_type == 9:
        return "tier9"
    elif payment_type == 10:
        return "tier10"
    elif payment_type == 11:
        return "tier11"
    elif payment_type == 12:
        return "tier12"
    return "unknown"
"""
    src = repo_path / "src"
    src.mkdir()
    (src / "payment_engine.py").write_text(payment_py_content, encoding="utf-8")

    # Circular dependencies
    (src / "auth_service.py").write_text(
        "import session_service\ndef verify_auth(): return session_service.get_session()\n",
        encoding="utf-8"
    )
    (src / "session_service.py").write_text(
        "import auth_service\ndef get_session(): return auth_service.verify_auth()\n",
        encoding="utf-8"
    )

    # Missing test directory completely!
    (repo_path / "README.md").write_text("# Core Payment Gateway\nOutdated docs.\n", encoding="utf-8")

    repo = Repo.init(str(repo_path))
    repo.index.add(["src/payment_engine.py", "src/auth_service.py", "src/session_service.py", "README.md"])
    repo.index.commit("Initial payment core engine")

    # Generate 5 recurring bugfix commits touching payment_engine.py to trigger Git churn & defect density agents
    for i in range(1, 6):
        updated_content = payment_py_content + f"\n# Emergency hotfix patch {i} for null pointer\n"
        (src / "payment_engine.py").write_text(updated_content, encoding="utf-8")
        repo.index.add(["src/payment_engine.py"])
        repo.index.commit(f"fix: resolve critical payment processing bug #{i}")

    repo.close()
    return repo_path


def generate_all_benchmark_repos():
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    print("Setting up synthetic benchmark test repositories...")

    r1 = setup_healthy_repo(BENCHMARK_DIR)
    print(f"  [1/3] Created Healthy Repo: {r1}")

    r2 = setup_dependency_risk_repo(BENCHMARK_DIR)
    print(f"  [2/3] Created Dependency Risk Repo: {r2}")

    r3 = setup_high_churn_no_tests_repo(BENCHMARK_DIR)
    print(f"  [3/3] Created High-Churn Failure-Prone Repo: {r3}")

    print("All benchmark repositories initialized successfully.")


if __name__ == "__main__":
    generate_all_benchmark_repos()
