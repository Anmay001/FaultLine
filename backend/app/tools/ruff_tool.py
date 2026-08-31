import ast
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LintIssue:
    code: str
    message: str
    file_path: str
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    severity: str = "MEDIUM"
    fix_available: bool = False


@dataclass
class RuffAnalysisResult:
    total_issues: int
    issues_by_category: Dict[str, int]
    high_severity_issues: List[LintIssue]
    all_issues: List[LintIssue]
    complexity_hotspots: List[Dict[str, Any]]
    execution_success: bool = True
    error_message: Optional[str] = None


class ComplexityVisitor(ast.NodeVisitor):
    """Calculates McCabe cyclomatic complexity for Python functions."""
    def __init__(self):
        self.functions: List[Dict[str, Any]] = []

    def _calculate_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def visit_FunctionDef(self, node: ast.FunctionDef):
        complexity = self._calculate_complexity(node)
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "complexity": complexity,
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        complexity = self._calculate_complexity(node)
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "complexity": complexity,
        })
        self.generic_visit(node)


class RuffTool:
    """Wrapper for Ruff static analysis and AST cyclomatic complexity checks."""

    @classmethod
    def find_ruff_executable(cls) -> Optional[str]:
        # Check current python environment script dir
        venv_bin = Path(sys.executable).parent / ("ruff.exe" if os.name == "nt" else "ruff")
        if venv_bin.exists():
            return str(venv_bin)
        return shutil.which("ruff")

    @classmethod
    def analyze_python_ast(cls, repo_path: Path) -> List[Dict[str, Any]]:
        """Fallback and supplementary AST analysis for complexity across Python files."""
        hotspots = []
        for py_file in repo_path.glob("**/*.py"):
            # Skip hidden, virtual environments and caches
            if any(part.startswith(".") or part in ["node_modules", ".venv", "venv", "__pycache__"] for part in py_file.parts):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(py_file))
                visitor = ComplexityVisitor()
                visitor.visit(tree)

                for func in visitor.functions:
                    if func["complexity"] >= 10:  # McCabe complexity threshold
                        rel_path = py_file.relative_to(repo_path).as_posix()
                        hotspots.append({
                            "file": rel_path,
                            "function": func["name"],
                            "line": func["line"],
                            "complexity": func["complexity"],
                            "level": "CRITICAL" if func["complexity"] >= 20 else "HIGH",
                        })
            except Exception:
                continue

        return sorted(hotspots, key=lambda x: x["complexity"], reverse=True)

    @classmethod
    def run_ruff(cls, repo_path: Path, timeout_seconds: int = 30) -> RuffAnalysisResult:
        """
        Runs Ruff static analyzer against repository directory and parses diagnostic JSON.
        """
        repo_path = Path(repo_path)
        ruff_bin = cls.find_ruff_executable()
        ast_hotspots = cls.analyze_python_ast(repo_path)

        if not ruff_bin:
            # Fallback to pure AST analysis
            return RuffAnalysisResult(
                total_issues=len(ast_hotspots),
                issues_by_category={"COMPLEXITY": len(ast_hotspots)},
                high_severity_issues=[],
                all_issues=[],
                complexity_hotspots=ast_hotspots,
                execution_success=True,
                error_message="Ruff binary not in path, AST fallback utilized",
            )

        cmd = [
            ruff_bin,
            "check",
            str(repo_path),
            "--output-format", "json",
            "--exit-zero",
            "--exclude", ".venv,venv,node_modules,__pycache__,.git",
        ]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            raw_output = res.stdout.strip()
            if not raw_output:
                return RuffAnalysisResult(
                    total_issues=len(ast_hotspots),
                    issues_by_category={"COMPLEXITY": len(ast_hotspots)},
                    high_severity_issues=[],
                    all_issues=[],
                    complexity_hotspots=ast_hotspots,
                    execution_success=True,
                )

            data = json.loads(raw_output)
            parsed_issues: List[LintIssue] = []
            category_counts: Dict[str, int] = {}

            for item in data:
                code = item.get("code", "UNKNOWN")
                prefix = code[:1] if code else "OTHER"
                category_counts[prefix] = category_counts.get(prefix, 0) + 1

                # Classify severity based on rule prefix
                # S = Security (Bandit), E9 / F8 = Syntax/Undefined, C901 = Complexity
                severity = "LOW"
                if code.startswith("S") or code in ["F821", "F822", "E999"]:
                    severity = "CRITICAL"
                elif code.startswith("F") or code.startswith("E7") or code == "C901":
                    severity = "HIGH"
                elif code.startswith("E") or code.startswith("W"):
                    severity = "MEDIUM"

                file_loc = item.get("filename", "")
                try:
                    rel_file = Path(file_loc).relative_to(repo_path).as_posix()
                except Exception:
                    rel_file = file_loc

                loc = item.get("location", {})
                end_loc = item.get("end_location", {})

                parsed_issues.append(
                    LintIssue(
                        code=code,
                        message=item.get("message", ""),
                        file_path=rel_file,
                        line=loc.get("row", 1),
                        column=loc.get("column", 1),
                        end_line=end_loc.get("row"),
                        end_column=end_loc.get("column"),
                        severity=severity,
                        fix_available=bool(item.get("fix")),
                    )
                )

            high_severity = [i for i in parsed_issues if i.severity in ["CRITICAL", "HIGH"]]

            return RuffAnalysisResult(
                total_issues=len(parsed_issues),
                issues_by_category=category_counts,
                high_severity_issues=high_severity,
                all_issues=parsed_issues,
                complexity_hotspots=ast_hotspots,
                execution_success=True,
            )

        except subprocess.TimeoutExpired:
            return RuffAnalysisResult(
                total_issues=0,
                issues_by_category={},
                high_severity_issues=[],
                all_issues=[],
                complexity_hotspots=ast_hotspots,
                execution_success=False,
                error_message=f"Ruff analysis timed out after {timeout_seconds}s",
            )
        except Exception as e:
            return RuffAnalysisResult(
                total_issues=0,
                issues_by_category={},
                high_severity_issues=[],
                all_issues=[],
                complexity_hotspots=ast_hotspots,
                execution_success=False,
                error_message=str(e),
            )
