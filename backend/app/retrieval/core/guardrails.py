import re
from typing import List, Tuple, Optional
from app.core.logging import get_logger
from app.retrieval.query.query_trace import QueryTrace

logger = get_logger("app.retrieval.guardrails")

# Common injection vectors and jailbreaks targeting prompt manipulation
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+a\s+[^,\.]*",
    r"jailbreak",
    r"bypass\s+restrictions",
    r"system\s+prompt",
    r"developer\s+mode",
    r"override\s+system",
    r"ignore\s+above"
]

class GuardrailEngine:
    """
    Validation engine ensuring safety and semantic integrity of input queries.
    """
    def __init__(self, max_length: int = 1000):
        self.max_length = max_length

    def validate_query(self, query: str, trace: QueryTrace) -> Tuple[bool, Optional[str]]:
        """
        Validate query and record metrics. Returns (is_valid, error_message).
        """
        if not query or not query.strip():
            err = "Query string cannot be empty."
            logger.warning(f"Guardrail check failed: {err}")
            return False, err

        if len(query) > self.max_length:
            err = f"Query length ({len(query)}) exceeds maximum allowed limit ({self.max_length})."
            logger.warning(f"Guardrail check failed: {err}")
            return False, err

        # Normalise repeat token patterns (e.g., repeating spaces or exclamation marks)
        normalized = re.sub(r"\s+", " ", query.strip())
        normalized = re.sub(r"([!?\.])\1+", r"\1", normalized)

        # Check prompt injection patterns
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                err = "Possible security validation attempt (prompt injection pattern detected)."
                logger.warning(f"Guardrail check failed: {err} | Query: {query}")
                return False, err

        # Verify external ID shapes if present in intent parsing
        # (e.g., checking for wikidata codes Qxxxx or imdb codes ttXXXXXX)
        if re.search(r"\btt[0-9]{3,}\b", normalized) or re.search(r"\bQ[0-9]{2,}\b", normalized):
            logger.info("External identifier pattern found in query.")

        return True, None

guardrail_engine = GuardrailEngine()
