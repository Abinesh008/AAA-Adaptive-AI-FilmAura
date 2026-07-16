import asyncio
from typing import AsyncGenerator
from app.core.interfaces.llm import BaseLLMProvider
from app.core.logging import get_logger

logger = get_logger("app.providers.llm.mock")

class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider returning simulated responses.
    """
    def generate(self, prompt: str, **kwargs) -> str:
        logger.info(f"Mock generate called with prompt length: {len(prompt)}")
        return f"[Mock LLM Response] processed prompt: '{prompt[:40]}...'"

    async def generate_async(self, prompt: str, **kwargs) -> str:
        logger.info(f"Mock generate_async called")
        await asyncio.sleep(0.1)  # Simulate small network latency
        return self.generate(prompt, **kwargs)

    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        logger.info(f"Mock stream called")
        response_text = f"[Mock LLM Streamed Response] for prompt: '{prompt[:30]}...'"
        for word in response_text.split(" "):
            yield word + " "
            await asyncio.sleep(0.05)
