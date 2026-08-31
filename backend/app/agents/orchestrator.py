import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.api.schemas import FindingCreate
from app.llm.provider import LLMProvider
from app.models.finding import RiskCategory
from app.agents.base import BaseAgent, AgentResult
from app.agents.scout import RepositoryScoutAgent
from app.agents.code_risk import CodeRiskAgent
from app.agents.test_health import TestHealthAgent
from app.agents.dependency import DependencyRiskAgent
from app.agents.git_history import GitHistoryAgent
from app.agents.docs_consistency import DocsConsistencyAgent
from app.agents.architecture import ArchitectureAgent


class OrchestratorResult(BaseModel):
    repository_path: str
    total_execution_time_seconds: float
    total_findings: int
    findings_by_category: Dict[str, int] = Field(default_factory=dict)
    findings: List[FindingCreate] = Field(default_factory=list)
    agent_results: List[AgentResult] = Field(default_factory=list)


class AgentOrchestrator:
    """Orchestrates parallel execution of all 7 specialized analysis agents via asyncio.gather."""

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        custom_agents: Optional[List[BaseAgent]] = None,
    ):
        self.llm_provider = llm_provider
        if custom_agents is not None:
            self.agents = custom_agents
        else:
            self.agents = [
                RepositoryScoutAgent(llm_provider=llm_provider),
                CodeRiskAgent(llm_provider=llm_provider),
                TestHealthAgent(llm_provider=llm_provider),
                DependencyRiskAgent(llm_provider=llm_provider),
                GitHistoryAgent(llm_provider=llm_provider),
                DocsConsistencyAgent(llm_provider=llm_provider),
                ArchitectureAgent(llm_provider=llm_provider),
            ]

    async def run_all(self, repo_path: Path) -> OrchestratorResult:
        """
        Executes all specialized agents concurrently on the target repository.
        """
        repo_path = Path(repo_path)
        start_time = time.time()

        # Run all agents in parallel
        agent_tasks = [agent.execute(repo_path) for agent in self.agents]
        results: List[AgentResult] = await asyncio.gather(*agent_tasks, return_exceptions=False)

        all_findings: List[FindingCreate] = []
        category_counts: Dict[str, int] = {}

        for res in results:
            for f in res.findings:
                all_findings.append(f)
                cat_str = f.category.value if hasattr(f.category, "value") else str(f.category)
                category_counts[cat_str] = category_counts.get(cat_str, 0) + 1

        total_time = round(time.time() - start_time, 3)

        return OrchestratorResult(
            repository_path=str(repo_path),
            total_execution_time_seconds=total_time,
            total_findings=len(all_findings),
            findings_by_category=category_counts,
            findings=all_findings,
            agent_results=results,
        )
