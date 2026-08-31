import re
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType


class DocDriftReport(BaseModel):
    has_drift: bool
    drift_items: List[str] = Field(default_factory=list, description="List of inconsistencies between README and actual code")


class DocsConsistencyAgent(BaseAgent):
    """Agent 6: Detects documentation drift, outdated installation instructions, and missing docs."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(
            name="DocsConsistencyAgent",
            category=RiskCategory.DOCUMENTATION,
            llm_provider=llm_provider,
        )

    async def run(self, repo_path: Path) -> List[FindingCreate]:
        repo_path = Path(repo_path)
        findings: List[FindingCreate] = []

        readme_file = None
        for name in ["README.md", "README", "readme.md", "README.rst"]:
            candidate = repo_path / name
            if candidate.exists():
                readme_file = candidate
                break

        # 1. Total Missing Documentation
        if not readme_file:
            findings.append(
                FindingCreate(
                    finding="Missing Repository Documentation (No README.md)",
                    category=RiskCategory.DOCUMENTATION,
                    severity=RiskSeverity.HIGH,
                    confidence=1.0,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes="Repository lacks a README file describing installation, usage, or architecture.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.DOCUMENTATION,
                            file="README.md",
                            description="Project contains no top-level README documentation file.",
                        )
                    ],
                )
            )
            return findings

        # Read README content
        readme_content = readme_file.read_text(encoding="utf-8", errors="ignore")
        rel_readme = readme_file.relative_to(repo_path).as_posix()

        # 2. Stub or Empty README
        if len(readme_content.strip()) < 80:
            findings.append(
                FindingCreate(
                    finding="Stub or Incomplete README Documentation",
                    category=RiskCategory.DOCUMENTATION,
                    severity=RiskSeverity.MEDIUM,
                    confidence=0.95,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"README contains only {len(readme_content.strip())} characters.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.DOCUMENTATION,
                            file=rel_readme,
                            description="README is a minimal placeholder without operational or installation guidelines.",
                            snippet=readme_content[:150],
                        )
                    ],
                )
            )

        # 3. LLM Consistency Evaluation against Project Structure
        top_files = [f.relative_to(repo_path).as_posix() for f in repo_path.glob("*") if not f.name.startswith(".")]
        prompt = f"""Compare the README documentation against the actual files present in the project to identify documentation drift:

Project Root Files:
{top_files}

README Content:
```markdown
{readme_content[:4000]}
```

Does the README contain documented modules, installation commands, or prerequisites that contradict the actual project structure?
"""
        try:
            report = await self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=DocDriftReport,
                system_instruction="You are a technical documentation quality auditor.",
            )

            if report.has_drift:
                for item in report.drift_items:
                    findings.append(
                        FindingCreate(
                            finding=f"Documentation Drift: {item}",
                            category=RiskCategory.DOCUMENTATION,
                            severity=RiskSeverity.MEDIUM,
                            confidence=0.85,
                            verification_status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                            verification_notes="Discrepancy identified between documented usage and actual repository structure.",
                            evidence=[
                                EvidenceCreate(
                                    type=EvidenceType.DOCUMENTATION,
                                    file=rel_readme,
                                    description=item,
                                )
                            ],
                        )
                    )
        except Exception:
            pass

        return findings
