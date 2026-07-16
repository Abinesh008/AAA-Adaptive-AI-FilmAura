from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, date
from app.ingestion.base import BaseMovieDataProvider
from app.ingestion.cleaning import clean_movie_data
from app.ingestion.validation import validate_movie_ontology
from app.ingestion.enrichment import MovieEnricher
from app.api import deps
from app.models.movie import *
from app.services.graph_service import GraphService
from app.services.vector_service import VectorService
from app.core.interfaces.vector import BaseVectorStore
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.logging import get_logger

logger = get_logger("app.ingestion.pipeline")

class MovieIngestionPipeline:
    """
    Core coordinator orchestrating movie seeding across PostgreSQL, Neo4j, and ChromaDB.
    Consumes the abstract BaseMovieDataProvider interface.
    """
    def __init__(
        self,
        db: Session,
        graph_db: BaseKnowledgeGraph,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        provider: BaseMovieDataProvider
    ):
        self.db = db
        self.provider = provider
        self.graph_db = graph_db
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        
        # Initialize sub-services
        self.graph_service = GraphService(graph_db)
        self.vector_service = VectorService(vector_store, embedding_provider)
        
        # Initialize graph constraints/schemas
        try:
            self.graph_service.initialize_schema()
        except Exception as e:
            logger.warning(f"Failed to pre-initialize Neo4j schemas: {e}")

    def ingest_movie_by_id(self, movie_id: str, run_enrichment: bool = True) -> Movie:
        """
        Trigger complete idempotent ingestion cycle for a single movie by external ID.
        """
        logger.info(f"==> Starting base ingestion cycle for movie ID: {movie_id}")
        
        # 1. Fetch raw data from provider
        raw_movie_data = self.provider.fetch_movie_by_id(movie_id)
        
        # 2. Clean and normalize payload data
        cleaned_movie = clean_movie_data(raw_movie_data)
        
        # 3. Validate the movie payload before DB insertions
        validation_errors = validate_movie_ontology(cleaned_movie)
        if validation_errors:
            logger.warning(f"Validation warnings/errors for ID {movie_id}: {'; '.join(validation_errors)}")
            # Filter fatal schema errors to block execution if critical
            fatal_errors = [e for e in validation_errors if "Validation Error:" in e]
            if fatal_errors:
                raise ValueError(f"Ingestion aborted due to validation failures: {'; '.join(fatal_errors)}")

        # 4. Write relational schema to PostgreSQL (idempotent check-and-update)
        db_movie = self._save_to_postgresql(cleaned_movie)
        
        # 5. Populate Knowledge Graph in Neo4j (idempotent MERGE queries)
        try:
            self.graph_service.populate_movie(cleaned_movie)
        except Exception as e:
            logger.error(f"Failed to populate Neo4j graph for movie {cleaned_movie.title}: {e}")
            
        # 6. Populate Vector embeddings in ChromaDB (clear old vectors first)
        try:
            self._clear_chroma_vectors(cleaned_movie.tmdb_id)
            self.vector_service.populate_movie(cleaned_movie)
        except Exception as e:
            logger.error(f"Failed to populate ChromaDB vectors for movie {cleaned_movie.title}: {e}")
            
        logger.info(f"==> Base Ingestion complete for '{cleaned_movie.title}' (ID: {cleaned_movie.tmdb_id}). Movie is fully usable.")

        # 7. Asynchronous/Background AI Enrichment
        if run_enrichment:
            self._run_asynchronous_enrichment(cleaned_movie)

        return db_movie

    def ingest_popular_movies(self, limit: int = 20, run_enrichment: bool = True) -> List[Movie]:
        """
        Ingest a batch of popular movies.
        """
        logger.info(f"==> Initiating batch popular movie ingestion (limit={limit})")
        popular_movies = self.provider.fetch_popular_movies(limit=limit)
        
        ingested_movies = []
        for index, movie_input in enumerate(popular_movies):
            try:
                logger.info(f"Ingesting batch movie {index + 1}/{len(popular_movies)}: '{movie_input.title}'")
                db_movie = self.ingest_movie_by_id(movie_input.tmdb_id, run_enrichment=run_enrichment)
                ingested_movies.append(db_movie)
            except Exception as e:
                logger.exception(f"Failed to ingest movie '{movie_input.title}' in batch: {e}")
                
        logger.info(f"==> Batch popular movie ingestion complete. Total ingested: {len(ingested_movies)}")
        return ingested_movies

    def _clear_chroma_vectors(self, movie_id: str) -> None:
        """
        Clears existing documents for a movie from all target collections in Chroma.
        """
        collections = ["movie_overviews", "characters", "scenes", "dialogues", "themes", "memory_cues", "visual_cues"]
        for col in collections:
            try:
                # Retrieve the raw collection to utilize native where-clause deletion
                if hasattr(self.vector_store, "_get_collection"):
                    collection = self.vector_store._get_collection(col)
                    collection.delete(where={"movie_id": movie_id})
                    logger.debug(f"Cleared existing vectors for ID {movie_id} in collection '{col}'")
            except Exception as e:
                logger.warning(f"Could not clear Chroma collection '{col}' for ID {movie_id}: {e}")

