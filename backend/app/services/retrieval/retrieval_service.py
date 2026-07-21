from app.services.base import BaseService
from app.retrieval.sdk import retrieval_client
from app.retrieval.disambiguation import ambiguity_resolver

class RetrievalService(BaseService):
    """
    Orchestrates logic for multi-store search queries, recommendations, movie identification, and trace explanations.
    """
    async def search_query(self, query: str, session_id: str | None, profile: str, experiment_id: str | None):
        with self.time_block("retrieval_search"):
            disambig = ambiguity_resolver.resolve_ambiguity(query)
            if disambig.is_ambiguous:
                return {
                    "status": "ambiguous",
                    "disambiguation": disambig.dict(),
                    "answer": "Your query is ambiguous. Please select one of the clarification candidates.",
                    "movies": []
                }
            
            response = await retrieval_client.search(
                query=query,
                session_id=session_id,
                profile=profile,
                experiment_id=experiment_id
            )
            return {
                "status": "success",
                "data": response.dict()
            }

    async def recommend_query(self, query: str, session_id: str | None, profile: str):
        with self.time_block("retrieval_recommend"):
            response = await retrieval_client.recommend(query, session_id, profile)
            return {"status": "success", "data": response.dict()}

    async def identify_query(self, query: str, session_id: str | None, profile: str):
        with self.time_block("retrieval_identify"):
            response = await retrieval_client.identify(query, session_id, profile)
            return {"status": "success", "data": response.dict()}

    def explain_query(self, trace_id: str):
        return retrieval_client.explain(trace_id)
