from typing import List, Dict, Any
from app.api.deps import get_knowledge_graph
from app.retrieval.interfaces.plugin import BaseRetrievalPlugin
from app.retrieval.contracts.contract import ExecutionStep, RetrievalResult, ProvenanceChain
from app.retrieval.query.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.retrieval.plugins.neo4j")

class Neo4jRetrievalPlugin(BaseRetrievalPlugin):
    """
    Plugin running Cypher traversal queries on Neo4j Graph Database.
    """
    @property
    def name(self) -> str:
        return "neo4j"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "supports_graph": True,
            "supports_graph_reasoning": True,
            "supports_similarity": True
        }

    @property
    def dependencies(self) -> List[str]:
        return ["neo4j"]

    async def search(self, step: ExecutionStep, trace: QueryTrace) -> List[RetrievalResult]:
        graph_db = get_knowledge_graph()
        query_str = step.params.get("query", "")
        filters = step.params.get("filters", {})
        
        # Build standard Cypher queries based on intent and filter states
        cypher = ""
        params: Dict[str, Any] = {}
        
        if "director" in filters:
            cypher = (
                "MATCH (m:Movie)-[:DIRECTED_BY]->(p:Person) "
                "WHERE p.name =~ $director "
                "RETURN m.id AS id, m.title AS title, m.overview AS overview, m.year AS year, p.name AS matched_entity"
            )
            params["director"] = f"(?i).*{filters['director']}.*"
        elif "similar_to" in filters:
            cypher = (
                "MATCH (target:Movie {id: $target_id})-[:HAS_THEME|HAS_GENRE]->(common)<-[:HAS_THEME|HAS_GENRE]-(m:Movie) "
                "RETURN m.id AS id, m.title AS title, m.overview AS overview, m.year AS year, count(common) AS strength, common.name AS matched_entity "
                "ORDER BY strength DESC"
            )
            params["target_id"] = int(filters["similar_to"])
        elif "movie_id" in filters:
            cypher = (
                "MATCH (m:Movie {id: $movie_id}) "
                "RETURN m.id AS id, m.title AS title, m.overview AS overview, m.year AS year, 'exact_match' AS matched_entity"
            )
            params["movie_id"] = int(filters["movie_id"])
        elif query_str:
            # Fuzzy match keywords, genres or themes
            cypher = (
                "MATCH (m:Movie) "
                "WHERE m.title =~ $query OR m.overview =~ $query "
                "RETURN m.id AS id, m.title AS title, m.overview AS overview, m.year AS year, 'keyword_match' AS matched_entity"
            )
            params["query"] = f"(?i).*{query_str}.*"
        else:
            # Fallback limit check
            cypher = "MATCH (m:Movie) RETURN m.id AS id, m.title AS title, m.overview AS overview, m.year AS year, 'all' AS matched_entity LIMIT 5"
            
        try:
            records = graph_db.execute_query(cypher, params)
            retrieval_results = []
            
            for rec in records:
                m_id = rec.get("id")
                if m_id is None:
                    continue
                    
                title = rec.get("title", f"Movie {m_id}")
                overview = rec.get("overview", "")
                year = rec.get("year", 0)
                matched_entity = rec.get("matched_entity", "unknown")
                
                prov = ProvenanceChain(
                    database="neo4j",
                    table_or_label="Movie",
                    node_id_or_vector_id=str(m_id),
                    query_executed=cypher,
                    confidence_contribution=0.85
                )
                
                retval = RetrievalResult(
                    source="neo4j",
                    entity_type="movie",
                    entity_id=str(m_id),
                    score=1.0,
                    confidence=0.85,
                    provenance=prov,
                    metadata={
                        "title": title,
                        "year": year,
                        "matched_relationship": matched_entity
                    },
                    evidence={"overview": overview, "cypher_path": f"(:Movie {{id: {m_id}}})-[:MATCHED]->({matched_entity})"}
                )
                retrieval_results.append(retval)
                
            return retrieval_results
        except Exception as e:
            logger.error(f"Neo4j Cypher query execution failed: {str(e)}")
            raise e
