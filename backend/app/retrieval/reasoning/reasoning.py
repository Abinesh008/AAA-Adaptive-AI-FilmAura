from typing import AsyncGenerator
from app.core.logging import get_logger
from app.retrieval.contracts.contract import ReasoningContext
from app.retrieval.query.query_trace import QueryTrace
from app.retrieval.reasoning.llm_router import llm_router
from app.retrieval.core.features import features

logger = get_logger("app.retrieval.reasoning")

class ReasoningEngine:
    """
    Coordinates prompt construction and response formatting via MultiLLMRouter.
    """
    async def generate_answer(self, context: ReasoningContext, trace: QueryTrace) -> str:
        trace.record_start("llm_reasoning")
        
        # Enforce feature flags check
        if not features.is_enabled("reasoning"):
            logger.info("Reasoning engine is disabled via feature flags. Omitting LLM call.")
            trace.record_end("llm_reasoning")
            return "Reasoning engine disabled. Please review retrieved candidates list."

        system_instruction = (
            "You are FilmAura Brain, the movie intelligence specialist.\n"
            "Format your answer cleanly. Cite candidate movies explicitly."
        )
        
        try:
            answer = await llm_router.generate_response(
                prompt=context.prompt,
                system_instruction=system_instruction
            )
            trace.record_end("llm_reasoning")
            return answer
        except Exception as e:
            logger.error(f"Reasoning engine failed to generate answer: {str(e)}")
            trace.record_end("llm_reasoning")
            return f"Error generating answer: {str(e)}"

    async def generate_answer_stream(self, context: ReasoningContext, trace: QueryTrace) -> AsyncGenerator[str, None]:
        if not features.is_enabled("reasoning"):
            yield "Reasoning engine disabled."
            return

        system_instruction = "You are FilmAura Brain. Cite movies by title."
        async for chunk in llm_router.generate_response_stream(context.prompt, system_instruction):
            yield chunk

# Export singleton reasoning instance
reasoning_engine = ReasoningEngine()
