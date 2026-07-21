from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.core.logging import get_logger

logger = get_logger("app.retrieval.disambiguation")

class DisambiguationCandidate(BaseModel):
    tmdb_id: int
    title: str
    year: int
    extra_info: str

class DisambiguationResult(BaseModel):
    is_ambiguous: bool
    message: str
    candidates: List[DisambiguationCandidate] = Field(default_factory=list)

# Hardcoded ambiguity mappings for common movie search terms
AMBIGUITY_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "batman": {
        "message": "Which Batman movie are you looking for?",
        "candidates": [
            {"tmdb_id": 272, "title": "Batman", "year": 1989, "extra_info": "Directed by Tim Burton"},
            {"tmdb_id": 155, "title": "The Dark Knight", "year": 2008, "extra_info": "Directed by Christopher Nolan"},
            {"tmdb_id": 414906, "title": "The Batman", "year": 2022, "extra_info": "Directed by Matt Reeves"}
        ]
    },
    "avatar": {
        "message": "Which Avatar movie are you looking for?",
        "candidates": [
            {"tmdb_id": 19995, "title": "Avatar", "year": 2009, "extra_info": "Directed by James Cameron"},
            {"tmdb_id": 76600, "title": "Avatar: The Way of Water", "year": 2022, "extra_info": "Directed by James Cameron"}
        ]
    },
    "joker": {
        "message": "Which Joker movie are you looking for?",
        "candidates": [
            {"tmdb_id": 475557, "title": "Joker", "year": 2019, "extra_info": "Directed by Todd Phillips"},
            {"tmdb_id": 926393, "title": "Joker: Folie à Deux", "year": 2024, "extra_info": "Directed by Todd Phillips"}
        ]
    },
    "king kong": {
        "message": "Which King Kong movie are you looking for?",
        "candidates": [
            {"tmdb_id": 244, "title": "King Kong", "year": 1933, "extra_info": "Original classic film"},
            {"tmdb_id": 254, "title": "King Kong", "year": 2005, "extra_info": "Directed by Peter Jackson"},
            {"tmdb_id": 399055, "title": "Kong: Skull Island", "year": 2017, "extra_info": "MonsterVerse film"}
        ]
    }
}

class AmbiguityResolver:
    """
    Resolver detecting ambiguous search inputs and generating structured options.
    """
    def resolve_ambiguity(self, query: str) -> DisambiguationResult:
        normalized = query.strip().lower()
        
        # Simple match check
        if normalized in AMBIGUITY_MAPPINGS:
            data = AMBIGUITY_MAPPINGS[normalized]
            logger.info(f"Ambiguity detected for search term: {normalized}")
            candidates = [
                DisambiguationCandidate(**cand) for cand in data["candidates"]
            ]
            return DisambiguationResult(
                is_ambiguous=True,
                message=data["message"],
                candidates=candidates
            )
            
        return DisambiguationResult(is_ambiguous=False, message="")

ambiguity_resolver = AmbiguityResolver()
