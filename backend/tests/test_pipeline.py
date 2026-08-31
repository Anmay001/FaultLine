import pytest
import uuid
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.repository import Repository
from app.models.analysis_run import AnalysisRun, AnalysisStatus
from app.models.finding import Finding
from app.llm.mock import MockLLMProvider
from app.services.analysis_pipeline import AnalysisPipelineService


@pytest.mark.asyncio
async def test_full_analysis_pipeline_e2e(
    test_db_session: AsyncSession,
    sample_local_git_repo: Path
):
    # 1. Create Repository in DB
    repo_id = str(uuid.uuid4())
    repo = Repository(
        id=repo_id,
        url=str(sample_local_git_repo),
        name="test-repo",
        owner="local",
        default_branch="master",
    )
    test_db_session.add(repo)
    await test_db_session.commit()

    # 2. Create initial AnalysisRun in DB
    analysis_id = str(uuid.uuid4())
    analysis = AnalysisRun(
        id=analysis_id,
        repository_id=repo_id,
        status=AnalysisStatus.PENDING,
        branch="master",
    )
    test_db_session.add(analysis)
    await test_db_session.commit()

    # 3. Execute full pipeline using MockLLMProvider
    pipeline = AnalysisPipelineService(llm_provider=MockLLMProvider())
    completed = await pipeline.execute_analysis(
        analysis_id=analysis_id,
        repo_url=str(sample_local_git_repo),
        branch="master",
        depth=50,
        db=test_db_session,
        allow_local_paths=True,
    )

    # 4. Verify completed analysis properties
    assert completed is not None
    assert completed.status == AnalysisStatus.COMPLETED
    assert completed.overall_score is not None
    assert completed.code_risk_score is not None
    assert completed.commit_hash is not None
    assert completed.summary is not None
    assert len(completed.findings) >= 1

    # Verify findings are persisted in SQLite DB
    stmt = (
        select(Finding)
        .where(Finding.analysis_run_id == analysis_id)
        .options(selectinload(Finding.evidence))
    )
    res = await test_db_session.execute(stmt)
    persisted_findings = res.scalars().all()
    assert len(persisted_findings) >= 1
    assert all(len(f.evidence) >= 1 for f in persisted_findings)
