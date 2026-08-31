import json
import os
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

from app.core.config import settings
from app.llm.provider import LLMProvider

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    """Google Gemini API implementation using the google-genai SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        self.default_model = default_model or settings.DEFAULT_LLM_MODEL or "gemini-2.0-flash"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable "
                    "or pass api_key to GeminiProvider."
                )
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError("google-genai library is required. Install with: pip install google-genai")
        return self._client

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        model: Optional[str] = None,
    ) -> str:
        """Generate unstructured text from Gemini."""
        target_model = model or self.default_model
        
        # Build configuration
        config = {
            "temperature": temperature,
        }
        if system_instruction:
            config["system_instruction"] = system_instruction

        try:
            response = self.client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            # Fallback or wrap error
            raise RuntimeError(f"Gemini generate_text failed: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        model: Optional[str] = None,
    ) -> T:
        """Generate structured JSON and parse directly into the target Pydantic model."""
        target_model = model or self.default_model
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)

        enhanced_instruction = (
            f"{system_instruction or ''}\n\n"
            f"You MUST respond ONLY with valid JSON conforming exactly to this JSON schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Do not include markdown code blocks or additional conversational text in your output."
        ).strip()

        config = {
            "temperature": temperature,
            "response_mime_type": "application/json",
            "system_instruction": enhanced_instruction,
        }

        try:
            response = self.client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config,
            )
            raw_text = response.text or "{}"
            
            # Clean possible markdown wrapping if returned
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.removeprefix("```json").removesuffix("```").strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text.removeprefix("```").removesuffix("```").strip()

            parsed_data = json.loads(clean_text)
            return response_model.model_validate(parsed_data)
        except Exception as e:
            raise RuntimeError(f"Gemini generate_structured failed for {response_model.__name__}: {str(e)}")
