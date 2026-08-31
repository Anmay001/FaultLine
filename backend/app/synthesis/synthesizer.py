from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.api.schemas import FindingCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus


class RiskReport(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0, description="Overall project health score (0 - 100)")
    code_risk_score: float = Field(ge=0.0, le=100.0)
    test_risk_score: float = Field(ge=0.0, le=100.0)
    git_risk_score: float = Field(ge=0.0, le=100.0)
    dependency_risk_score: float = Field(ge=0.0, le=100.0)
    architecture_risk_score: float = Field(ge=0.0, le=100.0)
    documentation_risk_score: float = Field(ge=0.0, le=100.0)
    summary: str = Field(description="Executive summary of key failure risks and recommended actions")
    top_verified_risks: List[FindingCreate] = Field(default_factory=list)
    total_findings: int = 0
    verified_findings_count: int = 0
    not_verified_findings_count: int = 0


class RiskSynthesizer:
    """
    Agent 10: Calculates deterministic risk scores based on strict mathematical weighting
    and synthesizes verified findings into executive reports.
    """

    SEVERITY_PENALTIES = {
        RiskSeverity.CRITICAL: 25.0,
        RiskSeverity.HIGH: 15.0,
        RiskSeverity.MEDIUM: 8.0,
        RiskSeverity.LOW: 3.0,
    }

    STATUS_WEIGHTS = {
        VerificationStatus.VERIFIED: 1.0,
        VerificationStatus.INSUFFICIENT_EVIDENCE: 0.6,
        VerificationStatus.NOT_VERIFIED: 0.0,  # Unverified claims do not penalize scores
    }

    # Weight distribution matching Master Specification
    WEIGHTS = {
        RiskCategory.CODE: 0.25,
        RiskCategory.TEST: 0.20,
        RiskCategory.GIT: 0.20,
        RiskCategory.DEPENDENCY: 0.15,
        RiskCategory.ARCHITECTURE: 0.10,
        RiskCategory.DOCUMENTATION: 0.10,
    }

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider

    @classmethod
    def calculate_category_scores(cls, findings: List[FindingCreate]) -> Dict[RiskCategory, float]:
        """
        Calculates deterministic scores (0 to 100) for each individual risk category.
        """
        penalties: Dict[RiskCategory, float] = {
            RiskCategory.CODE: 0.0,
            RiskCategory.TEST: 0.0,
            RiskCategory.GIT: 0.0,
            RiskCategory.DEPENDENCY: 0.0,
            RiskCategory.ARCHITECTURE: 0.0,
            RiskCategory.DOCUMENTATION: 0.0,
        }

        for finding in findings:
            base_penalty = cls.SEVERITY_PENALTIES.get(finding.severity, 5.0)
            status_mult = cls.STATUS_WEIGHTS.get(finding.verification_status, 0.5)
            effective_penalty = base_penalty * status_mult * finding.confidence

            if finding.category == RiskCategory.COMPOUNDED:
                # Distribute compounded penalty across code, test, and git
                penalties[RiskCategory.CODE] += effective_penalty * 0.4
                penalties[RiskCategory.TEST] += effective_penalty * 0.3
                penalties[RiskCategory.GIT] += effective_penalty * 0.3
            elif finding.category in penalties:
                penalties[finding.category] += effective_penalty

        # Compute category scores: 100 - penalties (clamped between 0 and 100)
        scores: Dict[RiskCategory, float] = {}
        for cat, penalty in penalties.items():
            scores[cat] = round(max(0.0, min(100.0, 100.0 - penalty)), 1)

        return scores

    @classmethod
    def calculate_overall_score(cls, category_scores: Dict[RiskCategory, float]) -> float:
        """
        Computes the weighted aggregate health score out of 100.
        """
        overall = sum(
            category_scores.get(cat, 100.0) * weight
            for cat, weight in cls.WEIGHTS.items()
        )
        return round(max(0.0, min(100.0, overall)), 1)

    async def synthesize(
        self,
        findings: List[FindingCreate],
        project_name: str = "Target Repository",
    ) -> RiskReport:
        """
        Synthesizes verified findings, calculates deterministic scores, and creates the final risk report.
        """
        cat_scores = self.calculate_category_scores(findings)
        overall = self.calculate_overall_score(cat_scores)

        # Sort top verified findings by severity
        severity_order = {
            RiskSeverity.CRITICAL: 0,
            RiskSeverity.HIGH: 1,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.LOW: 3,
        }

        verified_findings = [f for f in findings if f.verification_status == VerificationStatus.VERIFIED]
        top_risks = sorted(
            verified_findings,
            key=lambda x: (severity_order.get(x.severity, 4), -x.confidence)
        )[:8]

        verified_count = len(verified_findings)
        not_verified_count = sum(1 for f in findings if f.verification_status == VerificationStatus.NOT_VERIFIED)

        # Generate summary
        critical_count = sum(1 for f in verified_findings if f.severity == RiskSeverity.CRITICAL)
        high_count = sum(1 for f in verified_findings if f.severity == RiskSeverity.HIGH)

        if overall >= 85:
            health_label = "HEALTHY"
        elif overall >= 65:
            health_label = "MODERATE RISK"
        elif overall >= 45:
            health_label = "ELEVATED RISK"
        else:
            health_label = "CRITICAL RISK"

        summary = (
            f"Repository assessment concluded with an overall health score of {overall}/100 ({health_label}). "
            f"Identified {len(findings)} total findings ({verified_count} ground-truth verified, {not_verified_count} refuted). "
            f"Key risk areas include {critical_count} critical and {high_count} high severity issues across "
            f"Code ({cat_scores[RiskCategory.CODE]}%), Test ({cat_scores[RiskCategory.TEST]}%), "
            f"Git ({cat_scores[RiskCategory.GIT]}%), and Dependencies ({cat_scores[RiskCategory.DEPENDENCY]}%)."
        )

        return RiskReport(
            overall_score=overall,
            code_risk_score=cat_scores[RiskCategory.CODE],
            test_risk_score=cat_scores[RiskCategory.TEST],
            git_risk_score=cat_scores[RiskCategory.GIT],
            dependency_risk_score=cat_scores[RiskCategory.DEPENDENCY],
            architecture_risk_score=cat_scores[RiskCategory.ARCHITECTURE],
            documentation_risk_score=cat_scores[RiskCategory.DOCUMENTATION],
            summary=summary,
            top_verified_risks=top_risks,
            total_findings=len(findings),
            verified_findings_count=verified_count,
            not_verified_findings_count=not_verified_count,
        )
