import abc
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMResponse(BaseModel):
    text: str
    parsed: Optional[Any] = None
    raw_response: Optional[Dict[str, Any]] = None
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


class LLMProvider(abc.ABC):
    """Abstract interface for LLM operations supporting plain text and structured Pydantic outputs."""

    @abc.abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        model: Optional[str] = None,
    ) -> str:
        """Generate unstructured text from the LLM."""
        pass

    @abc.abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        model: Optional[str] = None,
    ) -> T:
        """Generate structured data parsed into a Pydantic model."""
        pass
