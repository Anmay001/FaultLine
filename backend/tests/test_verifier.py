import pytest
import tempfile
from pathlib import Path

from app.api.schemas import FindingCreate, EvidenceCreate
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType
from app.agents.verifier import VerificationAgent


def test_verification_agent_valid_evidence():
    with tempfile.TemporaryDirectory() as tmp_dir:
        sandbox = Path(tmp_dir)
        src = sandbox / "src"
        src.mkdir()
        (src / "service.py").write_text("line 1\nline 2\ndef eval_code():\n    return 42\nline 5\n", encoding="utf-8")

        finding = FindingCreate(
            finding="Dangerous Code in service.py",
            category=RiskCategory.CODE,
            severity=RiskSeverity.CRITICAL,
            confidence=0.95,
            evidence=[
                EvidenceCreate(
                    type=EvidenceType.CODE,
                    file="src/service.py",
                    line_start=3,
                    line_end=4,
                    description="eval_code function exists",
                    snippet="def eval_code():",
                )
            ]
        )

        verified = VerificationAgent.verify_finding(sandbox, finding)
        assert verified.verification_status == VerificationStatus.VERIFIED
        assert "Verified" in verified.verification_notes


def test_verification_agent_nonexistent_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        sandbox = Path(tmp_dir)

        finding = FindingCreate(
            finding="Ghost file risk",
            category=RiskCategory.CODE,
            severity=RiskSeverity.HIGH,
            evidence=[
                EvidenceCreate(
                    type=EvidenceType.CODE,
                    file="nonexistent/ghost.py",
                    description="Ghost file",
                )
            ]
        )

        verified = VerificationAgent.verify_finding(sandbox, finding)
        assert verified.verification_status == VerificationStatus.NOT_VERIFIED
        assert "does not exist" in verified.verification_notes


def test_verification_agent_line_out_of_bounds():
    with tempfile.TemporaryDirectory() as tmp_dir:
        sandbox = Path(tmp_dir)
        (sandbox / "short.py").write_text("x = 1\ny = 2\n", encoding="utf-8")

        finding = FindingCreate(
            finding="Out of bounds line",
            category=RiskCategory.CODE,
            severity=RiskSeverity.MEDIUM,
            evidence=[
                EvidenceCreate(
                    type=EvidenceType.CODE,
                    file="short.py",
                    line_start=150,  # File only has 2 lines
                    description="Far out line",
                )
            ]
        )

        verified = VerificationAgent.verify_finding(sandbox, finding)
        assert verified.verification_status == VerificationStatus.NOT_VERIFIED
        assert "out of bounds" in verified.verification_notes
