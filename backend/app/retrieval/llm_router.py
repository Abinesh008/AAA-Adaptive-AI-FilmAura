from typing import List, Dict, Any, AsyncGenerator
from app.api.deps import get_llm_provider
from app.core.interfaces.llm import BaseLLMProvider
from app.core.providers.llm.mock import MockLLMProvider
from app.retrieval.circuit_breaker import circuit_breakers
from app.core.logging import get_logger

logger = get_logger("app.retrieval.llm_router")

class MultiLLMRouter:
    """
    Router managing primary and fallback LLM services for final query answers.
    """
    def __init__(self):
        # We fetch the default configured providers
        self.primary_provider_name = "gemini"  # Default configuration provider
        self.fallback_provider_name = "mock"

    async def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        cb_llm = circuit_breakers.get("llm")
        
        # Try primary LLM provider
        if cb_llm and cb_llm.is_allowed():
            try:
                provider = get_llm_provider()
                logger.info(f"Routing query to primary LLM provider: {provider.__class__.__name__}")
                response = await provider.generate_async(prompt, system_instruction=system_instruction)
                cb_llm.record_success()
                return response
            except Exception as e:
                logger.error(f"Primary LLM provider failed: {str(e)}. Tripping circuit and falling back.")
                if cb_llm:
                    cb_llm.record_failure()
                    
        # Fallback path: Mock response generation
        logger.info("Routing query to fallback MockLLMProvider.")
        mock_provider = MockLLMProvider()
        return await mock_provider.generate_async(prompt, system_instruction=system_instruction)

    async def generate_response_stream(self, prompt: str, system_instruction: str = "") -> AsyncGenerator[str, None]:
        """
        Supports future streaming reasoning blocks.
        """
        try:
            provider = get_llm_provider()
            async for chunk in provider.stream(prompt, system_instruction=system_instruction):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming failed, falling back to static mock chunks: {str(e)}")
            mock_provider = MockLLMProvider()
            async for chunk in mock_provider.stream(prompt, system_instruction=system_instruction):
                yield chunk

# Export singleton instance
llm_router = MultiLLMRouter()
