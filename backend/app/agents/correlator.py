from collections import defaultdict
from typing import Dict, List, Set
from pydantic import BaseModel

from app.api.schemas import FindingCreate, EvidenceCreate
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType


class RiskCorrelator:
    """
    Combines multi-modal risk signals across agents.
    If a file or component has compound risks (e.g. high code complexity + low test coverage + high git churn),
    it generates a compounded Critical/High Risk Hotspot.
    """

    @classmethod
    def correlate(cls, findings: List[FindingCreate]) -> List[FindingCreate]:
        """
        Groups findings by target file and generates compounded risk findings for multi-signal hotspots.
        """
        # Map findings by target file
        file_findings_map: Dict[str, List[FindingCreate]] = defaultdict(list)
        file_categories_map: Dict[str, Set[RiskCategory]] = defaultdict(set)

        # Skip top-level build manifests from single-file hotspot grouping
        # (they frequently get modified across all PRs and would otherwise become false-positive hotspots)
        IGNORED_HOTSPOT_FILES = {".", ".git", "package.json", "requirements.txt", "readme.md", "pyproject.toml", "cargo.toml"}

        for finding in findings:
            for ev in finding.evidence:
                file_key = ev.file.strip().lower()
                if file_key and file_key not in IGNORED_HOTSPOT_FILES:
                    file_findings_map[ev.file].append(finding)
                    file_categories_map[ev.file].add(finding.category)

        compounded_findings: List[FindingCreate] = []

        # Find files with signals from at least 2 distinct risk categories
        for file_path, categories in file_categories_map.items():
            if len(categories) >= 2:
                correlated_list = file_findings_map[file_path]
                # Unique distinct finding titles
                signal_titles = list({f.finding for f in correlated_list})
                cat_names = ", ".join([c.value if hasattr(c, "value") else str(c) for c in categories])

                # Determine compounded severity
                severities = [f.severity for f in correlated_list]
                is_critical = (
                    RiskSeverity.CRITICAL in severities or
                    len(categories) >= 3 or
                    (RiskSeverity.HIGH in severities and len(categories) >= 2)
                )
                compounded_sev = RiskSeverity.CRITICAL if is_critical else RiskSeverity.HIGH

                # Aggregate all evidence items
                all_evidence: List[EvidenceCreate] = []
                for f in correlated_list:
                    for ev in f.evidence:
                        all_evidence.append(ev)

                evidence_summary = " + ".join(signal_titles[:3])
                compounded_findings.append(
                    FindingCreate(
                        finding=f"Compounded Failure Hotspot in `{file_path}` ({cat_names})",
                        category=RiskCategory.COMPOUNDED,
                        severity=compounded_sev,
                        confidence=0.98,
                        verification_status=VerificationStatus.VERIFIED,
                        verification_notes=f"Compounded risk: {len(categories)} distinct signal categories ({cat_names}) intersect in this file.",
                        evidence=all_evidence[:6],
                    )
                )

        # Return original findings + new compounded findings (compounded at top)
        return compounded_findings + findings
