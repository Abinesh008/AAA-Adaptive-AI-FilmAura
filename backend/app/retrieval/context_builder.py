from typing import List, Dict, Any
from app.core.config import settings
from app.retrieval.contract import CandidateMovie, ReasoningContext
from app.core.logging import get_logger

logger = get_logger("app.retrieval.context_builder")

class ContextBuilder:
    """
    Assembles structured query context for LLMs, enforcing and optimizing token budgets.
    """
    def build_context(self, candidates: List[CandidateMovie], token_budget: int = 4000) -> ReasoningContext:
        logger.info(f"Compiling context for {len(candidates)} candidates within budget: {token_budget} tokens.")
        
        # Simple local token estimator (4 characters ~= 1 token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
            
        context_blocks = []
        for rank, cand in enumerate(candidates, 1):
            block = (
                f"### {rank}. Movie Title: {cand.title} (ID: {cand.tmdb_id})\n"
                f"- **Confidence**: {cand.confidence} (Matched by: {', '.join(cand.matched_by_sources)})\n"
                f"- **Popularity**: {cand.metadata.get('popularity', 'N/A')}\n"
                f"- **Overview**: {cand.metadata.get('overview', 'No overview details available.')}\n"
            )
            
            # Append theme or scene details if present
            scenes = cand.metadata.get("scenes")
            if scenes:
                block += f"- **Notable Scenes**: {'; '.join(scenes)}\n"
                
            block += "\n"
            context_blocks.append((cand.tmdb_id, block))
            
        # Compile full context string
        context_str = "".join(b[1] for b in context_blocks)
        token_count = estimate_tokens(context_str)
        
        # Enforce budget limit and compress if necessary
        if token_count > token_budget:
            logger.warning(f"Context size ({token_count} tokens) exceeds budget ({token_budget}). Running compression...")
            context_str = self._compress_context(context_blocks, token_budget, estimate_tokens)
            token_count = estimate_tokens(context_str)
            
        prompt = (
            "You are an advanced film specialist reasoning engine for AAA-Adaptive-AI-FilmAura.\n"
            "Below is the retrieved film context from our unified knowledge base:\n\n"
            f"{context_str}\n"
            "Answer the user query concisely, citing movies by title and TMDB ID.\n"
        )
        
        return ReasoningContext(
            prompt=prompt,
            context_str=context_str,
            token_count=token_count
        )

    def _compress_context(self, blocks: List[Tuple[int, str]], budget: int, token_estimator: Callable[[str], int]) -> str:
        """
        Compress context by prioritizing top matches and trimming lower-ranked movies.
        """
        compressed_blocks = []
        current_tokens = 0
        
        # Add blocks one by one until budget limit is hit
        for tmdb_id, text in blocks:
            block_tokens = token_estimator(text)
            if current_tokens + block_tokens <= budget:
                compressed_blocks.append(text)
                current_tokens += block_tokens
            else:
                # Add truncated reference to save space
                summary = f"- [Truncated details for Movie ID {tmdb_id} due to token budget limits]\n\n"
                compressed_blocks.append(summary)
                break
                
        return "".join(compressed_blocks)

from typing import Tuple, Callable
# Export singleton instance
context_builder = ContextBuilder()
