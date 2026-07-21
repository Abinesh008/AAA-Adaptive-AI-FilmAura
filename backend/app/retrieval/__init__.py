import sys
import importlib

# Define backward-compatible mappings: old submodule name -> new module path
module_mappings = {
    "orchestrator": "app.retrieval.core.orchestrator",
    "planner": "app.retrieval.core.planner",
    "registry": "app.retrieval.core.registry",
    "supervisor": "app.retrieval.core.supervisor",
    "sdk": "app.retrieval.core.sdk",
    "circuit_breaker": "app.retrieval.core.circuit_breaker",
    "guardrails": "app.retrieval.core.guardrails",
    "strategy_learning": "app.retrieval.core.strategy_learning",
    "features": "app.retrieval.core.features",

    "query_normalize": "app.retrieval.query.query_normalize",
    "query_expansion": "app.retrieval.query.query_expansion",
    "query_trace": "app.retrieval.query.query_trace",
    "disambiguation": "app.retrieval.query.disambiguation",

    "reasoning": "app.retrieval.reasoning.reasoning",
    "llm_router": "app.retrieval.reasoning.llm_router",
    "context_builder": "app.retrieval.reasoning.context_builder",
    "context_memory": "app.retrieval.reasoning.context_memory",
    "evidence": "app.retrieval.reasoning.evidence",
    "explanation": "app.retrieval.reasoning.explanation",

    "reranker": "app.retrieval.ranking.reranker",
    "fusion": "app.retrieval.ranking.fusion",
    "diversity": "app.retrieval.ranking.diversity",
    "confidence": "app.retrieval.ranking.confidence",
    "calibration": "app.retrieval.ranking.calibration",
    "quality": "app.retrieval.ranking.quality",

    "retrieval_cache": "app.retrieval.cache.retrieval_cache",
    "session_store": "app.retrieval.cache.session_store",
    "snapshots": "app.retrieval.cache.snapshots",

    "analytics": "app.retrieval.analytics.analytics",
    "profiler": "app.retrieval.analytics.profiler",
    "replay": "app.retrieval.analytics.replay",
    "evaluation": "app.retrieval.analytics.evaluation",
    "datasets": "app.retrieval.analytics.datasets",
    "versioning": "app.retrieval.analytics.versioning",

    "contract": "app.retrieval.contracts.contract",
    "capabilities": "app.retrieval.contracts.capabilities",
    "resources": "app.retrieval.contracts.resources",
    "integrity": "app.retrieval.contracts.integrity",

    "hooks": "app.retrieval.hooks.hooks",
    "event_bus": "app.retrieval.hooks.event_bus"
}

# Dynamically load target modules and bind them to the old paths
this_module = sys.modules[__name__]

for short_name, full_path in module_mappings.items():
    # Import the target module object directly
    importlib.import_module(full_path)
    mod = sys.modules[full_path]
    
    # Register the submodule under its old import path
    sys.modules[f"app.retrieval.{short_name}"] = mod
    
    # Bind the module as an attribute on the parent package
    setattr(this_module, short_name, mod)

# Export names from packages for from app.retrieval import ... usage
from app.retrieval.core.sdk import retrieval_client
from app.retrieval.core.orchestrator import orchestrator, RetrievalOrchestrator
from app.retrieval.query.disambiguation import ambiguity_resolver
