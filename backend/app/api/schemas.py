from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.analysis_run import AnalysisStatus
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType


# Evidence Schemas
class EvidenceBase(BaseModel):
    type: EvidenceType
    file: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    description: str
    snippet: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceResponse(EvidenceBase):
    id: str
    finding_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Finding Schemas
class FindingBase(BaseModel):
    finding: str
    category: RiskCategory
    severity: RiskSeverity
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    verification_status: VerificationStatus = VerificationStatus.INSUFFICIENT_EVIDENCE
    verification_notes: Optional[str] = None


class FindingCreate(FindingBase):
    evidence: List[EvidenceCreate] = []


class FindingResponse(FindingBase):
    id: str
    analysis_run_id: str
    created_at: datetime
    evidence: List[EvidenceResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Analysis Run Schemas
class AnalysisRunCreate(BaseModel):
    repository_id: Optional[str] = None
    repo_url: Optional[str] = None
    branch: Optional[str] = None
    shallow_depth: int = 100


class AnalysisRunResponse(BaseModel):
    id: str
    repository_id: str
    status: AnalysisStatus
    commit_hash: Optional[str] = None
    branch: Optional[str] = None
    overall_score: Optional[float] = None
    code_risk_score: Optional[float] = None
    test_risk_score: Optional[float] = None
    git_risk_score: Optional[float] = None
    dependency_risk_score: Optional[float] = None
    architecture_risk_score: Optional[float] = None
    documentation_risk_score: Optional[float] = None
    summary: Optional[str] = None
    error_message: Optional[str] = None
    sandbox_path: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    findings: List[FindingResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Repository Schemas
class RepositoryCreate(BaseModel):
    url: str
    name: Optional[str] = None
    owner: Optional[str] = None
    default_branch: str = "main"


class RepositoryResponse(BaseModel):
    id: str
    url: str
    name: str
    owner: str
    default_branch: str
    created_at: datetime
    updated_at: datetime
    analysis_runs: List[AnalysisRunResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Health and Status Schemas
class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    version: str
    timestamp: datetime
    database: str = "connected"
    sandbox_storage: str = "ready"
