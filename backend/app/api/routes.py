import re
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.repository import Repository
from app.models.analysis_run import AnalysisRun, AnalysisStatus
from app.models.finding import Finding
from app.models.evidence import Evidence
from app.sandbox.manager import sandbox_manager
from app.sandbox.cloner import RepositoryClonerError, InvalidRepositoryURLError
from app.services.analysis_pipeline import AnalysisPipelineService
from app.api.schemas import (
    HealthCheckResponse,
    RepositoryCreate,
    RepositoryResponse,
    AnalysisRunCreate,
    AnalysisRunResponse,
    FindingCreate,
    FindingResponse,
)

router = APIRouter()


def parse_repo_info_from_url(url: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub/GitLab URL."""
    clean_url = url.rstrip("/").removesuffix(".git")
    parts = clean_url.split("/")
    if len(parts) >= 2:
        owner = parts[-2]
        name = parts[-1]
        return owner, name
    return "unknown", "unknown"


# --- Health Check ---
@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
        database="connected",
        sandbox_storage="ready",
    )


# --- Repository Endpoints ---
@router.post("/repositories", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED, tags=["Repositories"])
async def create_repository(payload: RepositoryCreate, db: AsyncSession = Depends(get_db)):
    # Check if repo already exists
    stmt = select(Repository).where(Repository.url == payload.url).options(selectinload(Repository.analysis_runs))
    result = await db.execute(stmt)
    existing_repo = result.scalars().first()
    if existing_repo:
        return existing_repo

    owner, name = parse_repo_info_from_url(payload.url)
    owner = payload.owner or owner
    name = payload.name or name

    repo = Repository(
        id=str(uuid.uuid4()),
        url=payload.url,
        name=name,
        owner=owner,
        default_branch=payload.default_branch,
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)
    
    # Reload with relationships
    stmt = select(Repository).where(Repository.id == repo.id).options(selectinload(Repository.analysis_runs))
    result = await db.execute(stmt)
    return result.scalars().first()


@router.get("/repositories", response_model=List[RepositoryResponse], tags=["Repositories"])
async def list_repositories(db: AsyncSession = Depends(get_db)):
    stmt = select(Repository).options(selectinload(Repository.analysis_runs)).order_by(desc(Repository.created_at))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/repositories/{repo_id}", response_model=RepositoryResponse, tags=["Repositories"])
async def get_repository(repo_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Repository).where(Repository.id == repo_id).options(
        selectinload(Repository.analysis_runs).selectinload(AnalysisRun.findings).selectinload(Finding.evidence)
    )
    result = await db.execute(stmt)
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repo


# --- Analysis Run Endpoints ---
@router.post("/analyses", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED, tags=["Analyses"])
async def create_analysis_run(payload: AnalysisRunCreate, db: AsyncSession = Depends(get_db)):
    repo: Optional[Repository] = None

    if payload.repository_id:
        stmt = select(Repository).where(Repository.id == payload.repository_id)
        result = await db.execute(stmt)
        repo = result.scalars().first()
        if not repo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    elif payload.repo_url:
        # Check or auto-create repository
        stmt = select(Repository).where(Repository.url == payload.repo_url)
        result = await db.execute(stmt)
        repo = result.scalars().first()
        if not repo:
            owner, name = parse_repo_info_from_url(payload.repo_url)
            repo = Repository(
                id=str(uuid.uuid4()),
                url=payload.repo_url,
                name=name,
                owner=owner,
                default_branch=payload.branch or "main",
            )
            db.add(repo)
            await db.commit()
            await db.refresh(repo)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either repository_id or repo_url must be provided."
        )

    # Initialize analysis run record
    analysis_id = str(uuid.uuid4())
    branch_name = payload.branch or repo.default_branch

    analysis = AnalysisRun(
        id=analysis_id,
        repository_id=repo.id,
        status=AnalysisStatus.PENDING,
        branch=branch_name,
        started_at=datetime.now(timezone.utc),
    )
    db.add(analysis)
    await db.commit()

    # Execute full analysis pipeline
    pipeline_service = AnalysisPipelineService()
    try:
        completed_analysis = await pipeline_service.execute_analysis(
            analysis_id=analysis_id,
            repo_url=repo.url,
            branch=branch_name,
            depth=payload.shallow_depth,
            db=db,
            allow_local_paths=True,
        )
        return completed_analysis
    except Exception as e:
        # Fetch updated record if failed
        stmt = (
            select(AnalysisRun)
            .where(AnalysisRun.id == analysis_id)
            .options(selectinload(AnalysisRun.findings).selectinload(Finding.evidence))
        )
        res = await db.execute(stmt)
        return res.scalars().first()


@router.get("/analyses/{analysis_id}", response_model=AnalysisRunResponse, tags=["Analyses"])
async def get_analysis_run(analysis_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(AnalysisRun)
        .where(AnalysisRun.id == analysis_id)
        .options(selectinload(AnalysisRun.findings).selectinload(Finding.evidence))
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found")
    return analysis


@router.get("/analyses", response_model=List[AnalysisRunResponse], tags=["Analyses"])
async def list_analyses(
    repository_id: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AnalysisRun)
        .options(selectinload(AnalysisRun.findings).selectinload(Finding.evidence))
        .order_by(desc(AnalysisRun.created_at))
        .limit(limit)
    )
    if repository_id:
        stmt = stmt.where(AnalysisRun.repository_id == repository_id)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/analyses/{analysis_id}/findings", response_model=FindingResponse, status_code=status.HTTP_201_CREATED, tags=["Findings"])
async def add_finding_to_analysis(
    analysis_id: str,
    payload: FindingCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify analysis exists
    stmt = select(AnalysisRun).where(AnalysisRun.id == analysis_id)
    res = await db.execute(stmt)
    analysis = res.scalars().first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found")

    finding_id = str(uuid.uuid4())
    finding = Finding(
        id=finding_id,
        analysis_run_id=analysis_id,
        finding=payload.finding,
        category=payload.category,
        severity=payload.severity,
        confidence=payload.confidence,
        verification_status=payload.verification_status,
        verification_notes=payload.verification_notes,
    )
    db.add(finding)

    # Add evidence items
    for ev in payload.evidence:
        ev_record = Evidence(
            id=str(uuid.uuid4()),
            finding_id=finding_id,
            type=ev.type,
            file=ev.file,
            line_start=ev.line_start,
            line_end=ev.line_end,
            description=ev.description,
            snippet=ev.snippet,
        )
        db.add(ev_record)

    await db.commit()

    # Return created finding with evidence
    stmt = select(Finding).where(Finding.id == finding_id).options(selectinload(Finding.evidence))
    result = await db.execute(stmt)
    return result.scalars().first()


# --- Sandbox Management Endpoints ---
@router.get("/sandboxes/{analysis_id}/files", tags=["Sandbox"])
async def list_sandbox_files(analysis_id: str, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(AnalysisRun).where(AnalysisRun.id == analysis_id)
        res = await db.execute(stmt)
        analysis = res.scalars().first()
        custom_path = Path(analysis.sandbox_path) if (analysis and analysis.sandbox_path) else None

        files = sandbox_manager.list_files(analysis_id, custom_sandbox_path=custom_path)
        return {"analysis_id": analysis_id, "files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sandboxes/{analysis_id}/file-content", tags=["Sandbox"])
async def get_sandbox_file_content(analysis_id: str, file_path: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(AnalysisRun).where(AnalysisRun.id == analysis_id)
        res = await db.execute(stmt)
        analysis = res.scalars().first()
        custom_path = Path(analysis.sandbox_path) if (analysis and analysis.sandbox_path) else None

        content = sandbox_manager.read_file(analysis_id, file_path, custom_sandbox_path=custom_path)
        return {"analysis_id": analysis_id, "file_path": file_path, "content": content}
    except (FileNotFoundError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/sandboxes/{analysis_id}", tags=["Sandbox"])
async def delete_sandbox(analysis_id: str):
    cleaned = sandbox_manager.cleanup_sandbox(analysis_id)
    return {"analysis_id": analysis_id, "cleaned": cleaned}
