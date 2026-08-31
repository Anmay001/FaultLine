import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import FindingCreate
from app.agents.orchestrator import AgentOrchestrator
from app.agents.correlator import RiskCorrelator
from app.agents.verifier import VerificationAgent
from app.synthesis.synthesizer import RiskSynthesizer
from app.llm.provider import LLMProvider
from app.models.analysis_run import AnalysisRun, AnalysisStatus
from app.models.finding import Finding
from app.models.evidence import Evidence
from app.sandbox.manager import sandbox_manager


class AnalysisPipelineService:
    """
    End-to-end orchestration pipeline:
    Clone -> 7 Specialized Agents (Parallel) -> Risk Correlation -> Verification -> Synthesis -> SQLite Persistence
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        if llm_provider is None:
            from app.core.config import settings
            import os
            api_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
            if api_key:
                try:
                    from app.llm.gemini import GeminiProvider
                    llm_provider = GeminiProvider(api_key=api_key)
                except Exception:
                    from app.llm.mock import MockLLMProvider
                    llm_provider = MockLLMProvider()
            else:
                from app.llm.mock import MockLLMProvider
                llm_provider = MockLLMProvider()

        self.llm_provider = llm_provider
        self.orchestrator = AgentOrchestrator(llm_provider=llm_provider)
        self.synthesizer = RiskSynthesizer(llm_provider=llm_provider)

    async def execute_analysis(
        self,
        analysis_id: str,
        repo_url: str,
        branch: Optional[str] = None,
        depth: int = 100,
        db: Optional[AsyncSession] = None,
        allow_local_paths: bool = True,
    ) -> AnalysisRun:
        """
        Runs the full 7-step analysis lifecycle on the target repository.
        """
        # Fetch AnalysisRun from DB if session provided
        analysis = None
        if db:
            stmt = select(AnalysisRun).where(AnalysisRun.id == analysis_id)
            res = await db.execute(stmt)
            analysis = res.scalars().first()

        try:
            # 1. Clone into isolated Sandbox
            meta = sandbox_manager.create_sandbox(
                analysis_id=analysis_id,
                repo_url=repo_url,
                target_branch=branch,
                depth=depth,
                allow_local_paths=allow_local_paths,
            )

            sandbox_path = meta.sandbox_path

            if analysis and db:
                analysis.status = AnalysisStatus.RUNNING
                analysis.sandbox_path = str(sandbox_path)
                analysis.commit_hash = meta.commit_hash
                analysis.branch = meta.branch
                analysis.started_at = datetime.now(timezone.utc)
                await db.commit()

            # 2. Run 7 Specialized Agents in Parallel
            orchestrator_result = await self.orchestrator.run_all(sandbox_path)

            # 3. Correlate multi-modal signals into compounded hotspots
            correlated_findings = RiskCorrelator.correlate(orchestrator_result.findings)

            # 4. Verify evidence against actual sandbox filesystem
            verified_findings = VerificationAgent.verify_all(sandbox_path, correlated_findings)

            # 5. Synthesize deterministic scores and generate report
            report = await self.synthesizer.synthesize(verified_findings, project_name=Path(repo_url).stem)

            # 6. Save results to Database
            if analysis and db:
                analysis.status = AnalysisStatus.COMPLETED
                analysis.overall_score = report.overall_score
                analysis.code_risk_score = report.code_risk_score
                analysis.test_risk_score = report.test_risk_score
                analysis.git_risk_score = report.git_risk_score
                analysis.dependency_risk_score = report.dependency_risk_score
                analysis.architecture_risk_score = report.architecture_risk_score
                analysis.documentation_risk_score = report.documentation_risk_score
                analysis.summary = report.summary
                analysis.completed_at = datetime.now(timezone.utc)

                # Persist findings and evidence
                for f_data in verified_findings:
                    f_id = str(uuid.uuid4())
                    finding_rec = Finding(
                        id=f_id,
                        analysis_run_id=analysis_id,
                        finding=f_data.finding,
                        category=f_data.category,
                        severity=f_data.severity,
                        confidence=f_data.confidence,
                        verification_status=f_data.verification_status,
                        verification_notes=f_data.verification_notes,
                    )
                    db.add(finding_rec)

                    for ev_data in f_data.evidence:
                        ev_rec = Evidence(
                            id=str(uuid.uuid4()),
                            finding_id=f_id,
                            type=ev_data.type,
                            file=ev_data.file,
                            line_start=ev_data.line_start,
                            line_end=ev_data.line_end,
                            description=ev_data.description,
                            snippet=ev_data.snippet,
                        )
                        db.add(ev_rec)

                await db.commit()

                # Reload full analysis with relations
                reload_stmt = (
                    select(AnalysisRun)
                    .where(AnalysisRun.id == analysis_id)
                    .options(selectinload(AnalysisRun.findings).selectinload(Finding.evidence))
                )
                reloaded = await db.execute(reload_stmt)
                return reloaded.scalars().first()

            return analysis

        except Exception as e:
            if analysis and db:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = str(e)
                analysis.completed_at = datetime.now(timezone.utc)
                await db.commit()
            raise e
