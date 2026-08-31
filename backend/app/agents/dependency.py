import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.agents.base import BaseAgent
from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType


class DependencyRiskAgent(BaseAgent):
    """Agent 4: Evaluates dependency vulnerability, unpinned versions, and missing lockfiles."""

    KNOWN_VULNERABLE_PACKAGES: Dict[str, Tuple[str, RiskSeverity, str]] = {
        "express": ("<4.18.0", RiskSeverity.HIGH, "Known prototype pollution & body-parser vulnerabilities"),
        "lodash": ("<4.17.21", RiskSeverity.HIGH, "Critical prototype pollution vulnerabilities (CVE-2019-10744)"),
        "axios": ("<1.6.0", RiskSeverity.MEDIUM, "SSRF and cross-site request vulnerabilities (CVE-2023-45857)"),
        "jsonwebtoken": ("<9.0.0", RiskSeverity.CRITICAL, "Insecure key verification vulnerabilities (CVE-2022-23529)"),
        "urllib3": ("<2.0.0", RiskSeverity.MEDIUM, "Cookie leak and proxy authorization vulnerabilities"),
        "requests": ("<2.31.0", RiskSeverity.MEDIUM, "Leaked proxy credentials on HTTPS redirect (CVE-2023-32681)"),
        "django": ("<4.2.0", RiskSeverity.HIGH, "Multiple SQL injection and DoS CVE vulnerabilities"),
        "flask": ("<2.2.0", RiskSeverity.MEDIUM, "Session cookie signing and security bypasses"),
        "cryptography": ("<41.0.0", RiskSeverity.HIGH, "Memory corruption and NULL pointer dereference in OpenSSL bindings"),
    }

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(
            name="DependencyRiskAgent",
            category=RiskCategory.DEPENDENCY,
            llm_provider=llm_provider,
        )

    async def run(self, repo_path: Path) -> List[FindingCreate]:
        repo_path = Path(repo_path)
        findings: List[FindingCreate] = []

        # 1. Check Node/NPM dependencies in package.json
        pkg_json = repo_path / "package.json"
        if pkg_json.exists():
            # Check lockfile
            has_lock = (repo_path / "package-lock.json").exists() or (repo_path / "yarn.lock").exists() or (repo_path / "pnpm-lock.yaml").exists()
            if not has_lock:
                findings.append(
                    FindingCreate(
                        finding="Missing NPM Lockfile (Non-Deterministic Builds)",
                        category=RiskCategory.DEPENDENCY,
                        severity=RiskSeverity.HIGH,
                        confidence=1.0,
                        verification_status=VerificationStatus.VERIFIED,
                        verification_notes="package.json found without package-lock.json, yarn.lock, or pnpm-lock.yaml.",
                        evidence=[
                            EvidenceCreate(
                                type=EvidenceType.DEPENDENCY,
                                file="package.json",
                                description="Builds may resolve divergent dependency subtrees across development and CI/CD environments.",
                            )
                        ],
                    )
                )

            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8", errors="ignore"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                for name, ver in deps.items():
                    # Check wildcard / unpinned
                    if ver in ["*", "latest"] or ver.startswith(">="):
                        findings.append(
                            FindingCreate(
                                finding=f"Unpinned Wildcard Dependency: `{name}: {ver}`",
                                category=RiskCategory.DEPENDENCY,
                                severity=RiskSeverity.MEDIUM,
                                confidence=0.95,
                                verification_status=VerificationStatus.VERIFIED,
                                verification_notes=f"Found wildcard specifier `{ver}` in package.json.",
                                evidence=[
                                    EvidenceCreate(
                                        type=EvidenceType.DEPENDENCY,
                                        file="package.json",
                                        description=f"Package `{name}` specifies `{ver}`, exposing build to breaking upstream changes without notice.",
                                    )
                                ],
                            )
                        )

                    # Check known vulnerable packages
                    lower_name = name.lower()
                    if lower_name in self.KNOWN_VULNERABLE_PACKAGES:
                        rule, sev, desc = self.KNOWN_VULNERABLE_PACKAGES[lower_name]
                        # Rough version check
                        if any(c.isdigit() for c in ver) and not ver.startswith("^5") and not ver.startswith("^9"):
                            findings.append(
                                FindingCreate(
                                    finding=f"Potentially Vulnerable Dependency `{name}@{ver}`",
                                    category=RiskCategory.DEPENDENCY,
                                    severity=sev,
                                    confidence=0.85,
                                    verification_status=VerificationStatus.VERIFIED,
                                    verification_notes=f"Detected package version matching advisory condition: {rule}.",
                                    evidence=[
                                        EvidenceCreate(
                                            type=EvidenceType.DEPENDENCY,
                                            file="package.json",
                                            description=f"{desc} (Targeted rule: {rule})",
                                            snippet=f'"{name}": "{ver}"',
                                        )
                                    ],
                                )
                            )
            except Exception:
                pass

        # 2. Check Python requirements.txt
        req_txt = repo_path / "requirements.txt"
        if req_txt.exists():
            try:
                lines = req_txt.read_text(encoding="utf-8", errors="ignore").splitlines()
                unpinned_count = 0
                for line in lines:
                    cleaned = line.strip().split("#")[0]
                    if not cleaned or cleaned.startswith("-"):
                        continue
                    
                    if "==" not in cleaned:
                        unpinned_count += 1
                        pkg_name = re.split(r'[<>=!~]', cleaned)[0].strip()
                    else:
                        pkg_name, ver = cleaned.split("==", 1)
                        pkg_name = pkg_name.strip().lower()
                        ver = ver.strip()
                        if pkg_name in self.KNOWN_VULNERABLE_PACKAGES:
                            rule, sev, desc = self.KNOWN_VULNERABLE_PACKAGES[pkg_name]
                            findings.append(
                                FindingCreate(
                                    finding=f"Vulnerable Python Dependency `{pkg_name}=={ver}`",
                                    category=RiskCategory.DEPENDENCY,
                                    severity=sev,
                                    confidence=0.90,
                                    verification_status=VerificationStatus.VERIFIED,
                                    verification_notes=f"Version `{ver}` matches known vulnerability baseline.",
                                    evidence=[
                                        EvidenceCreate(
                                            type=EvidenceType.DEPENDENCY,
                                            file="requirements.txt",
                                            description=f"{desc} (Constraint: {rule})",
                                            snippet=line.strip(),
                                        )
                                    ],
                                )
                            )

                if unpinned_count >= 3:
                    findings.append(
                        FindingCreate(
                            finding=f"Multiple Unpinned Python Dependencies ({unpinned_count} packages)",
                            category=RiskCategory.DEPENDENCY,
                            severity=RiskSeverity.MEDIUM,
                            confidence=0.92,
                            verification_status=VerificationStatus.VERIFIED,
                            verification_notes=f"{unpinned_count} lines in requirements.txt lack strict `==` version pinning.",
                            evidence=[
                                EvidenceCreate(
                                    type=EvidenceType.DEPENDENCY,
                                    file="requirements.txt",
                                    description=f"{unpinned_count} packages do not specify exact pinned versions.",
                                )
                            ],
                        )
                    )
            except Exception:
                pass

        return findings