def _parse_dt(dt_val):
    if not dt_val:
        return datetime.utcnow()
    if isinstance(dt_val, datetime):
        return dt_val
    try:
        return datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
    except Exception:
        return datetime.utcnow()

class MovieIngestionPipeline:
    """
    Core coordinator orchestrating movie seeding across PostgreSQL, Neo4j, and ChromaDB.
    Consumes the abstract BaseMovieDataProvider interface.
    """
    def __init__(
        self,
        db: Session,
        graph_db: BaseKnowledgeGraph,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        provider: BaseMovieDataProvider
    ):
        self.db = db
        self.provider = provider
        self.graph_db = graph_db
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        
        # Initialize sub-services
        self.graph_service = GraphService(graph_db)
        self.vector_service = VectorService(vector_store, embedding_provider)
        
        # Initialize graph constraints/schemas
        try:
            self.graph_service.initialize_schema()
        except Exception as e:
            logger.warning(f"Failed to pre-initialize Neo4j schemas: {e}")

    def ingest_movie_by_id(self, movie_id: str, run_enrichment: bool = True) -> Movie:
        """
        Trigger complete idempotent ingestion cycle for a single movie by external ID.
        """
        logger.info(f"==> Starting base ingestion cycle for movie ID: {movie_id}")
        
        # 1. Fetch raw data from provider
        raw_movie_data = self.provider.fetch_movie_by_id(movie_id)
        
        # 2. Clean and normalize payload data
        cleaned_movie = clean_movie_data(raw_movie_data)
        
        # 3. Validate the movie payload before DB insertions
        validation_errors = validate_movie_ontology(cleaned_movie)
        if validation_errors:
            logger.warning(f"Validation warnings/errors for ID {movie_id}: {'; '.join(validation_errors)}")
            # Filter fatal schema errors to block execution if critical
            fatal_errors = [e for e in validation_errors if "Validation Error:" in e]
            if fatal_errors:
                raise ValueError(f"Ingestion aborted due to validation failures: {'; '.join(fatal_errors)}")

        # 4. Write relational schema to PostgreSQL (idempotent check-and-update)
        db_movie = self._save_to_postgresql(cleaned_movie)
        
        # 5. Populate Knowledge Graph in Neo4j (idempotent MERGE queries)
        try:
            self.graph_service.populate_movie(cleaned_movie)
        except Exception as e:
            logger.error(f"Failed to populate Neo4j graph for movie {cleaned_movie.title}: {e}")
            
        # 6. Populate Vector embeddings in ChromaDB (clear old vectors first)
        try:
            self._clear_chroma_vectors(cleaned_movie.tmdb_id)
            self.vector_service.populate_movie(cleaned_movie)
        except Exception as e:
            logger.error(f"Failed to populate ChromaDB vectors for movie {cleaned_movie.title}: {e}")
            
        logger.info(f"==> Base Ingestion complete for '{cleaned_movie.title}' (ID: {cleaned_movie.tmdb_id}). Movie is fully usable.")

        # 7. Asynchronous/Background AI Enrichment
        if run_enrichment:
            self._run_asynchronous_enrichment(cleaned_movie)

        return db_movie

    def ingest_popular_movies(self, limit: int = 20, run_enrichment: bool = True) -> List[Movie]:
        """
        Ingest a batch of popular movies.
        """
        logger.info(f"==> Initiating batch popular movie ingestion (limit={limit})")
        popular_movies = self.provider.fetch_popular_movies(limit=limit)
        
        ingested_movies = []
        for index, movie_input in enumerate(popular_movies):
            try:
                logger.info(f"Ingesting batch movie {index + 1}/{len(popular_movies)}: '{movie_input.title}'")
                db_movie = self.ingest_movie_by_id(movie_input.tmdb_id, run_enrichment=run_enrichment)
                ingested_movies.append(db_movie)
            except Exception as e:
                logger.exception(f"Failed to ingest movie '{movie_input.title}' in batch: {e}")
                
        logger.info(f"==> Batch popular movie ingestion complete. Total ingested: {len(ingested_movies)}")
        return ingested_movies

    def _clear_chroma_vectors(self, movie_id: str) -> None:
        """
        Clears existing documents for a movie from all target collections in Chroma.
        """
        collections = ["movie_overviews", "characters", "scenes", "dialogues", "themes", "memory_cues", "visual_cues"]
        for col in collections:
            try:
                # Retrieve the raw collection to utilize native where-clause deletion
                if hasattr(self.vector_store, "_get_collection"):
                    collection = self.vector_store._get_collection(col)
                    collection.delete(where={"movie_id": movie_id})
                    logger.debug(f"Cleared existing vectors for ID {movie_id} in collection '{col}'")
            except Exception as e:
                logger.warning(f"Could not clear Chroma collection '{col}' for ID {movie_id}: {e}")

    def _run_asynchronous_enrichment(self, movie: MovieOntologyInput) -> None:
        """
        Triggers the semantic AI enrichment stage.
        Runs in a separate task context, catching errors to avoid affecting base usability.
        """
        logger.info(f"Triggering asynchronous AI enrichment stage for '{movie.title}'...")
        try:
            llm = deps.get_llm_provider()
            enricher = MovieEnricher(llm)
            enriched_movie = enricher.enrich_movie(movie)
            
            # Inject AI enrichment metadata
            gen_by = llm.provider_name if hasattr(llm, "provider_name") else "mock"
            gen_at = datetime.utcnow().isoformat()
            
            enriched_movie.source = "llm"
            enriched_movie.confidence_score = 0.90
            enriched_movie.generated_by = gen_by
            enriched_movie.generated_at = gen_at
            
            for scene in enriched_movie.scenes:
                scene.source = "llm"
                scene.confidence_score = 0.90
                scene.generated_by = gen_by
                scene.generated_at = gen_at
                for d in scene.dialogues:
                    d.source = "llm"
                    d.confidence_score = 0.90
                    d.generated_by = gen_by
                    d.generated_at = gen_at
            
            for cast_member in enriched_movie.cast:
                if cast_member.personality_traits or cast_member.motivations or cast_member.arc:
                    cast_member.source = "llm"
                    cast_member.confidence_score = 0.85
                    cast_member.generated_by = gen_by
                    cast_member.generated_at = gen_at
            
            logger.info(f"Saving AI enriched attributes back into PostgreSQL for '{movie.title}'...")
            self._save_to_postgresql(enriched_movie)
            
            logger.info(f"Saving AI enriched attributes back into Neo4j for '{movie.title}'...")
            self.graph_service.populate_movie(enriched_movie)
            
            logger.info(f"Saving AI enriched attributes back into ChromaDB for '{movie.title}'...")
            self._clear_chroma_vectors(enriched_movie.tmdb_id)
            self.vector_service.populate_movie(enriched_movie)
            
            logger.info(f"AI enrichment stage completed successfully for '{movie.title}'")
        except Exception as e:
            logger.error(f"AI enrichment stage failed for '{movie.title}': {e}. Movie remains fully active with base metadata.")

    def _save_to_postgresql(self, movie: MovieOntologyInput) -> Movie:
        """
        Write/update movie ontology schema relational records into PostgreSQL.
        Guarantees idempotence via upsert updates.
        """
        logger.info(f"Saving '{movie.title}' to PostgreSQL database...")
        
        # Check if movie already exists
        db_movie = self.db.query(Movie).filter(Movie.tmdb_id == movie.tmdb_id).first()
        
        # Parse release date
        release_date = None
        if movie.release_date:
            try:
                release_date = datetime.strptime(movie.release_date, "%Y-%m-%d").date()
            except ValueError:
                pass

        if not db_movie:
            db_movie = Movie(
                title=movie.title,
                overview=movie.overview,
                release_year=movie.release_year,
                runtime=movie.runtime,
                language=movie.language,
                country=movie.country,
                tmdb_id=movie.tmdb_id,
                provider_name="tmdb",
                imdb_id=movie.imdb_id,
                wikidata_id=movie.wikidata_id,
                tvdb_id=movie.tvdb_id,
                original_title=movie.original_title,
                release_date=release_date,
                budget=movie.budget,
                revenue=movie.revenue,
                tagline=movie.tagline,
                status=movie.status,
                adult=movie.adult,
                popularity=movie.popularity,
                vote_average=movie.vote_average,
                vote_count=movie.vote_count,
                plot=movie.plot,
                plot_summary=movie.plot_summary,
                beginning=movie.beginning,
                middle=movie.middle,
                climax=movie.climax,
                ending=movie.ending,
                ending_type=movie.ending_type,
                timeline=movie.timeline,
                # Metadata
                confidence_score=movie.confidence_score,
                generated_by=movie.generated_by,
                generated_at=_parse_dt(movie.generated_at),
                source=movie.source
            )
            self.db.add(db_movie)
            self.db.flush()  # Populates db_movie.id
        else:
            # Update core attributes (idempotent update)
            db_movie.title = movie.title
            db_movie.overview = movie.overview
            db_movie.release_year = movie.release_year
            db_movie.runtime = movie.runtime
            db_movie.language = movie.language
            db_movie.country = movie.country
            db_movie.imdb_id = movie.imdb_id
            db_movie.wikidata_id = movie.wikidata_id
            db_movie.tvdb_id = movie.tvdb_id
            db_movie.original_title = movie.original_title
            db_movie.release_date = release_date
            db_movie.budget = movie.budget
            db_movie.revenue = movie.revenue
            db_movie.tagline = movie.tagline
            db_movie.status = movie.status
            db_movie.adult = movie.adult
            db_movie.popularity = movie.popularity
            db_movie.vote_average = movie.vote_average
            db_movie.vote_count = movie.vote_count
            db_movie.plot = movie.plot
            db_movie.plot_summary = movie.plot_summary
            db_movie.beginning = movie.beginning
            db_movie.middle = movie.middle
            db_movie.climax = movie.climax
            db_movie.ending = movie.ending
            db_movie.ending_type = movie.ending_type
            db_movie.timeline = movie.timeline
            db_movie.last_synced_at = datetime.utcnow()
            
            # Update metadata fields
            db_movie.confidence_score = movie.confidence_score
            db_movie.generated_by = movie.generated_by
            db_movie.generated_at = _parse_dt(movie.generated_at)
            db_movie.source = movie.source
            
            # Clear child relational links to rewrite cleanly on sync updates
            self.db.query(MovieCast).filter(MovieCast.movie_id == db_movie.id).delete()
            self.db.query(MovieCrew).filter(MovieCrew.movie_id == db_movie.id).delete()
            self.db.query(Scene).filter(Scene.movie_id == db_movie.id).delete()
            self.db.query(VisualCue).filter(VisualCue.movie_id == db_movie.id).delete()
            self.db.query(MemoryCue).filter(MemoryCue.movie_id == db_movie.id).delete()
            self.db.query(Music).filter(Music.movie_id == db_movie.id).delete()
            self.db.query(Award).filter(Award.movie_id == db_movie.id).delete()
            self.db.query(Review).filter(Review.movie_id == db_movie.id).delete()
            self.db.query(MovieTwist).filter(MovieTwist.movie_id == db_movie.id).delete()
            self.db.query(MovieConflict).filter(MovieConflict.movie_id == db_movie.id).delete()
            self.db.query(MovieSubplot).filter(MovieSubplot.movie_id == db_movie.id).delete()
            self.db.query(MovieRelationship).filter((MovieRelationship.from_movie_id == db_movie.id) | (MovieRelationship.to_movie_id == db_movie.id)).delete()
            
            db_movie.genres.clear()
            db_movie.keywords.clear()
            db_movie.studios.clear()
            db_movie.themes.clear()
            db_movie.emotions.clear()
            db_movie.moods.clear()
            db_movie.streaming_providers.clear()
            self.db.flush()

        # 1. Map Franchise
        if movie.franchise:
            f = self.db.query(Franchise).filter(Franchise.name == movie.franchise).first()
            if not f:
                f = Franchise(name=movie.franchise)
                self.db.add(f)
                self.db.flush()
            db_movie.franchise_id = f.id
        else:
            db_movie.franchise_id = None

        # 2. Map Genres
        genre_objects = []
        for genre_name in movie.genres:
            g = self.db.query(Genre).filter(Genre.name == genre_name).first()
            if not g:
                g = Genre(name=genre_name)
                self.db.add(g)
                self.db.flush()
            genre_objects.append(g)
        db_movie.genres = genre_objects

        # 3. Map Keywords
        keyword_objects = []
        for kw_name in movie.keywords:
            k = self.db.query(Keyword).filter(Keyword.name == kw_name).first()
            if not k:
                k = Keyword(name=kw_name)
                self.db.add(k)
                self.db.flush()
            keyword_objects.append(k)
        db_movie.keywords = keyword_objects

        # 4. Map Studios
        studio_objects = []
        for s_name in movie.studios:
            s = self.db.query(Studio).filter(Studio.name == s_name).first()
            if not s:
                s = Studio(name=s_name)
                self.db.add(s)
                self.db.flush()
            studio_objects.append(s)
        db_movie.studios = studio_objects

        # 5. Map Themes
        theme_objects = []
        for t_name in movie.themes:
            t = self.db.query(Theme).filter(Theme.name == t_name).first()
            if not t:
                t = Theme(name=t_name)
                self.db.add(t)
                self.db.flush()
            theme_objects.append(t)
        db_movie.themes = theme_objects

        # 6. Map Emotions
        emotion_objects = []
        for e_name in movie.emotions:
            e = self.db.query(Emotion).filter(Emotion.name == e_name).first()
            if not e:
                e = Emotion(name=e_name)
                self.db.add(e)
                self.db.flush()
            emotion_objects.append(e)
        db_movie.emotions = emotion_objects

        # 7. Map Moods
        mood_objects = []
        for m_name in movie.moods:
            m = self.db.query(Mood).filter(Mood.name == m_name).first()
            if not m:
                m = Mood(name=m_name)
                self.db.add(m)
                self.db.flush()
            mood_objects.append(m)
        db_movie.moods = mood_objects

        # 8. Map Streaming Providers
        provider_objects = []
        for sp in movie.streaming_providers:
            provider_name = sp.get("name")
            if provider_name:
                p = self.db.query(StreamingProvider).filter(
                    StreamingProvider.name == provider_name,
                    StreamingProvider.region == sp.get("region")
                ).first()
                if not p:
                    p = StreamingProvider(
                        name=provider_name,
                        availability=sp.get("availability"),
                        region=sp.get("region")
                    )
                    self.db.add(p)
                    self.db.flush()
                provider_objects.append(p)
        db_movie.streaming_providers = provider_objects

        # 9. Map Cast (Actors) with character traits
        for cast_member in movie.cast:
            person = self.db.query(Person).filter(Person.external_person_id == cast_member.external_person_id).first()
            if not person:
                person = Person(
                    name=cast_member.person_name,
                    external_person_id=cast_member.external_person_id,
                    provider_name="tmdb"
                )
                self.db.add(person)
                self.db.flush()
                
            cast_assoc = MovieCast(
                movie_id=db_movie.id,
                person_id=person.id,
                character_name=cast_member.character_name,
                aliases=cast_member.aliases,
                biography=cast_member.biography,
                importance=cast_member.importance,
                relationships=cast_member.relationships,
                personality_traits=cast_member.personality_traits,
                motivations=cast_member.motivations,
                arc=cast_member.arc,
                # Metadata
                confidence_score=cast_member.confidence_score,
                generated_by=cast_member.generated_by,
                generated_at=_parse_dt(cast_member.generated_at),
                source=cast_member.source
            )
            self.db.add(cast_assoc)

        # 10. Map Crew
        for crew_member in movie.crew:
            person = self.db.query(Person).filter(Person.external_person_id == crew_member.external_person_id).first()
            if not person:
                person = Person(
                    name=crew_member.person_name,
                    external_person_id=crew_member.external_person_id,
                    provider_name="tmdb"
                )
                self.db.add(person)
                self.db.flush()
                
            crew_assoc = MovieCrew(
                movie_id=db_movie.id,
                person_id=person.id,
                job=crew_member.job,
                department=crew_member.department
            )
            self.db.add(crew_assoc)

        # 11. Map Scenes and Dialogues
        for idx, scene in enumerate(movie.scenes):
            scene_obj = Scene(
                movie_id=db_movie.id,
                scene_index=idx,
                summary=scene.summary or scene.description,
                location=scene.location,
                importance=scene.narrative_importance,
                scene_type=scene.scene_type,
                # Metadata
                confidence_score=scene.confidence_score,
                generated_by=scene.generated_by,
                generated_at=_parse_dt(scene.generated_at),
                source=scene.source
            )
            self.db.add(scene_obj)
            self.db.flush()  # Populates scene_obj.id
            
            # Map scene dialogues
            for d in scene.dialogues:
                dialogue_obj = Dialogue(
                    scene_id=scene_obj.id,
                    speaker=d.speaker or d.character_name,
                    listener=d.listener,
                    dialogue_text=d.text,
                    meaning=d.meaning,
                    emotional_tone=d.emotional_tone,
                    subtext=d.subtext,
                    # Metadata
                    confidence_score=d.confidence_score,
                    generated_by=d.generated_by,
                    generated_at=_parse_dt(d.generated_at),
                    source=d.source
                )
                self.db.add(dialogue_obj)

        # 12. Map Visual Cues
        for vc in movie.visual_cues:
            # We can classify cue_type based on prefix heuristics or default
            cue_type = "motif"
            desc_lower = vc.lower()
            if "palette" in desc_lower or "color" in desc_lower:
                cue_type = "palette"
            elif "lighting" in desc_lower:
                cue_type = "lighting"
            elif "camera" in desc_lower or "shot" in desc_lower:
                cue_type = "camera"
            elif "symbol" in desc_lower:
                cue_type = "symbolism"
                
            vc_obj = VisualCue(
                movie_id=db_movie.id,
                description=vc,
                cue_type=cue_type,
                # Metadata
                confidence_score=movie.confidence_score,
                generated_by=movie.generated_by,
                generated_at=_parse_dt(movie.generated_at),
                source=movie.source
            )
            self.db.add(vc_obj)

        # 13. Map Memory Cues
        for mc in movie.memory_cues:
            mc_obj = MemoryCue(
                movie_id=db_movie.id,
                description=mc,
                # Metadata
                confidence_score=movie.confidence_score,
                generated_by=movie.generated_by,
                generated_at=_parse_dt(movie.generated_at),
                source=movie.source
            )
            self.db.add(mc_obj)

        # 14. Map Music tracks
        for m in movie.music:
            m_obj = Music(
                movie_id=db_movie.id,
                track_name=m.track_name,
                artist=m.artist,
                type=m.type
            )
            self.db.add(m_obj)

        # 15. Map Awards
        for a in movie.awards:
            a_obj = Award(
                movie_id=db_movie.id,
                name=a.name,
                category=a.category,
                year=a.year,
                winner=a.winner
            )
            self.db.add(a_obj)

        # 16. Map Reviews
        for r in movie.reviews:
            r_obj = Review(
                movie_id=db_movie.id,
                critic_name=r.critic_name,
                rating=r.rating,
                text=r.text
            )
            self.db.add(r_obj)

        # 17. Map Narrative Extensions: twists, conflicts, subplots
        for twist in movie.twists:
            self.db.add(MovieTwist(
                movie_id=db_movie.id, 
                description=twist,
                confidence_score=movie.confidence_score,
                generated_by=movie.generated_by,
                generated_at=_parse_dt(movie.generated_at),
                source=movie.source
            ))
        for conflict in movie.conflicts:
            self.db.add(MovieConflict(
                movie_id=db_movie.id, 
                description=conflict,
                confidence_score=movie.confidence_score,
                generated_by=movie.generated_by,
                generated_at=_parse_dt(movie.generated_at),
                source=movie.source
            ))
        for subplot in movie.subplots:
            self.db.add(MovieSubplot(
                movie_id=db_movie.id, 
                description=subplot,
                confidence_score=movie.confidence_score,
                generated_by=movie.generated_by,
                generated_at=_parse_dt(movie.generated_at),
                source=movie.source
            ))

        # 18. Map Prequels / Sequels
        for prequel_title in movie.prequels:
            preq_movie = self.db.query(Movie).filter(Movie.title == prequel_title).first()
            if preq_movie:
                rel = MovieRelationship(
                    from_movie_id=preq_movie.id,
                    to_movie_id=db_movie.id,
                    relation_type="prequel"
                )
                self.db.add(rel)
                
        for sequel_title in movie.sequels:
            seq_movie = self.db.query(Movie).filter(Movie.title == sequel_title).first()
            if seq_movie:
                rel = MovieRelationship(
                    from_movie_id=db_movie.id,
                    to_movie_id=seq_movie.id,
                    relation_type="sequel"
                )
                self.db.add(rel)

        self.db.commit()
        logger.info(f"PostgreSQL relational records committed successfully for ID {movie.tmdb_id}")
        return db_movie
