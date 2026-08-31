from pathlib import Path
from typing import List, Tuple

from app.api.schemas import FindingCreate, EvidenceCreate
from app.models.finding import VerificationStatus, RiskSeverity


class VerificationAgent:
    """
    Agent 9: Ground-truth verifier.
    Inspects cited evidence against the actual sandbox filesystem to prove or disprove findings.
    Prevents hallucinated files, invalid line numbers, or unfounded claims.
    """

    @classmethod
    def verify_evidence_item(cls, sandbox_path: Path, ev: EvidenceCreate) -> Tuple[bool, str]:
        """
        Validates a single evidence item against the sandbox filesystem.
        """
        rel_file = ev.file.strip()

        # Handle root or special meta paths
        if rel_file in [".", "root", "", "tests"]:
            return True, "Root repository context validated."
        if rel_file == ".git":
            return (sandbox_path / ".git").exists(), "Git metadata directory validated."

        target_file = (sandbox_path / rel_file.lstrip("/\\")).resolve()
        
        # Security check: ensure target stays inside sandbox
        try:
            target_file.relative_to(sandbox_path.resolve())
        except ValueError:
            return False, f"Evidence path escapes sandbox: {rel_file}"

        if not target_file.exists():
            return False, f"Cited file `{rel_file}` does not exist in repository sandbox."

        if not target_file.is_file():
            return True, f"Directory `{rel_file}` exists in sandbox."

        # Line number validation
        try:
            lines = target_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            total_lines = len(lines)

            if ev.line_start is not None:
                if ev.line_start < 1 or ev.line_start > max(1, total_lines + 5):
                    return False, f"Line number {ev.line_start} is out of bounds (file `{rel_file}` has {total_lines} lines)."

            # Snippet verification
            if ev.snippet and len(ev.snippet.strip()) > 5:
                snippet_token = ev.snippet.strip().splitlines()[0][:40].strip()
                file_content = "\n".join(lines)
                if snippet_token not in file_content and ev.line_start is None:
                    return False, f"Code snippet `{snippet_token}...` not found in `{rel_file}`."

            return True, f"Verified file `{rel_file}` ({total_lines} LOC)"
        except Exception as e:
            return False, f"Error reading cited file `{rel_file}`: {str(e)}"

    @classmethod
    def verify_finding(cls, sandbox_path: Path, finding: FindingCreate) -> FindingCreate:
        """
        Validates all evidence items of a finding and assigns final verification status.
        """
        if not finding.evidence:
            finding.verification_status = VerificationStatus.INSUFFICIENT_EVIDENCE
            finding.verification_notes = "No supporting evidence items provided for verification."
            return finding

        passed_items = 0
        notes_list = []
        has_critical_failure = False

        for ev in finding.evidence:
            is_valid, note = cls.verify_evidence_item(sandbox_path, ev)
            notes_list.append(note)
            if is_valid:
                passed_items += 1
            else:
                has_critical_failure = True

        if has_critical_failure:
            finding.verification_status = VerificationStatus.NOT_VERIFIED
            finding.verification_notes = f"Verification Failed: {'; '.join(notes_list)}"
        elif passed_items == len(finding.evidence):
            finding.verification_status = VerificationStatus.VERIFIED
            finding.verification_notes = f"Verified: {'; '.join(notes_list[:2])}"
        else:
            finding.verification_status = VerificationStatus.INSUFFICIENT_EVIDENCE
            finding.verification_notes = f"Partial Verification: {'; '.join(notes_list)}"

        return finding

    @classmethod
    def verify_all(cls, sandbox_path: Path, findings: List[FindingCreate]) -> List[FindingCreate]:
        """
        Iterates through all findings and verifies evidence against sandbox files.
        """
        sandbox_path = Path(sandbox_path)
        verified_list: List[FindingCreate] = []

        for f in findings:
            verified_finding = cls.verify_finding(sandbox_path, f)
            verified_list.append(verified_finding)

        return verified_list
