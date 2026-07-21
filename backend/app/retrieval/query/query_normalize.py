import unicodedata
import re
from typing import Dict
from app.core.logging import get_logger

logger = get_logger("app.retrieval.query_normalize")

NICKNAME_MAPPINGS: Dict[str, str] = {
    "arnie": "Arnold Schwarzenegger",
    "nolan": "Christopher Nolan",
    "leo": "Leonardo DiCaprio",
    "sci-fi": "science fiction",
    "scifi": "science fiction",
    "action-packed": "action",
    "rom-com": "romance comedy",
    "romcom": "romance comedy",
    "spidey": "Spider-Man",
    "tarantino": "Quentin Tarantino",
    "spielberg": "Steven Spielberg",
    "scorsese": "Martin Scorsese"
}

class QueryNormalizer:
    """
    Normalizes query strings to remove formatting inconsistencies and expand abbreviations/nicknames.
    """
    def normalize(self, query: str) -> str:
        if not query:
            return ""

        # Step 1: Unicode decomposition and NFKC normalization
        normalized = unicodedata.normalize("NFKC", query)

        # Step 2: Clean excessive punctuation, keep alphanumeric, spaces, and essential tokens
        normalized = re.sub(r"[^\w\s\-\?\!\'\"]", " ", normalized)
        
        # Step 3: Normalize spaces
        normalized = re.sub(r"\s+", " ", normalized).strip().lower()

        # Step 4: Expand nicknames, abbreviations, and common aliases
        words = normalized.split(" ")
        expanded_words = []
        for word in words:
            expanded = NICKNAME_MAPPINGS.get(word, word)
            expanded_words.append(expanded)
            
        result = " ".join(expanded_words)
        logger.info(f"Query normalization result: '{query}' -> '{result}'")
        return result

query_normalizer = QueryNormalizer()
