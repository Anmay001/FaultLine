import abc
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from app.api.schemas import FindingCreate, EvidenceCreate
from app.llm.provider import LLMProvider
from app.llm.gemini import GeminiProvider
from app.models.finding import RiskCategory, RiskSeverity, VerificationStatus
from app.models.evidence import EvidenceType


class AgentResult(BaseModel):
    agent_name: str
    category: RiskCategory
    execution_time_seconds: float
    findings: List[FindingCreate] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class BaseAgent(abc.ABC):
    """Abstract base class for all specialized FaultLine analysis agents."""

    def __init__(
        self,
        name: str,
        category: RiskCategory,
        llm_provider: Optional[LLMProvider] = None,
    ):
        self.name = name
        self.category = category
        self.llm_provider = llm_provider or GeminiProvider()

    @abc.abstractmethod
    async def run(self, repo_path: Path) -> List[FindingCreate]:
        """
        Executes analysis on the target repository and returns a list of verified or candidate findings.
        All findings must strictly adhere to FindingCreate schema with verifiable evidence items.
        """
        pass

    async def execute(self, repo_path: Path) -> AgentResult:
        """
        Wrapper around run() that tracks execution time and captures errors safely.
        """
        import time
        start_time = time.time()
        try:
            findings = await self.run(repo_path)
            elapsed = round(time.time() - start_time, 3)
            return AgentResult(
                agent_name=self.name,
                category=self.category,
                execution_time_seconds=elapsed,
                findings=findings,
            )
        except Exception as e:
            elapsed = round(time.time() - start_time, 3)
            return AgentResult(
                agent_name=self.name,
                category=self.category,
                execution_time_seconds=elapsed,
                findings=[],
                error=str(e),
            )
