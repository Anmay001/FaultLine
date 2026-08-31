from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

from app.llm.provider import LLMProvider

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for deterministic offline testing and CI workflows."""

    def __init__(
        self,
        mock_text_response: str = "Mock analysis result",
        mock_structured_response: Optional[Any] = None,
    ):
        self.mock_text_response = mock_text_response
        self.mock_structured_response = mock_structured_response
        self.call_history: list[dict] = []

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        model: Optional[str] = None,
    ) -> str:
        self.call_history.append({
            "type": "text",
            "prompt": prompt,
            "system_instruction": system_instruction,
            "temperature": temperature,
            "model": model,
        })
        return self.mock_text_response

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        model: Optional[str] = None,
    ) -> T:
        self.call_history.append({
            "type": "structured",
            "prompt": prompt,
            "response_model": response_model.__name__,
            "system_instruction": system_instruction,
            "temperature": temperature,
            "model": model,
        })

        if self.mock_structured_response is not None:
            if isinstance(self.mock_structured_response, response_model):
                return self.mock_structured_response
            elif isinstance(self.mock_structured_response, dict):
                return response_model.model_validate(self.mock_structured_response)
        
        if response_model.__name__ == "BaselineReport":
            # Simulate a standard single-prompt LLM audit with speculative claims
            from app.baseline.evaluator import BaselineReport, BaselineFinding
            from app.models.finding import RiskCategory, RiskSeverity
            
            # If prompt mentions high churn or payment
            if "payment" in prompt.lower() or "transaction" in prompt.lower():
                return BaselineReport(
                    overall_score=68.0,
                    summary="Repository appears to handle payments with high complexity and missing tests.",
                    findings=[
                        BaselineFinding(
                            finding="Possible memory leak in event loop",
                            category=RiskCategory.CODE,
                            severity=RiskSeverity.HIGH,
                            description="Code may not release handlers properly.",
                            suggested_file="src/async_handler.py"  # Hallucinated non-existent file
                        ),
                        BaselineFinding(
                            finding="Payment processing complexity in payment_engine.py",
                            category=RiskCategory.CODE,
                            severity=RiskSeverity.CRITICAL,
                            description="Payment engine contains multiple branches.",
                            suggested_file="src/payment_engine.py"  # Real file
                        ),
                        BaselineFinding(
                            finding="Missing unit tests across codebase",
                            category=RiskCategory.TEST,
                            severity=RiskSeverity.HIGH,
                            description="No test directory was discovered in the repository tree.",
                            suggested_file=None  # Ungrounded general claim
                        ),
                    ]
                )
            elif "express" in prompt.lower() or "package.json" in prompt.lower():
                return BaselineReport(
                    overall_score=72.0,
                    summary="Dependency tree contains outdated packages.",
                    findings=[
                        BaselineFinding(
                            finding="Outdated package.json dependencies",
                            category=RiskCategory.DEPENDENCY,
                            severity=RiskSeverity.HIGH,
                            description="Dependencies like express and lodash might be old.",
                            suggested_file="package.json"
                        ),
                        BaselineFinding(
                            finding="Vulnerable SSL cipher configuration",
                            category=RiskCategory.CODE,
                            severity=RiskSeverity.MEDIUM,
                            description="Potential SSL configuration vulnerability.",
                            suggested_file="config/ssl_config.json"  # Hallucinated file
                        ),
                    ]
                )
            else:
                return BaselineReport(
                    overall_score=85.0,
                    summary="Repository looks relatively clean with test suite.",
                    findings=[
                        BaselineFinding(
                            finding="Potential hardcoded timeout in client",
                            category=RiskCategory.CODE,
                            severity=RiskSeverity.LOW,
                            description="Check timeout values.",
                            suggested_file="src/calculator.py"
                        )
                    ]
                )

        # If no explicit mock provided, construct a minimal valid instance if possible
        try:
            return response_model.model_validate({})
        except Exception:
            # Return construct instance with dummy data
            schema = response_model.model_json_schema()
            dummy_data = {}
            for prop_name, prop_val in schema.get("properties", {}).items():
                p_type = prop_val.get("type")
                if p_type == "string":
                    dummy_data[prop_name] = "test"
                elif p_type in ["number", "integer"]:
                    dummy_data[prop_name] = 0
                elif p_type == "boolean":
                    dummy_data[prop_name] = False
                elif p_type == "array":
                    dummy_data[prop_name] = []
            return response_model.model_validate(dummy_data)
