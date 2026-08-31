import pytest
from pydantic import BaseModel
from app.llm.provider import LLMProvider
from app.llm.mock import MockLLMProvider
from app.llm.gemini import GeminiProvider


class SampleOutputSchema(BaseModel):
    summary: str
    risk_score: float
    items: list[str]


@pytest.mark.asyncio
async def test_mock_llm_provider_text():
    provider = MockLLMProvider(mock_text_response="Custom mock answer")
    res = await provider.generate_text("Explain risk")
    assert res == "Custom mock answer"
    assert len(provider.call_history) == 1
    assert provider.call_history[0]["prompt"] == "Explain risk"


@pytest.mark.asyncio
async def test_mock_llm_provider_structured():
    expected_response = SampleOutputSchema(
        summary="High risk repo",
        risk_score=85.0,
        items=["Memory leak", "No tests"],
    )
    provider = MockLLMProvider(mock_structured_response=expected_response)
    
    result = await provider.generate_structured(
        prompt="Analyze risk",
        response_model=SampleOutputSchema,
    )
    
    assert isinstance(result, SampleOutputSchema)
    assert result.summary == "High risk repo"
    assert result.risk_score == 85.0
    assert len(result.items) == 2


def test_gemini_provider_init():
    provider = GeminiProvider(api_key="test-api-key", default_model="gemini-2.0-flash")
    assert provider.api_key == "test-api-key"
    assert provider.default_model == "gemini-2.0-flash"


def test_gemini_provider_missing_key_error():
    provider = GeminiProvider(api_key="")
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
        _ = provider.client
