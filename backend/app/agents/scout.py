from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType
from app.tools.file_tree_tool import FileTreeTool, FileTreeSummary


class ScoutProfile(BaseModel):
    project_name: str
    primary_language: str
    frameworks: List[str] = Field(default_factory=list)
    package_managers: List[str] = Field(default_factory=list)
    test_frameworks: List[str] = Field(default_factory=list)
    project_type: str = Field(description="e.g. monolith, library, web service, CLI tool")
    identified_risks: List[str] = Field(default_factory=list)


class RepositoryScoutAgent(BaseAgent):
    """Agent 1: Discovers project topography, language stack, build tooling, and structural health."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(
            name="RepositoryScoutAgent",
            category=RiskCategory.ARCHITECTURE,
            llm_provider=llm_provider,
        )

    async def run(self, repo_path: Path) -> List[FindingCreate]:
        repo_path = Path(repo_path)
        summary = FileTreeTool.analyze_tree(repo_path)
        findings: List[FindingCreate] = []

        # 1. Deterministic Checks
        # Check: Missing any build/package manifest
        if not summary.manifests:
            findings.append(
                FindingCreate(
                    finding="Missing Standard Package or Build Configuration",
                    category=RiskCategory.ARCHITECTURE,
                    severity=RiskSeverity.HIGH,
                    confidence=1.0,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes="File tree walk revealed no recognised dependency/build manifest.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.ARCHITECTURE,
                            file=".",
                            description="No package.json, pyproject.toml, Cargo.toml, or requirements.txt found in repository root.",
                        )
                    ],
                )
            )

        # Check: Missing CI/CD configuration
        if not summary.has_ci:
            findings.append(
                FindingCreate(
                    finding="Absence of Automated CI/CD Pipeline Configuration",
                    category=RiskCategory.ARCHITECTURE,
                    severity=RiskSeverity.MEDIUM,
                    confidence=0.95,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes="No .github/workflows directory or standard CI configuration file found.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.ARCHITECTURE,
                            file=".github",
                            description="Repository does not define GitHub Actions workflows or automated build gates.",
                        )
                    ],
                )
            )

        # 2. LLM Stack Synthesis (if manifests exist)
        if summary.manifests:
            manifest_samples = "\n\n".join(
                f"File: {m.relative_path}\n```{m.content[:2000]}```"
                for m in summary.manifests[:4]
            )
            prompt = f"""Analyze the repository metadata and manifest files to identify the architecture profile and structural risks:
Languages: {summary.languages}
Total Files: {summary.total_files}
Has Tests: {summary.has_tests}
Has Docker: {summary.has_docker}

Manifests:
{manifest_samples}
"""
            try:
                profile = await self.llm_provider.generate_structured(
                    prompt=prompt,
                    response_model=ScoutProfile,
                    system_instruction="You are a senior software architect creating a structured project profile.",
                )

                for risk_desc in profile.identified_risks:
                    findings.append(
                        FindingCreate(
                            finding=f"Structural Risk: {risk_desc}",
                            category=RiskCategory.ARCHITECTURE,
                            severity=RiskSeverity.MEDIUM,
                            confidence=0.85,
                            verification_status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                            verification_notes="Discovered during repository manifest discovery.",
                            evidence=[
                                EvidenceCreate(
                                    type=EvidenceType.ARCHITECTURE,
                                    file=summary.manifests[0].relative_path if summary.manifests else "root",
                                    description=f"Project profile ({profile.project_type}) identified risk: {risk_desc}",
                                )
                            ],
                        )
                    )
            except Exception:
                pass

        return findings
