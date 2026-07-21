from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.ingestion.pipeline import MovieIngestionPipeline
from app.ingestion.providers.tmdb import TMDbMovieProvider
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.vector import BaseVectorStore
from app.core.interfaces.embedding import BaseEmbeddingProvider

class IngestionService(BaseService):
    """
    Orchestrates logic for launching and supervising the TMDB movie metadata ingestion pipeline runs in background tasks.
    """
    def trigger_ingestion(
        self,
        movie_ids: list[str],
        popular_limit: int,
        provider: str,
        db: Session,
        graph: BaseKnowledgeGraph,
        vector: BaseVectorStore,
        embedding: BaseEmbeddingProvider,
        background_tasks: BackgroundTasks
    ):
        background_tasks.add_task(
            self.run_ingestion_background,
            movie_ids,
            popular_limit,
            provider,
            db,
            graph,
            vector,
            embedding
        )

    def run_ingestion_background(
        self,
        movie_ids: list[str],
        popular_limit: int,
        provider: str,
        db: Session,
        graph: BaseKnowledgeGraph,
        vector: BaseVectorStore,
        embedding: BaseEmbeddingProvider
    ):
        self.logger.info("Background ingestion task started...")
        
        # 1. Resolve provider
        if provider.lower() == "tmdb":
            movie_provider = TMDbMovieProvider()
        else:
            self.logger.warning(f"Unknown provider '{provider}', defaulting to TMDbProvider.")
            movie_provider = TMDbMovieProvider()

        # 2. Instantiate pipeline
        try:
            pipeline = MovieIngestionPipeline(
                db=db,
                graph_db=graph,
                vector_store=vector,
                embedding_provider=embedding,
                provider=movie_provider
            )

            # 3. Run Ingestion based on parameters
            if movie_ids:
                self.logger.info(f"Ingesting specific movie IDs: {movie_ids}")
                for mid in movie_ids:
                    try:
                        pipeline.ingest_movie_by_id(mid)
                    except Exception as e:
                        self.logger.error(f"Failed to ingest movie ID {mid} in background: {e}")
            elif popular_limit > 0:
                self.logger.info(f"Ingesting popular movies batch (limit={popular_limit})")
                pipeline.ingest_popular_movies(limit=popular_limit)
            else:
                self.logger.warning("Ingestion triggered with empty parameters.")
                
            self.logger.info("Background ingestion task completed successfully.")
        except Exception as e:
            self.logger.exception(f"Fatal error in background ingestion pipeline: {e}")
