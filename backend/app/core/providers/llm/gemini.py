import asyncio
from typing import AsyncGenerator
from openai import OpenAI, AsyncOpenAI
from app.core.interfaces.llm import BaseLLMProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.providers.llm.gemini")

class GeminiLLMProvider(BaseLLMProvider):
    """
    Gemini provider implementing BaseLLMProvider via Gemini's OpenAI-compatibility layer.
    """
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        # Fallback to gemini-1.5-flash if none provided
        self.model = model or "gemini-1.5-flash"
        
        # Gemini's official OpenAI-compatible endpoint
        base_url = "https://generativelanguage.googleapis.com/v1beta/"
        
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            logger.debug(f"Calling Gemini generate with model={self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Gemini generate failed: {e}")
            raise

    async def generate_async(self, prompt: str, **kwargs) -> str:
        try:
            logger.debug(f"Calling Gemini generate_async with model={self.model}")
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Gemini generate_async failed: {e}")
            raise

    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        try:
            logger.debug(f"Calling Gemini stream with model={self.model}")
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                **kwargs
            )
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Gemini stream failed: {e}")
            raise
