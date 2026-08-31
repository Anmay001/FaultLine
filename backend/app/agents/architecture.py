import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.agents.base import BaseAgent
from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType


class ArchitectureAgent(BaseAgent):
    """Agent 7: Builds import graph to detect circular dependencies, God modules, and high coupling."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(
            name="ArchitectureAgent",
            category=RiskCategory.ARCHITECTURE,
            llm_provider=llm_provider,
        )

    def _extract_python_imports(self, file_path: Path, repo_root: Path) -> Tuple[List[str], int]:
        """Extracts imported module names and total import count from Python file."""
        imports = []
        import_count = 0
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8", errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    import_count += len(node.names)
                    for n in node.names:
                        imports.append(n.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    import_count += 1
                    if node.module:
                        imports.append(node.module.split(".")[0])
        except Exception:
            pass
        return imports, import_count

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Tarjan / DFS cycle detection in module dependency graph."""
        visited = set()
        stack = []
        stack_set = set()
        cycles = []

        def dfs(node: str):
            visited.add(node)
            stack.append(node)
            stack_set.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in stack_set:
                    # Cycle detected
                    idx = stack.index(neighbor)
                    cycles.append(stack[idx:] + [neighbor])

            stack.pop()
            stack_set.remove(node)

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node)

        return cycles

    async def run(self, repo_path: Path) -> List[FindingCreate]:
        repo_path = Path(repo_path)
        findings: List[FindingCreate] = []

        import_graph: Dict[str, Set[str]] = defaultdict(set)
        in_degree: Dict[str, int] = defaultdict(int)
        module_import_counts: Dict[str, int] = {}
        dir_file_counts: Dict[str, int] = defaultdict(int)

        py_files = [
            f for f in repo_path.glob("**/*.py")
            if not any(part.startswith(".") or part in ["node_modules", ".venv", "venv", "__pycache__"] for part in f.parts)
        ]

        # 1. Monolithic Flat Structure Check
        for f in py_files:
            rel_dir = f.parent.relative_to(repo_path).as_posix()
            dir_file_counts[rel_dir] += 1

        for d_path, count in dir_file_counts.items():
            if count >= 25 and d_path == ".":
                findings.append(
                    FindingCreate(
                        finding=f"Flat Monolithic Architecture ({count} root source files)",
                        category=RiskCategory.ARCHITECTURE,
                        severity=RiskSeverity.HIGH,
                        confidence=0.95,
                        verification_status=VerificationStatus.VERIFIED,
                        verification_notes="Repository lacks modular subdirectory organization.",
                        evidence=[
                            EvidenceCreate(
                                type=EvidenceType.ARCHITECTURE,
                                file=".",
                                description=f"Root directory contains {count} source files without domain or layer packaging.",
                            )
                        ],
                    )
                )

        # 2. Build Dependency Graph
        internal_modules = {f.stem for f in py_files}
        
        for f in py_files:
            rel_path = f.relative_to(repo_path).as_posix()
            mod_name = f.stem
            imported_mods, total_imports = self._extract_python_imports(f, repo_path)
            module_import_counts[rel_path] = total_imports

            # High coupling check
            if total_imports >= 20:
                findings.append(
                    FindingCreate(
                        finding=f"High Coupling: `{rel_path}` imports {total_imports} modules",
                        category=RiskCategory.ARCHITECTURE,
                        severity=RiskSeverity.MEDIUM,
                        confidence=0.92,
                        verification_status=VerificationStatus.VERIFIED,
                        verification_notes=f"File contains {total_imports} import declarations exceeding recommended coupling limit (15).",
                        evidence=[
                            EvidenceCreate(
                                type=EvidenceType.ARCHITECTURE,
                                file=rel_path,
                                description=f"Excessive dependencies ({total_imports} imports) increase fragility and testing complexity.",
                            )
                        ],
                    )
                )

            # Map internal dependencies
            for imp in imported_mods:
                if imp in internal_modules and imp != mod_name:
                    import_graph[mod_name].add(imp)
                    in_degree[imp] += 1

        # 3. Detect Circular Dependencies
        cycles = self._find_cycles(import_graph)
        for cycle in cycles[:3]:
            cycle_str = " -> ".join(cycle)
            findings.append(
                FindingCreate(
                    finding=f"Circular Architecture Dependency: `{cycle_str}`",
                    category=RiskCategory.ARCHITECTURE,
                    severity=RiskSeverity.HIGH,
                    confidence=0.95,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"Cyclic import dependency path verified: {cycle_str}.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.ARCHITECTURE,
                            file=f"{cycle[0]}.py",
                            description=f"Direct or transitive cyclic import loop: {cycle_str}",
                        )
                    ],
                )
            )

        # 4. God Module / Central Bottleneck
        total_internal = len(internal_modules)
        if total_internal >= 6:
            for mod, fan_in in in_degree.items():
                if fan_in >= max(4, int(total_internal * 0.6)):
                    findings.append(
                        FindingCreate(
                            finding=f"Architectural Bottleneck (God Module): `{mod}`",
                            category=RiskCategory.ARCHITECTURE,
                            severity=RiskSeverity.HIGH,
                            confidence=0.90,
                            verification_status=VerificationStatus.VERIFIED,
                            verification_notes=f"Imported directly by {fan_in} of {total_internal} internal modules.",
                            evidence=[
                                EvidenceCreate(
                                    type=EvidenceType.ARCHITECTURE,
                                    file=f"{mod}.py",
                                    description=f"Module `{mod}` is a central bottleneck with fan-in degree of {fan_in}, causing ripple effects across changes.",
                                )
                            ],
                        )
                    )

        return findings
