import pytest
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.repository import Repository
from app.models.analysis_run import AnalysisRun, AnalysisStatus
from app.models.finding import Finding, RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import Evidence, EvidenceType


@pytest.mark.asyncio
async def test_create_and_query_repository(test_db_session: AsyncSession):
    repo_id = str(uuid.uuid4())
    repo = Repository(
        id=repo_id,
        url="https://github.com/octocat/Hello-World.git",
        name="Hello-World",
        owner="octocat",
        default_branch="master",
    )
    test_db_session.add(repo)
    await test_db_session.commit()

    stmt = select(Repository).where(Repository.id == repo_id)
    res = await test_db_session.execute(stmt)
    fetched = res.scalars().first()

    assert fetched is not None
    assert fetched.name == "Hello-World"
    assert fetched.owner == "octocat"
    assert fetched.default_branch == "master"


@pytest.mark.asyncio
async def test_create_analysis_run_with_findings_and_evidence(test_db_session: AsyncSession):
    # 1. Create Repository
    repo = Repository(
        id=str(uuid.uuid4()),
        url="https://github.com/facebook/react.git",
        name="react",
        owner="facebook",
    )
    test_db_session.add(repo)
    await test_db_session.commit()

    # 2. Create AnalysisRun
    analysis = AnalysisRun(
        id=str(uuid.uuid4()),
        repository_id=repo.id,
        status=AnalysisStatus.COMPLETED,
        commit_hash="abc1234567890",
        branch="main",
        overall_score=85.5,
        code_risk_score=90.0,
        test_risk_score=75.0,
        git_risk_score=88.0,
        dependency_risk_score=95.0,
        architecture_risk_score=80.0,
        documentation_risk_score=85.0,
        summary="Analysis completed with minor risks identified.",
    )
    test_db_session.add(analysis)
    await test_db_session.commit()

    # 3. Create Finding
    finding = Finding(
        id=str(uuid.uuid4()),
        analysis_run_id=analysis.id,
        finding="High Cyclomatic Complexity in Core Dispatcher",
        category=RiskCategory.CODE,
        severity=RiskSeverity.HIGH,
        confidence=0.92,
        verification_status=VerificationStatus.VERIFIED,
        verification_notes="AST analysis confirmed complexity score of 28.",
    )
    test_db_session.add(finding)
    await test_db_session.commit()

    # 4. Create Evidence
    ev1 = Evidence(
        id=str(uuid.uuid4()),
        finding_id=finding.id,
        type=EvidenceType.CODE,
        file="packages/react-reconciler/src/ReactFiberWorkLoop.js",
        line_start=150,
        line_end=220,
        description="Function performUnitOfWork exceeds cognitive complexity limit.",
        snippet="function performUnitOfWork(unitOfWork: Fiber): void { ... }",
    )
    ev2 = Evidence(
        id=str(uuid.uuid4()),
        finding_id=finding.id,
        type=EvidenceType.TEST,
        file="packages/react-reconciler/src/__tests__/ReactFiberWorkLoop-test.js",
        line_start=1,
        line_end=1,
        description="Branch coverage for condition on line 182 is 0%.",
    )
    test_db_session.add_all([ev1, ev2])
    await test_db_session.commit()

    # 5. Query and verify nested structure
    stmt = (
        select(AnalysisRun)
        .where(AnalysisRun.id == analysis.id)
        .options(selectinload(AnalysisRun.findings).selectinload(Finding.evidence))
    )
    res = await test_db_session.execute(stmt)
    result = res.scalars().first()

    assert result is not None
    assert result.overall_score == 85.5
    assert len(result.findings) == 1
    assert result.findings[0].severity == RiskSeverity.HIGH
    assert result.findings[0].verification_status == VerificationStatus.VERIFIED
    assert len(result.findings[0].evidence) == 2
    assert result.findings[0].evidence[0].file == "packages/react-reconciler/src/ReactFiberWorkLoop.js"


@pytest.mark.asyncio
async def test_cascading_deletion(test_db_session: AsyncSession):
    # Verify that deleting a repository cascade-deletes analysis runs, findings, and evidence
    repo = Repository(
        id=str(uuid.uuid4()),
        url="https://github.com/delete-test/repo.git",
        name="repo",
        owner="delete-test",
    )
    test_db_session.add(repo)
    await test_db_session.commit()

    analysis = AnalysisRun(
        id=str(uuid.uuid4()),
        repository_id=repo.id,
        status=AnalysisStatus.COMPLETED,
    )
    test_db_session.add(analysis)
    await test_db_session.commit()

    finding = Finding(
        id=str(uuid.uuid4()),
        analysis_run_id=analysis.id,
        finding="Sample Risk",
        category=RiskCategory.GIT,
        severity=RiskSeverity.LOW,
    )
    test_db_session.add(finding)
    await test_db_session.commit()

    evidence = Evidence(
        id=str(uuid.uuid4()),
        finding_id=finding.id,
        type=EvidenceType.GIT,
        file="file.py",
        description="git log evidence",
    )
    test_db_session.add(evidence)
    await test_db_session.commit()

    # Delete repository
    await test_db_session.delete(repo)
    await test_db_session.commit()

    # Confirm all cascading records are deleted
    f_res = await test_db_session.execute(select(Finding).where(Finding.id == finding.id))
    assert f_res.scalars().first() is None

    e_res = await test_db_session.execute(select(Evidence).where(Evidence.id == evidence.id))
    assert e_res.scalars().first() is None
