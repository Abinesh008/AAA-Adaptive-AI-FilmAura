import hashlib
import json
from typing import Dict, Any
from app.core.config import settings
from app.retrieval.features import features

RETRIEVAL_VERSION = "1.0.0"
PLANNER_VERSION = "1.0.0"
FUSION_VERSION = "1.0.0"
RERANKER_VERSION = "1.0.0"
REASONING_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"

def get_configuration_hash() -> str:
    """
    Generate a SHA-256 hash representing the active state of all feature flags,
    weights, models, and retrieval configurations to guarantee reproducibility.
    """
    config_dict = {
        "features": {f: features.get_state(f).value for f in ["query_rewrite", "query_expansion", "graph_search", "vector_search", "sql_search", "reranking", "reasoning", "cache", "diversity", "explainability", "streaming"]},
        "weights": {
            "reranker": settings.RERANKING_WEIGHTS,
            "planner_cost": settings.PLANNER_COST_WEIGHTS
        },
        "models": {
            "embedding": settings.EMBEDDING_PROVIDER,
            "llm": settings.LLM_PROVIDER,
            "llm_model": settings.LLM_MODEL
        },
        "limits": {
            "max_candidates": settings.RETRIEVAL_MAX_CANDIDATES,
            "similarity_threshold": settings.VECTOR_SIMILARITY_THRESHOLD,
            "graph_depth": settings.GRAPH_TRAVERSAL_DEPTH,
            "token_budget": settings.TOKEN_BUDGET
        }
    }
    
    # Deterministic serialization
    config_str = json.dumps(config_dict, sort_keys=True)
    return hashlib.sha256(config_str.encode("utf-8")).hexdigest()

def get_version_manifest() -> Dict[str, Any]:
    return {
        "retrieval_version": RETRIEVAL_VERSION,
        "planner_version": PLANNER_VERSION,
        "fusion_version": FUSION_VERSION,
        "ranking_version": RERANKER_VERSION,
        "reasoning_version": REASONING_VERSION,
        "schema_version": SCHEMA_VERSION,
        "configuration_hash": get_configuration_hash()
    }
