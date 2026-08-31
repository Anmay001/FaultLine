import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.finding import Finding


class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False, index=True
    )
    
    commit_hash: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Deterministic scores (0 - 100)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    code_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    test_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    git_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dependency_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    architecture_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    documentation_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata & timings
    sandbox_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository", back_populates="analysis_runs")
    findings: Mapped[List["Finding"]] = relationship(
        "Finding", back_populates="analysis_run", cascade="all, delete-orphan"
    )
