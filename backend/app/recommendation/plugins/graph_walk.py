import sqlalchemy as sa
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.recommendation.interfaces.plugin import BaseRecommendationPlugin
from app.models.movie import UserInteractionHistory, Movie, movie_genres
from app.retrieval.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.recommendation.plugins.graph_walk")

class GraphWalkPlugin(BaseRecommendationPlugin):
    """
    Personalized Graph Walk recommendation candidate generator.
    Traverses Neo4j graph nodes of direct connections, falls back to SQL attribute overlap walks.
    """
    @property
    def name(self) -> str:
        return "graph_walk"

    async def generate_candidates(
        self, 
        user_id: str, 
        limit: int, 
        db: Session, 
        trace: QueryTrace
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating graph-walk candidates for user: {user_id}")
        trace.record_start("plugin_graph_walk")
        
        candidates: List[Dict[str, Any]] = []
        
        # 1. Attempt Neo4j traversal (Graph database walk)
        try:
            # Import neo4j dependency lazily
            from app.database.session import get_neo4j_driver
            driver = get_neo4j_driver()
            if driver:
                with driver.session() as session:
                    cypher_query = """
                    MATCH (u:User {id: $user_id})-[:WATCHED|RATED]->(m:Movie)-[:IN_GENRE|DIRECTED_BY]-(attr)-(other:Movie)
                    WHERE NOT (u)-[:WATCHED|RATED]->(other)
                    RETURN other.tmdb_id AS tmdb_id, count(attr) AS overlap_score
                    ORDER BY overlap_score DESC
                    LIMIT $limit
                    """
                    result = session.run(cypher_query, user_id=user_id, limit=limit)
                    for record in result:
                        tmdb_id = record["tmdb_id"]
                        overlap = record["overlap_score"]
                        # Calibrate overlap count into normalized score [0.0, 1.0]
                        normalized_score = min(1.0, max(0.0, overlap / 10.0))
                        candidates.append({
                            "movie_id": int(tmdb_id),
                            "score": round(normalized_score, 3),
                            "provenance_reason": f"Discovered via graph paths overlapping {overlap} shared attributes (genres/directors)"
                        })
                        
                    if candidates:
                        logger.info(f"Retrieved {len(candidates)} candidates from Neo4j.")
                        trace.record_end("plugin_graph_walk")
                        return candidates
        except Exception as e:
            logger.warn(f"Neo4j traversal failed: {str(e)}. Falling back to SQL relational attributes walk.")

        # 2. SQL Relational Database overlap walk fallback
        try:
            # Fetch user's interacted movies
            user_interactions = db.query(UserInteractionHistory.movie_id, UserInteractionHistory.interaction_type).filter(
                UserInteractionHistory.user_id == user_id
            ).all()
            
            interacted_movie_ids = {str(i[0]) for i in user_interactions}
            liked_movie_ids = [str(i[0]) for i in user_interactions if i[1] in ("rating", "bookmark")]
            
            if not liked_movie_ids:
                logger.info("User has no liked movies recorded. Graph walk returning zero candidates.")
                trace.record_end("plugin_graph_walk")
                return []

            # Find genres of liked movies
            liked_movie_details = db.query(Movie).filter(Movie.tmdb_id.in_(liked_movie_ids)).all()
            liked_genre_ids = []
            for m in liked_movie_details:
                liked_genre_ids.extend([g.id for g in m.genres])
                
            if not liked_genre_ids:
                logger.info("Liked movies have no genre associations. Graph walk fallback returning zero.")
                trace.record_end("plugin_graph_walk")
                return []

            # Query movies that share these genres and have NOT been interacted with
            fallback_query = db.query(
                movie_genres.c.movie_id,
                Movie.tmdb_id
            ).join(
                Movie, Movie.id == movie_genres.c.movie_id
            ).filter(
                and_(
                    movie_genres.c.genre_id.in_(liked_genre_ids),
                    ~Movie.tmdb_id.in_(interacted_movie_ids)
                )
            ).all()

            # Count frequency of overlaps
            movie_overlaps: Dict[int, int] = {}
            for m_id, tmdb_id in fallback_query:
                try:
                    t_id = int(tmdb_id)
                    movie_overlaps[t_id] = movie_overlaps.get(t_id, 0) + 1
                except (ValueError, TypeError):
                    continue

            for t_id, overlap_count in movie_overlaps.items():
                # Calibrate overlap count to [0.0, 1.0] scale
                normalized_score = min(0.9, max(0.1, overlap_count / 10.0))
                candidates.append({
                    "movie_id": t_id,
                    "score": round(normalized_score, 3),
                    "provenance_reason": f"Shares {overlap_count} genres with your bookmarked movies"
                })

            candidates.sort(key=lambda x: x["score"], reverse=True)
            candidates = candidates[:limit]

        except Exception as e:
            logger.error(f"SQL Relational fallback walk failed: {str(e)}")

        trace.record_end("plugin_graph_walk")
        return candidates

# Instantiate plugin singleton
graph_walk_plugin = GraphWalkPlugin()
