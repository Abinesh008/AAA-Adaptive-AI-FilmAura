from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger("app.recommendation.policies")

class BasePolicyFilter(ABC):
    """
    Abstract base filter class for policy rules.
    """
    @abstractmethod
    def filter(self, candidates: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

class AgeContentPolicy(BasePolicyFilter):
    """
    Filters adult or mature content if profile setting restricts it.
    """
    def filter(self, candidates: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        is_child_profile = context.get("is_child_profile", False)
        if not is_child_profile:
            return candidates

        filtered: List[Dict[str, Any]] = []
        for cand in candidates:
            # Safe default if adult indicator is missing
            is_adult = cand.get("adult", False)
            if not is_adult:
                filtered.append(cand)
            else:
                logger.info(f"Filtering movie {cand.get('movie_id')} due to child age policy restrictions.")
        return filtered

class RegionalPolicy(BasePolicyFilter):
    """
    Filters movies that are not licensed or available in user's geographic region.
    """
    def filter(self, candidates: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        target_region = context.get("region")
        if not target_region:
            return candidates

        filtered: List[Dict[str, Any]] = []
        for cand in candidates:
            # Fetch movie regional availability lists (mocked as country codes)
            available_countries = cand.get("available_countries", [])
            # If not defined, assume globally licensed/available
            if not available_countries or target_region in available_countries:
                filtered.append(cand)
            else:
                logger.info(f"Filtering movie {cand.get('movie_id')} due to regional licensing policy in {target_region}.")
        return filtered

class SubscriptionPolicy(BasePolicyFilter):
    """
    Restricts premium tier films if user only holds standard/free memberships.
    """
    def filter(self, candidates: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        user_tier = context.get("subscription_tier", "free").lower()
        if user_tier == "premium":
            return candidates

        filtered: List[Dict[str, Any]] = []
        for cand in candidates:
            is_premium_only = cand.get("premium_only", False)
            if not is_premium_only or user_tier == "premium":
                filtered.append(cand)
            else:
                logger.info(f"Filtering movie {cand.get('movie_id')} due to premium subscription requirements.")
        return filtered

class RecommendationPolicyChain:
    """
    Orchestrator pipeline executing registered policy filters sequentially.
    """
    def __init__(self):
        self._filters: List[BasePolicyFilter] = [
            AgeContentPolicy(),
            RegionalPolicy(),
            SubscriptionPolicy()
        ]

    def execute(self, candidates: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        logger.info(f"Running policy chain on {len(candidates)} candidates.")
        current_candidates = candidates
        for filter_rule in self._filters:
            current_candidates = filter_rule.filter(current_candidates, context)
        return current_candidates

# Export policy chain instance
policy_chain = RecommendationPolicyChain()
