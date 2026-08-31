import time
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from app.llm.provider import LLMProvider
from app.llm.gemini import GeminiProvider
from app.tools.file_tree_tool import FileTreeTool
from app.models.finding import RiskCategory, RiskSeverity


class BaselineFinding(BaseModel):
    finding: str = Field(description="Title or summary of the detected risk")
    category: RiskCategory = Field(description="Category of the risk: CODE, TEST, GIT, DEPENDENCY, ARCHITECTURE, DOCUMENTATION")
    severity: RiskSeverity = Field(description="Severity: CRITICAL, HIGH, MEDIUM, LOW")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence level between 0 and 1")
    description: str = Field(description="Explanation of the risk and why it was identified")
    suggested_file: Optional[str] = Field(default=None, description="The file path suspected of containing the issue")


class BaselineReport(BaseModel):
    overall_score: float = Field(default=70.0, ge=0.0, le=100.0, description="Overall repository health score from 0 to 100")
    summary: str = Field(description="Executive summary of the repository risks")
    code_risk_score: float = Field(default=70.0, ge=0.0, le=100.0)
    test_risk_score: float = Field(default=70.0, ge=0.0, le=100.0)
    dependency_risk_score: float = Field(default=70.0, ge=0.0, le=100.0)
    architecture_risk_score: float = Field(default=70.0, ge=0.0, le=100.0)
    findings: List[BaselineFinding] = Field(default_factory=list, description="List of identified risk findings")


class BaselineEvaluationResult(BaseModel):
    repository_path: str
    report: BaselineReport
    execution_time_seconds: float
    files_scanned: int
    manifests_included: int
    model_used: str


class BaselineEvaluator:
    """
    Single-prompt baseline evaluator.
    Directly prompts an LLM with directory tree & manifest context without tool validation or verification.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or GeminiProvider()

    async def evaluate_repository(
        self,
        repo_path: Path,
        model: Optional[str] = None,
    ) -> BaselineEvaluationResult:
        """
        Evaluates the target repository using a single ungrounded LLM prompt.
        """
        repo_path = Path(repo_path)
        start_time = time.time()

        # Extract file tree and manifests
        tree_summary = FileTreeTool.analyze_tree(
            repo_path,
            max_depth=4,
            max_files_in_tree=120,
            max_manifest_bytes=10_000,
        )

        # Build prompt payload
        manifest_text_blocks = []
        for m in tree_summary.manifests:
            manifest_text_blocks.append(
                f"### Manifest: `{m.relative_path}` ({m.file_type})\n```\n{m.content}\n```"
            )

        manifests_combined = "\n\n".join(manifest_text_blocks) if manifest_text_blocks else "No manifest files found."

        prompt = f"""You are a software project auditor evaluating repository risks.
Examine the following repository structure and manifest files to identify potential risks, bugs, lack of tests, security issues, or architectural vulnerabilities.

Repository Overview:
- Total Files: {tree_summary.total_files}
- Estimated LOC: {tree_summary.total_loc}
- Languages: {tree_summary.languages}
- Has Tests: {tree_summary.has_tests}
- Has Documentation: {tree_summary.has_documentation}
- Has Docker: {tree_summary.has_docker}
- Has CI: {tree_summary.has_ci}

Directory Structure:
```
{tree_summary.formatted_tree}
```

Manifest & Configuration Files:
{manifests_combined}

Based ONLY on this overview, identify the major project risks and assign an overall health score (0-100 where 100 is flawless and 0 is critical failure).
"""

        system_instruction = (
            "You are an automated code risk evaluator. Provide a concise, structured assessment of project health and risk factors."
        )

        report = await self.llm_provider.generate_structured(
            prompt=prompt,
            response_model=BaselineReport,
            system_instruction=system_instruction,
            temperature=0.2,
            model=model,
        )

        elapsed = round(time.time() - start_time, 3)

        return BaselineEvaluationResult(
            repository_path=str(repo_path),
            report=report,
            execution_time_seconds=elapsed,
            files_scanned=tree_summary.total_files,
            manifests_included=len(tree_summary.manifests),
            model_used=model or "default",
        )
