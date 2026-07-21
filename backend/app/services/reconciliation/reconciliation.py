from sqlalchemy.orm import Session
from typing import Dict, List, Any
from app.models.movie import Movie
from app.schemas.ontology import MovieOntologyInput, CastSchema, CrewSchema, SceneSchema, DialogueSchema, MusicSchema, AwardSchema, ReviewSchema
from app.services.graph import GraphService
from app.services.vector import VectorService
from app.core.interfaces.vector import BaseVectorStore
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.services.base import BaseService

class ReconciliationService(BaseService):
    """
    Orchestrates consistency audits and synchronization runs across Postgres,
    Neo4j, and ChromaDB.
    """
    def __init__(
        self,
        db: Session,
        graph_db: BaseKnowledgeGraph,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider
    ):
        super().__init__()
        self.db = db
        self.graph_db = graph_db
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.graph_service = GraphService(graph_db)
        self.vector_service = VectorService(vector_store, embedding_provider)

    def reconcile_all_movies(self) -> Dict[str, Any]:
        """
        Verify consistency of all movies across Postgres, Neo4j, and ChromaDB,
        and automatically repair any missing elements.
        """
        self.logger.info("Starting background reconciliation database check...")
        
        movies = self.db.query(Movie).all()
        checked_count = 0
        repaired_count = 0
        repaired_movies = []
        
        for m in movies:
            checked_count += 1
            needs_repair = False
            reasons = []
            
            # 1. Check Neo4j presence
            try:
                query = "MATCH (m:Movie {id: $movie_id}) RETURN count(m) as count"
                res = self.graph_db.execute_query(query, {"movie_id": m.tmdb_id})
                node_count = res[0].get("count", 0) if res else 0
                if node_count == 0:
                    needs_repair = True
                    reasons.append("Neo4j node missing")
            except Exception as e:
                self.logger.error(f"Reconciliation error checking Neo4j for {m.title}: {e}")
                
            # 2. Check ChromaDB presence
            try:
                if hasattr(self.vector_store, "client"):
                    collection = self.vector_store.client.get_collection("movie_overviews")
                    res = collection.get(where={"movie_id": m.tmdb_id})
                    doc_count = len(res.get("ids", [])) if res else 0
                    if doc_count == 0:
                        needs_repair = True
                        reasons.append("ChromaDB vectors missing")
            except Exception as e:
                self.logger.error(f"Reconciliation error checking ChromaDB for {m.title}: {e}")
                
            if needs_repair:
                self.logger.info(f"Reconciliation: Movie '{m.title}' (ID: {m.tmdb_id}) is INCONSISTENT. Reasons: {', '.join(reasons)}. Repairing...")
                try:
                    self.repair_movie(m)
                    repaired_count += 1
                    repaired_movies.append({"title": m.title, "tmdb_id": m.tmdb_id, "reasons": reasons})
                except Exception as e:
                    self.logger.exception(f"Reconciliation failed to repair movie '{m.title}': {e}")
                    
        self.logger.info(f"Reconciliation check complete. Checked: {checked_count}, Repaired: {repaired_count}")
        return {
            "status": "success",
            "checked_count": checked_count,
            "repaired_count": repaired_count,
            "repaired_movies": repaired_movies
        }

    def repair_movie(self, db_movie: Movie) -> None:
        """
        Rebuilds graph connections and vector indices for a movie using PostgreSQL data.
        """
        ontology_input = self.map_db_to_input(db_movie)
        
        # 1. Populate Neo4j Graph
        self.graph_service.populate_movie(ontology_input)
        
        # 2. Re-index Vectors in ChromaDB (Clear old vectors first)
        self._clear_chroma_vectors(db_movie.tmdb_id)
        self.vector_service.populate_movie(ontology_input)

    def _clear_chroma_vectors(self, movie_id: str) -> None:
        collections = ["movie_overviews", "characters", "scenes", "dialogues", "themes", "memory_cues", "visual_cues"]
        for col in collections:
            try:
                if hasattr(self.vector_store, "_get_collection"):
                    collection = self.vector_store._get_collection(col)
                    collection.delete(where={"movie_id": movie_id})
            except Exception as e:
                self.logger.warning(f"Could not clear Chroma collection '{col}' for ID {movie_id}: {e}")

    def map_db_to_input(self, db_movie: Movie) -> MovieOntologyInput:
        """
        Map a PostgreSQL Movie database model back to a MovieOntologyInput Pydantic model.
        """
        scenes_list = []
        for s in db_movie.scenes:
            dialogues_list = []
            for d in s.dialogues:
                dialogues_list.append(DialogueSchema(
                    character_name=d.speaker,
                    text=d.dialogue_text,
                    speaker=d.speaker,
                    listener=d.listener,
                    meaning=d.meaning,
                    emotional_tone=d.emotional_tone,
                    subtext=d.subtext,
                    confidence_score=d.confidence_score,
                    generated_by=d.generated_by,
                    generated_at=d.generated_at.isoformat() if d.generated_at else None,
                    source=d.source
                ))
            
            scenes_list.append(SceneSchema(
                description=s.summary,
                summary=s.summary,
                location=s.location,
                narrative_importance=s.importance,
                scene_type=s.scene_type,
                dialogues=dialogues_list,
                confidence_score=s.confidence_score,
                generated_by=s.generated_by,
                generated_at=s.generated_at.isoformat() if s.generated_at else None,
                source=s.source
            ))

        return MovieOntologyInput(
            title=db_movie.title,
            overview=db_movie.overview,
            release_year=db_movie.release_year,
            runtime=db_movie.runtime,
            language=db_movie.language,
            country=db_movie.country,
            tmdb_id=db_movie.tmdb_id,
            imdb_id=db_movie.imdb_id,
            wikidata_id=db_movie.wikidata_id,
            tvdb_id=db_movie.tvdb_id,
            original_title=db_movie.original_title,
            release_date=db_movie.release_date.isoformat() if db_movie.release_date else None,
            budget=db_movie.budget,
            revenue=db_movie.revenue,
            tagline=db_movie.tagline,
            status=db_movie.status,
            adult=db_movie.adult,
            popularity=db_movie.popularity,
            vote_average=db_movie.vote_average,
            vote_count=db_movie.vote_count,
            genres=[g.name for g in db_movie.genres],
            themes=[t.name for t in db_movie.themes],
            emotions=[e.name for e in db_movie.emotions],
            moods=[m.name for m in db_movie.moods],
            keywords=[k.name for k in db_movie.keywords],
            cast=[
                CastSchema(
                    character_name=c.character_name,
                    person_name=c.person.name if c.person else "Unknown",
                    external_person_id=c.person.external_person_id if c.person else "",
                    aliases=c.aliases or [],
                    biography=c.biography,
                    importance=c.importance,
                    relationships=c.relationships or [],
                    personality_traits=c.personality_traits or [],
                    motivations=c.motivations or [],
                    arc=c.arc,
                    confidence_score=c.confidence_score,
                    generated_by=c.generated_by,
                    generated_at=c.generated_at.isoformat() if c.generated_at else None,
                    source=c.source
                ) for c in db_movie.cast
            ],
            crew=[
                CrewSchema(
                    person_name=cr.person.name if cr.person else "Unknown",
                    external_person_id=cr.person.external_person_id if cr.person else "",
                    job=cr.job,
                    department=cr.department
                ) for cr in db_movie.crew
            ],
            scenes=scenes_list,
            memory_cues=[mc.description for mc in db_movie.memory_cues],
            visual_cues=[vc.description for vc in db_movie.visual_cues],
            music=[
                MusicSchema(
                    track_name=mu.track_name,
                    artist=mu.artist,
                    type=mu.type
                ) for mu in db_movie.music
            ],
            awards=[
                AwardSchema(
                    name=aw.name,
                    category=aw.category,
                    year=aw.year,
                    winner=aw.winner
                ) for aw in db_movie.awards
            ],
            reviews=[
                ReviewSchema(
                    critic_name=rev.critic_name,
                    rating=rev.rating,
                    text=rev.text
                ) for rev in db_movie.reviews
            ],
            twists=[t.description for t in db_movie.twists],
            conflicts=[co.description for co in db_movie.conflicts],
            subplots=[sb.description for sb in db_movie.subplots],
            confidence_score=db_movie.confidence_score,
            generated_by=db_movie.generated_by,
            generated_at=db_movie.generated_at.isoformat() if db_movie.generated_at else None,
            source=db_movie.source
        )
