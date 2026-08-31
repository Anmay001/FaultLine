import re
from pathlib import Path
from typing import List, Optional, Set

from app.agents.base import BaseAgent
from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType


class TestHealthAgent(BaseAgent):
    """Agent 3: Analyzes test suite completeness, untested critical modules, and hollow test cases."""

    __test__ = False  # Prevent pytest from treating this as a Test class

    TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs"}
    TEST_FILE_PATTERNS = [
        re.compile(r'^test_.*\.py$'),
        re.compile(r'.*_test\.py$'),
        re.compile(r'.*\.test\.(js|ts|jsx|tsx)$'),
        re.compile(r'.*\.spec\.(js|ts|jsx|tsx)$'),
    ]

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(
            name="TestHealthAgent",
            category=RiskCategory.TEST,
            llm_provider=llm_provider,
        )

    def _is_test_file(self, path: Path) -> bool:
        name = path.name.lower()
        if any(p.match(name) for p in self.TEST_FILE_PATTERNS):
            return True
        if any(part.lower() in self.TEST_DIR_NAMES for part in path.parts):
            return True
        return False

    async def run(self, repo_path: Path) -> List[FindingCreate]:
        repo_path = Path(repo_path)
        findings: List[FindingCreate] = []

        code_files: List[Path] = []
        test_files: List[Path] = []

        for p in repo_path.glob("**/*"):
            if not p.is_file() or any(part.startswith(".") or part in ["node_modules", ".venv", "venv", "__pycache__", "dist", "build"] for part in p.parts):
                continue

            if p.suffix.lower() in [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java"]:
                if self._is_test_file(p):
                    test_files.append(p)
                else:
                    code_files.append(p)

        # 1. Total Absence of Tests
        if not test_files and code_files:
            findings.append(
                FindingCreate(
                    finding="Complete Absence of Automated Tests",
                    category=RiskCategory.TEST,
                    severity=RiskSeverity.CRITICAL,
                    confidence=1.0,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"Scanned {len(code_files)} code files and found 0 test files.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.TEST,
                            file=".",
                            description=f"Project contains {len(code_files)} source files but no test suites or test directories were located.",
                        )
                    ],
                )
            )
            return findings

        # 2. Test-to-Code Ratio Check
        if code_files and test_files:
            ratio = len(test_files) / len(code_files)
            if ratio < 0.2:
                findings.append(
                    FindingCreate(
                        finding=f"Severe Test Deficit: Test-to-Code Ratio is {ratio:.1%}",
                        category=RiskCategory.TEST,
                        severity=RiskSeverity.HIGH,
                        confidence=0.95,
                        verification_status=VerificationStatus.VERIFIED,
                        verification_notes=f"Found {len(test_files)} test files for {len(code_files)} source files.",
                        evidence=[
                            EvidenceCreate(
                                type=EvidenceType.TEST,
                                file="tests",
                                description=f"Test coverage surface is critically low ({len(test_files)} tests vs {len(code_files)} source modules).",
                            )
                        ],
                    )
                )

        # 3. Detect Untested Core Modules
        test_basenames = {t.stem.replace("test_", "").replace("_test", "").replace(".test", "").replace(".spec", "").lower() for t in test_files}
        untested_critical: List[Path] = []

        for cf in code_files:
            stem = cf.stem.lower()
            # Flag modules with words like auth, payment, security, service, engine, model, core
            if any(term in stem for term in ["auth", "pay", "sec", "serv", "core", "order", "api"]):
                if stem not in test_basenames:
                    untested_critical.append(cf)

        for uc in untested_critical[:5]:
            rel_path = uc.relative_to(repo_path).as_posix()
            findings.append(
                FindingCreate(
                    finding=f"Untested Critical Business Module: `{rel_path}`",
                    category=RiskCategory.TEST,
                    severity=RiskSeverity.HIGH,
                    confidence=0.90,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"No matching test file found corresponding to `{uc.name}`.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.TEST,
                            file=rel_path,
                            description=f"High-impact module `{rel_path}` has no matching unit test fixture in test suite.",
                        )
                    ],
                )
            )

        # 4. Hollow Test Files (e.g. Empty or contain only pass / no assertions)
        for tf in test_files:
            try:
                content = tf.read_text(encoding="utf-8", errors="ignore")
                rel_path = tf.relative_to(repo_path).as_posix()
                if len(content.strip()) < 40 or ("def test_" in content and "assert" not in content and "expect(" not in content):
                    findings.append(
                        FindingCreate(
                            finding=f"Hollow Test Fixture with Zero Assertions: `{rel_path}`",
                            category=RiskCategory.TEST,
                            severity=RiskSeverity.MEDIUM,
                            confidence=0.88,
                            verification_status=VerificationStatus.VERIFIED,
                            verification_notes="File contains test function signatures but zero verifiable assertion statements.",
                            evidence=[
                                EvidenceCreate(
                                    type=EvidenceType.TEST,
                                    file=rel_path,
                                    description="Test file contains hollow stubs or lacks assertions, producing deceptive pass rates.",
                                    snippet=content[:200],
                                )
                            ],
                        )
                    )
            except Exception:
                continue

        return findings
