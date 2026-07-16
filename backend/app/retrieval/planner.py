from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.core.config import settings
from app.core.logging import get_logger
from app.retrieval.contract import QueryIntent, ExecutionPlan, ExecutionStep
from app.retrieval.features import features
from app.retrieval.registry import capability_registry
from app.retrieval.strategy_learning import strategy_learning_engine

logger = get_logger("app.retrieval.planner")

class BasePlanner(ABC):
    @abstractmethod
    def plan(self, intent: QueryIntent, profile: str = "balanced") -> ExecutionPlan:
        pass

class CostAwarePlanner(BasePlanner):
    """
    Query planner estimating plugin costs and dynamic capability queries.
    """
    def plan(self, intent: QueryIntent, profile: str = "balanced") -> ExecutionPlan:
        steps: List[ExecutionStep] = []
        primary_intent = intent.primary_intent.lower()
        
        # Check learned strategy preference
        preferred_strategy = strategy_learning_engine.get_preferred_strategy(primary_concept := intent.primary_intent)
        strategy = preferred_strategy or self._determine_default_strategy(primary_intent, profile)
        logger.info(f"Selected execution strategy for '{primary_intent}': {strategy}")
        
        cost_weights = settings.PLANNER_COST_WEIGHTS
        
        # 1. PostgreSQL Step
        if strategy in ("sql", "hybrid") and features.is_enabled("sql_search"):
            postgres_plugins = capability_registry.get_plugins_supporting("supports_sql")
            for plug_name in postgres_plugins:
                steps.append(ExecutionStep(
                    plugin_name=plug_name,
                    capability="supports_sql",
                    params={"query": intent.normalized_query, "filters": intent.filters},
                    estimated_cost=float(cost_weights.get("sql", 10))
                ))
                
        # 2. Neo4j Step
        if strategy in ("graph", "hybrid") and features.is_enabled("graph_search"):
            graph_plugins = capability_registry.get_plugins_supporting("supports_graph")
            for plug_name in graph_plugins:
                steps.append(ExecutionStep(
                    plugin_name=plug_name,
                    capability="supports_graph",
                    params={"query": intent.normalized_query, "depth": settings.GRAPH_TRAVERSAL_DEPTH, "filters": intent.filters},
                    estimated_cost=float(cost_weights.get("graph", 30))
                ))
                
        # 3. ChromaDB Step
        if strategy in ("vector", "hybrid") and features.is_enabled("vector_search"):
            vector_plugins = capability_registry.get_plugins_supporting("supports_vector")
            for plug_name in vector_plugins:
                steps.append(ExecutionStep(
                    plugin_name=plug_name,
                    capability="supports_vector",
                    params={"query": intent.normalized_query, "max_candidates": settings.RETRIEVAL_MAX_CANDIDATES, "filters": intent.filters},
                    estimated_cost=float(cost_weights.get("vector", 60))
                ))

        total_cost = sum(step.estimated_cost for step in steps)
        return ExecutionPlan(
            steps=steps,
            strategy=strategy,
            total_estimated_cost=total_cost
        )

    def _determine_default_strategy(self, primary_intent: str, profile: str) -> str:
        """
        Derives default strategy based on query intent and config profile.
        """
        if profile.lower() == "fast":
            return "sql"
        if profile.lower() == "offline":
            return "sql"
            
        if primary_intent == "identify":
            return "hybrid"
        if primary_intent == "recommend":
            return "hybrid"
        if primary_intent == "comparison":
            return "hybrid"
        if primary_intent == "qa":
            return "hybrid"
            
        return "sql"

# Export singleton planner instance
planner = CostAwarePlanner()
