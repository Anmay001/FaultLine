import pytest
import tempfile
from pathlib import Path

from app.llm.mock import MockLLMProvider
from app.baseline.evaluator import BaselineEvaluator, BaselineReport, BaselineFinding
from app.models.finding import RiskCategory, RiskSeverity


@pytest.mark.asyncio
async def test_baseline_evaluator_with_mock_llm():
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_dir = Path(tmp_dir)
        (repo_dir / "README.md").write_text("# Mock Project\nA demo project for testing.", encoding="utf-8")
        (repo_dir / "package.json").write_text('{"name": "demo", "dependencies": {"express": "4.17.1"}}', encoding="utf-8")
        (repo_dir / "server.js").write_text("const express = require('express');", encoding="utf-8")

        mock_report = BaselineReport(
            overall_score=65.0,
            summary="Identified outdated express dependency and missing unit tests.",
            code_risk_score=70.0,
            test_risk_score=50.0,
            dependency_risk_score=60.0,
            architecture_risk_score=80.0,
            findings=[
                BaselineFinding(
                    finding="Outdated Express Framework Version",
                    category=RiskCategory.DEPENDENCY,
                    severity=RiskSeverity.HIGH,
                    confidence=0.85,
                    description="Express version 4.17.1 is outdated and may contain known vulnerabilities.",
                    suggested_file="package.json",
                ),
                BaselineFinding(
                    finding="Missing Test Suite",
                    category=RiskCategory.TEST,
                    severity=RiskSeverity.HIGH,
                    confidence=0.90,
                    description="No test directory or test scripts were found in the package.",
                    suggested_file=None,
                )
            ]
        )

        mock_provider = MockLLMProvider(mock_structured_response=mock_report)
        evaluator = BaselineEvaluator(llm_provider=mock_provider)

        result = await evaluator.evaluate_repository(repo_dir)

        assert result.repository_path == str(repo_dir)
        assert result.report.overall_score == 65.0
        assert len(result.report.findings) == 2
        assert result.report.findings[0].category == RiskCategory.DEPENDENCY
        assert result.files_scanned >= 3
        assert result.manifests_included >= 2
        assert len(mock_provider.call_history) == 1
        assert "package.json" in mock_provider.call_history[0]["prompt"]
