import re
from pathlib import Path
from typing import List, Optional

from app.agents.base import BaseAgent
from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType
from app.tools.ruff_tool import RuffTool


class CodeRiskAgent(BaseAgent):
    """Agent 2: Detects code complexity hotspots, dangerous patterns, and maintenance debt."""

    DANGEROUS_PATTERNS = [
        (re.compile(r'\beval\s*\('), "Use of eval() introduces severe arbitrary code execution vulnerability.", RiskSeverity.CRITICAL),
        (re.compile(r'\bexec\s*\('), "Use of exec() permits dynamic execution of untrusted strings.", RiskSeverity.CRITICAL),
        (re.compile(r'\bexcept\s*:\s*pass\b|\bexcept\s+Exception\s*:\s*pass\b'), "Swallowed exception (silent failure) conceals runtime bugs.", RiskSeverity.HIGH),
        (re.compile(r'(?:api_key|secret|password|auth_token)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']', re.IGNORECASE), "Potential hardcoded secret or credential discovered.", RiskSeverity.CRITICAL),
    ]

    TODO_PATTERN = re.compile(r'\b(TODO|FIXME|HACK|XXX|BUG)\b', re.IGNORECASE)

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(
            name="CodeRiskAgent",
            category=RiskCategory.CODE,
            llm_provider=llm_provider,
        )

    async def run(self, repo_path: Path) -> List[FindingCreate]:
        repo_path = Path(repo_path)
        findings: List[FindingCreate] = []

        # 1. Run Ruff and AST Cyclomatic Complexity
        ruff_result = RuffTool.run_ruff(repo_path)

        # Process complexity hotspots
        for hotspot in ruff_result.complexity_hotspots:
            complexity = hotspot["complexity"]
            severity = RiskSeverity.CRITICAL if complexity >= 20 else RiskSeverity.HIGH
            
            # Read snippet if file exists
            file_p = repo_path / hotspot["file"]
            snippet = None
            if file_p.exists():
                try:
                    lines = file_p.read_text(encoding="utf-8", errors="ignore").splitlines()
                    start = max(0, hotspot["line"] - 1)
                    snippet = "\n".join(lines[start:start + 12])
                except Exception:
                    pass

            findings.append(
                FindingCreate(
                    finding=f"High Cyclomatic Complexity in `{hotspot['function']}` (Score: {complexity})",
                    category=RiskCategory.CODE,
                    severity=severity,
                    confidence=0.98,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"AST verification confirmed McCabe complexity of {complexity} (threshold: 10).",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.CODE,
                            file=hotspot["file"],
                            line_start=hotspot["line"],
                            line_end=hotspot["line"] + 10,
                            description=f"Function `{hotspot['function']}` has {complexity} independent execution paths, making it highly defect-prone and hard to test.",
                            snippet=snippet,
                        )
                    ],
                )
            )

        # Process high-severity Ruff lint issues
        for issue in ruff_result.high_severity_issues[:10]:
            findings.append(
                FindingCreate(
                    finding=f"Static Code Violation [{issue.code}]: {issue.message}",
                    category=RiskCategory.CODE,
                    severity=RiskSeverity(issue.severity),
                    confidence=0.95,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"Confirmed by static analysis rule {issue.code}.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.CODE,
                            file=issue.file_path,
                            line_start=issue.line,
                            line_end=issue.end_line or issue.line,
                            description=f"{issue.message} (Rule: {issue.code})",
                        )
                    ],
                )
            )

        # 2. Pattern Matching for Dangerous Constructs & TODO clusters
        for file_p in repo_path.glob("**/*"):
            if not file_p.is_file() or any(part.startswith(".") or part in ["node_modules", ".venv", "venv", "__pycache__", "dist", "build"] for part in file_p.parts):
                continue

            # Only check source files
            if file_p.suffix.lower() not in [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java", ".c", ".cpp"]:
                continue

            try:
                content = file_p.read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()
                rel_file = file_p.relative_to(repo_path).as_posix()

                # Check dangerous patterns
                for pattern, desc, severity in self.DANGEROUS_PATTERNS:
                    for idx, line in enumerate(lines, 1):
                        if pattern.search(line):
                            snippet_text = line.strip()
                            findings.append(
                                FindingCreate(
                                    finding=f"Dangerous Code Pattern in `{rel_file}`",
                                    category=RiskCategory.CODE,
                                    severity=severity,
                                    confidence=0.95,
                                    verification_status=VerificationStatus.VERIFIED,
                                    verification_notes=f"Pattern matched on line {idx}.",
                                    evidence=[
                                        EvidenceCreate(
                                            type=EvidenceType.CODE,
                                            file=rel_file,
                                            line_start=idx,
                                            line_end=idx,
                                            description=desc,
                                            snippet=snippet_text,
                                        )
                                    ],
                                )
                            )

                # Check dense TODOs
                todo_lines = [i for i, line in enumerate(lines, 1) if self.TODO_PATTERN.search(line)]
                if len(todo_lines) >= 5:
                    findings.append(
                        FindingCreate(
                            finding=f"Dense Technical Debt: {len(todo_lines)} Unresolved TODO/FIXME markers in `{rel_file}`",
                            category=RiskCategory.CODE,
                            severity=RiskSeverity.MEDIUM,
                            confidence=0.90,
                            verification_status=VerificationStatus.VERIFIED,
                            verification_notes=f"Identified {len(todo_lines)} debt markers across the file.",
                            evidence=[
                                EvidenceCreate(
                                    type=EvidenceType.CODE,
                                    file=rel_file,
                                    line_start=todo_lines[0],
                                    line_end=todo_lines[-1],
                                    description=f"File contains {len(todo_lines)} TODO/FIXME items indicating incomplete implementations or deferred fixes.",
                                )
                            ],
                        )
                    )

            except Exception:
                continue

        return findings
