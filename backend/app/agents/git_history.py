from pathlib import Path
from typing import List, Optional

from app.agents.base import BaseAgent
from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType
from app.tools.git_tool import GitTool


class GitHistoryAgent(BaseAgent):
    """Agent 5: Evaluates repository velocity, churn hotspots, bugfix clustering, and Bus Factor."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(
            name="GitHistoryAgent",
            category=RiskCategory.GIT,
            llm_provider=llm_provider,
        )

    async def run(self, repo_path: Path) -> List[FindingCreate]:
        repo_path = Path(repo_path)
        findings: List[FindingCreate] = []

        git_res = GitTool.analyze_repository(repo_path)
        if git_res.total_commits == 0:
            return findings

        # 1. High Churn Hotspot
        for stat in git_res.top_churn_files[:3]:
            churn_ratio = stat.commit_count / max(1, git_res.total_commits)
            if stat.commit_count >= 5 and churn_ratio >= 0.25:
                findings.append(
                    FindingCreate(
                        finding=f"High-Churn Instability Hotspot: `{stat.file_path}`",
                        category=RiskCategory.GIT,
                        severity=RiskSeverity.HIGH,
                        confidence=0.95,
                        verification_status=VerificationStatus.VERIFIED,
                        verification_notes=f"Modified in {stat.commit_count} of {git_res.total_commits} analyzed commits ({churn_ratio:.1%}).",
                        evidence=[
                            EvidenceCreate(
                                type=EvidenceType.GIT,
                                file=stat.file_path,
                                description=f"File changed across {stat.commit_count} commits with {stat.insertions} insertions and {stat.deletions} deletions.",
                            )
                        ],
                    )
                )

        # 2. Bug-fix Clustering Hotspot
        for stat in git_res.top_churn_files:
            if stat.bugfix_count >= 3:
                findings.append(
                    FindingCreate(
                        finding=f"High Defect Density Hotspot: `{stat.file_path}` ({stat.bugfix_count} bug fixes)",
                        category=RiskCategory.GIT,
                        severity=RiskSeverity.HIGH,
                        confidence=0.92,
                        verification_status=VerificationStatus.VERIFIED,
                        verification_notes=f"Associated with {stat.bugfix_count} separate bugfix/patch commits.",
                        evidence=[
                            EvidenceCreate(
                                type=EvidenceType.GIT,
                                file=stat.file_path,
                                description=f"File was modified in {stat.bugfix_count} bugfix commits, signaling recurring logic bugs or brittle code.",
                            )
                        ],
                    )
                )

        # 3. High Revert / Rollback Frequency
        if git_res.reverted_commits >= 2:
            revert_ratio = git_res.reverted_commits / git_res.total_commits
            findings.append(
                FindingCreate(
                    finding=f"Elevated Commit Reversion Rate ({git_res.reverted_commits} rollbacks)",
                    category=RiskCategory.GIT,
                    severity=RiskSeverity.MEDIUM,
                    confidence=0.90,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"{git_res.reverted_commits} revert commits detected in recent history.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.GIT,
                            file=".git",
                            description=f"Multiple reverted commits ({git_res.reverted_commits}) indicate inadequate pre-merge validation or CI testing.",
                        )
                    ],
                )
            )

        # 4. Bus Factor Risks (Ownership Concentration)
        for risk in git_res.bus_factor_risks[:3]:
            findings.append(
                FindingCreate(
                    finding=f"High Ownership Concentration (Bus Factor Risk) in `{risk['file']}`",
                    category=RiskCategory.GIT,
                    severity=RiskSeverity.MEDIUM,
                    confidence=0.88,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_notes=f"Author `{risk['dominant_author']}` contributed {risk['author_commit_ratio']:.0%} of all commits to this file.",
                    evidence=[
                        EvidenceCreate(
                            type=EvidenceType.GIT,
                            file=risk["file"],
                            description=f"{risk['dominant_author']} authored {risk['author_commit_ratio']:.0%} of changes across {risk['total_commits']} commits.",
                        )
                    ],
                )
            )

        return findings
