import pytest
from app.api.schemas import FindingCreate, EvidenceCreate
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.synthesis.synthesizer import RiskSynthesizer


@pytest.mark.asyncio
async def test_deterministic_scoring_weights():
    # Construct verified findings in different categories
    findings = [
        # Critical code risk: 25 pt penalty * 1.0 * 1.0 = 25 pts -> Code score = 75.0
        FindingCreate(
            finding="Critical Code Vulnerability",
            category=RiskCategory.CODE,
            severity=RiskSeverity.CRITICAL,
            confidence=1.0,
            verification_status=VerificationStatus.VERIFIED,
            evidence=[EvidenceCreate(type="code", file="main.py", description="eval() used")]
        ),
        # High test risk: 15 pt penalty * 1.0 * 1.0 = 15 pts -> Test score = 85.0
        FindingCreate(
            finding="Missing Test Coverage",
            category=RiskCategory.TEST,
            severity=RiskSeverity.HIGH,
            confidence=1.0,
            verification_status=VerificationStatus.VERIFIED,
            evidence=[EvidenceCreate(type="test", file="tests", description="0 tests")]
        ),
        # High git risk: 15 pt penalty * 1.0 * 1.0 = 15 pts -> Git score = 85.0
        FindingCreate(
            finding="High Churn Hotspot",
            category=RiskCategory.GIT,
            severity=RiskSeverity.HIGH,
            confidence=1.0,
            verification_status=VerificationStatus.VERIFIED,
            evidence=[EvidenceCreate(type="git", file="main.py", description="30 commits")]
        ),
        # Refuted finding: NOT_VERIFIED should have 0.0 multiplier and NOT penalize scores!
        FindingCreate(
            finding="Hallucinated Dep Issue",
            category=RiskCategory.DEPENDENCY,
            severity=RiskSeverity.CRITICAL,
            confidence=1.0,
            verification_status=VerificationStatus.NOT_VERIFIED,
            evidence=[EvidenceCreate(type="dependency", file="ghost.json", description="fake")]
        ),
    ]

    synthesizer = RiskSynthesizer()
    report = await synthesizer.synthesize(findings)

    # Verify category scores
    assert report.code_risk_score == 75.0
    assert report.test_risk_score == 85.0
    assert report.git_risk_score == 85.0
    assert report.dependency_risk_score == 100.0  # NOT_VERIFIED finding had 0 impact
    assert report.architecture_risk_score == 100.0
    assert report.documentation_risk_score == 100.0

    # Verify overall score calculation:
    # 0.25 * 75 + 0.20 * 85 + 0.20 * 85 + 0.15 * 100 + 0.10 * 100 + 0.10 * 100
    # = 18.75 + 17.0 + 17.0 + 15.0 + 10.0 + 10.0 = 87.75 -> rounded to 87.8
    expected_overall = round(0.25*75.0 + 0.20*85.0 + 0.20*85.0 + 0.15*100.0 + 0.10*100.0 + 0.10*100.0, 1)
    assert report.overall_score == expected_overall
    assert report.verified_findings_count == 3
    assert report.not_verified_findings_count == 1
