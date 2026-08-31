import pytest
from app.api.schemas import FindingCreate, EvidenceCreate
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType
from app.agents.correlator import RiskCorrelator


def test_risk_correlator_compounds_multi_signal_file():
    # File "payment.py" has Code risk + Test risk + Git risk
    f_code = FindingCreate(
        finding="High Cyclomatic Complexity in payment.py",
        category=RiskCategory.CODE,
        severity=RiskSeverity.HIGH,
        confidence=0.95,
        verification_status=VerificationStatus.VERIFIED,
        evidence=[
            EvidenceCreate(
                type=EvidenceType.CODE,
                file="src/payment.py",
                line_start=10,
                line_end=50,
                description="Complexity score is 22",
            )
        ]
    )

    f_test = FindingCreate(
        finding="Untested Critical Module: src/payment.py",
        category=RiskCategory.TEST,
        severity=RiskSeverity.HIGH,
        confidence=0.90,
        verification_status=VerificationStatus.VERIFIED,
        evidence=[
            EvidenceCreate(
                type=EvidenceType.TEST,
                file="src/payment.py",
                description="No matching test file",
            )
        ]
    )

    f_git = FindingCreate(
        finding="High Churn Hotspot: src/payment.py",
        category=RiskCategory.GIT,
        severity=RiskSeverity.HIGH,
        confidence=0.95,
        verification_status=VerificationStatus.VERIFIED,
        evidence=[
            EvidenceCreate(
                type=EvidenceType.GIT,
                file="src/payment.py",
                description="Modified in 15 commits",
            )
        ]
    )

    # An unrelated single-signal finding on another file
    f_unrelated = FindingCreate(
        finding="Missing Lockfile",
        category=RiskCategory.DEPENDENCY,
        severity=RiskSeverity.MEDIUM,
        confidence=0.90,
        evidence=[
            EvidenceCreate(
                type=EvidenceType.DEPENDENCY,
                file="package.json",
                description="No lockfile",
            )
        ]
    )

    raw_findings = [f_code, f_test, f_git, f_unrelated]
    correlated = RiskCorrelator.correlate(raw_findings)

    # Check that a compounded finding was created
    compounded = [f for f in correlated if f.category == RiskCategory.COMPOUNDED]
    assert len(compounded) == 1
    assert "src/payment.py" in compounded[0].finding
    assert compounded[0].severity == RiskSeverity.CRITICAL
    assert len(compounded[0].evidence) == 3
    assert len(correlated) == 5  # 1 compounded + 4 originals
