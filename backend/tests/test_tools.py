import pytest
import tempfile
from pathlib import Path
from git import Repo

from app.tools.git_tool import GitTool
from app.tools.ruff_tool import RuffTool
from app.tools.file_tree_tool import FileTreeTool


def test_file_tree_tool_with_sample_project():
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        
        # Create nested folders
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / ".git").mkdir()
        (root / ".venv").mkdir()

        # Create files
        (root / "README.md").write_text("# Project Docs\nWelcome to FaultLine.", encoding="utf-8")
        (root / "pyproject.toml").write_text("[project]\nname = 'demo'\nversion = '0.1.0'", encoding="utf-8")
        (root / "src" / "index.py").write_text("print('hello world')", encoding="utf-8")
        (root / "src" / "utils.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        (root / "tests" / "test_index.py").write_text("def test_ok(): assert True", encoding="utf-8")
        (root / ".venv" / "ignore_me.py").write_text("dummy", encoding="utf-8")

        summary = FileTreeTool.analyze_tree(root)

        assert summary.total_files == 5 # README, pyproject, index, utils, test_index (ignoring .venv & .git)
        assert summary.has_tests is True
        assert summary.has_documentation is True
        assert "Python" in summary.languages
        assert len(summary.manifests) >= 2 # README.md & pyproject.toml
        assert "pyproject.toml" in [m.relative_path for m in summary.manifests]
        assert "ignore_me.py" not in summary.formatted_tree


def test_git_tool_analysis():
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir)
        repo = Repo.init(str(repo_path))

        # Commit 1
        f1 = repo_path / "core.py"
        f1.write_text("def core(): pass", encoding="utf-8")
        repo.index.add(["core.py"])
        repo.index.commit("Initial setup of core module")

        # Commit 2 (Bugfix)
        f1.write_text("def core():\n    # fix null pointer bug\n    return 42\n", encoding="utf-8")
        repo.index.add(["core.py"])
        repo.index.commit("fix: resolve critical null pointer bug in core")

        # Commit 3 (Another commit)
        f2 = repo_path / "helpers.py"
        f2.write_text("def help(): pass", encoding="utf-8")
        repo.index.add(["helpers.py"])
        repo.index.commit("Add helper utilities")

        repo.close()

        result = GitTool.analyze_repository(repo_path)
        assert result.total_commits == 3
        assert result.bugfix_commits == 1
        assert len(result.top_churn_files) >= 1
        assert result.top_churn_files[0].file_path == "core.py"
        assert result.top_churn_files[0].commit_count == 2
        assert result.top_churn_files[0].bugfix_count == 1


def test_ruff_tool_ast_complexity():
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        complex_py = root / "complex_logic.py"
        
        # Construct a high cyclomatic complexity Python function
        complex_code = """
def process_data(val):
    if val == 1:
        return 'one'
    elif val == 2:
        return 'two'
    elif val == 3:
        return 'three'
    elif val == 4:
        return 'four'
    elif val == 5:
        return 'five'
    elif val == 6:
        return 'six'
    elif val == 7:
        return 'seven'
    elif val == 8:
        return 'eight'
    elif val == 9:
        return 'nine'
    elif val == 10:
        return 'ten'
    elif val == 11:
        return 'eleven'
    return 'other'
"""
        complex_py.write_text(complex_code, encoding="utf-8")

        res = RuffTool.run_ruff(root)
        assert res.execution_success is True
        assert len(res.complexity_hotspots) >= 1
        assert res.complexity_hotspots[0]["function"] == "process_data"
        assert res.complexity_hotspots[0]["complexity"] >= 10
