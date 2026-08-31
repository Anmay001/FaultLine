import pytest
import tempfile
from pathlib import Path
from git import Repo

from app.llm.mock import MockLLMProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType
from app.agents.scout import RepositoryScoutAgent
from app.agents.code_risk import CodeRiskAgent
from app.agents.test_health import TestHealthAgent
from app.agents.dependency import DependencyRiskAgent
from app.agents.git_history import GitHistoryAgent
from app.agents.docs_consistency import DocsConsistencyAgent
from app.agents.architecture import ArchitectureAgent
from app.agents.orchestrator import AgentOrchestrator


@pytest.fixture
def complex_mock_repo():
    """Creates a rich mock repository containing code complexity, missing tests, vulnerable deps, and git churn."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        repo = Repo.init(str(root))

        # 1. Manifests
        (root / "package.json").write_text(
            '{"name": "test-app", "dependencies": {"express": "4.16.0", "lodash": "*"}}',
            encoding="utf-8"
        )
        (root / "README.md").write_text("# Test App\nInstallation: npm install wrong-pkg\n", encoding="utf-8")

        # 2. Source files
        src = root / "src"
        src.mkdir()
        
        # Payment service with high complexity + dangerous pattern + TODOs
        payment_code = """
import os

def process_payment(amount, user_token, method):
    # TODO: implement audit logging
    # TODO: add currency conversion
    # TODO: fix race condition
    # TODO: encrypt payload
    # TODO: handle timeout
    
    # Dangerous pattern
    auth_token = "abcdef1234567890abcdef"
    
    if method == 1:
        if amount > 100:
            return "high"
        else:
            return "low"
    elif method == 2:
        if amount > 500:
            return "high"
        else:
            return "low"
    elif method == 3:
        if amount > 1000:
            return "high"
        else:
            return "low"
    elif method == 4:
        return "crypto"
    elif method == 5:
        return "wire"
    elif method == 6:
        return "check"
    elif method == 7:
        return "paypal"
    elif method == 8:
        return "stripe"
    elif method == 9:
        return "apple_pay"
    elif method == 10:
        return "google_pay"
    return "unknown"
"""
        (src / "payment.py").write_text(payment_code, encoding="utf-8")

        # Circular dependencies: module_a <-> module_b
        (src / "module_a.py").write_text("import module_b\ndef a(): return module_b.b()\n", encoding="utf-8")
        (src / "module_b.py").write_text("import module_a\ndef b(): return module_a.a()\n", encoding="utf-8")

        # 3. Tests (only 1 test file, missing payment tests)
        tests = root / "tests"
        tests.mkdir()
        (tests / "test_dummy.py").write_text("def test_dummy(): pass\n", encoding="utf-8")

        # Commit files
        repo.index.add([
            "package.json",
            "README.md",
            "src/payment.py",
            "src/module_a.py",
            "src/module_b.py",
            "tests/test_dummy.py",
        ])
        repo.index.commit("Initial setup")

        # Add bugfix commits to payment.py to create churn
        for i in range(3):
            (src / "payment.py").write_text(payment_code + f"\n# bugfix patch {i}\n", encoding="utf-8")
            repo.index.add(["src/payment.py"])
            repo.index.commit(f"fix: critical null pointer patch {i} in payment engine")

        repo.close()
        yield root


@pytest.mark.asyncio
async def test_code_risk_agent(complex_mock_repo: Path):
    agent = CodeRiskAgent(llm_provider=MockLLMProvider())
    findings = await agent.run(complex_mock_repo)

    assert len(findings) >= 2
    # Check complexity finding
    complexity_findings = [f for f in findings if "Complexity" in f.finding]
    assert len(complexity_findings) >= 1
    assert complexity_findings[0].category == RiskCategory.CODE
    assert complexity_findings[0].verification_status == VerificationStatus.VERIFIED

    # Check secret finding
    secret_findings = [f for f in findings if "Dangerous" in f.finding or "secret" in f.finding.lower()]
    assert len(secret_findings) >= 1

    # Check TODO cluster finding
    todo_findings = [f for f in findings if "Technical Debt" in f.finding]
    assert len(todo_findings) >= 1


@pytest.mark.asyncio
async def test_test_health_agent(complex_mock_repo: Path):
    agent = TestHealthAgent(llm_provider=MockLLMProvider())
    findings = await agent.run(complex_mock_repo)

    assert len(findings) >= 1
    # Untested payment module finding
    untested = [f for f in findings if "payment.py" in f.finding or "Untested" in f.finding]
    assert len(untested) >= 1
    assert untested[0].category == RiskCategory.TEST

    # Hollow test finding
    hollow = [f for f in findings if "Hollow" in f.finding]
    assert len(hollow) >= 1


@pytest.mark.asyncio
async def test_dependency_risk_agent(complex_mock_repo: Path):
    agent = DependencyRiskAgent(llm_provider=MockLLMProvider())
    findings = await agent.run(complex_mock_repo)

    assert len(findings) >= 2
    # Missing lockfile
    lockfile_findings = [f for f in findings if "Lockfile" in f.finding]
    assert len(lockfile_findings) >= 1
    assert lockfile_findings[0].severity == RiskSeverity.HIGH

    # Wildcard dependency
    wildcard_findings = [f for f in findings if "lodash" in f.finding or "Wildcard" in f.finding]
    assert len(wildcard_findings) >= 1

    # Vulnerable express
    vulnerable_findings = [f for f in findings if "express" in f.finding.lower() or "Vulnerable" in f.finding]
    assert len(vulnerable_findings) >= 1


@pytest.mark.asyncio
async def test_git_history_agent(complex_mock_repo: Path):
    agent = GitHistoryAgent(llm_provider=MockLLMProvider())
    findings = await agent.run(complex_mock_repo)

    assert len(findings) >= 1
    bugfix_findings = [f for f in findings if "Defect Density" in f.finding or "payment.py" in f.finding]
    assert len(bugfix_findings) >= 1
    assert bugfix_findings[0].category == RiskCategory.GIT


@pytest.mark.asyncio
async def test_architecture_agent(complex_mock_repo: Path):
    agent = ArchitectureAgent(llm_provider=MockLLMProvider())
    findings = await agent.run(complex_mock_repo)

    assert len(findings) >= 1
    circular = [f for f in findings if "Circular" in f.finding]
    assert len(circular) >= 1
    assert "module_a" in circular[0].finding
    assert circular[0].category == RiskCategory.ARCHITECTURE


@pytest.mark.asyncio
async def test_orchestrator_parallel_execution(complex_mock_repo: Path):
    mock_provider = MockLLMProvider()
    orchestrator = AgentOrchestrator(llm_provider=mock_provider)

    result = await orchestrator.run_all(complex_mock_repo)

    assert result.total_findings >= 6
    assert len(result.agent_results) == 7
    assert all(ar.error is None for ar in result.agent_results)
    assert result.total_execution_time_seconds >= 0.0

    # Ensure categories from multiple agents are populated
    assert "CODE" in result.findings_by_category
    assert "TEST" in result.findings_by_category
    assert "DEPENDENCY" in result.findings_by_category
    assert "GIT" in result.findings_by_category
    assert "ARCHITECTURE" in result.findings_by_category
