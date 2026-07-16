from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Any

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True, 
        extra="ignore"
    )

    # Application Configuration
    APP_NAME: str = "AAA - Adaptive AI FilmAura"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database Configuration (PostgreSQL)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "filmaura"
    SQLALCHEMY_DATABASE_URI: str | None = None

    @model_validator(mode="before")
    @classmethod
    def assemble_db_connection(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If database URI is not set, assemble it from components
            if not data.get("SQLALCHEMY_DATABASE_URI"):
                server = data.get("POSTGRES_SERVER", "localhost")
                port = data.get("POSTGRES_PORT", 5432)
                user = data.get("POSTGRES_USER", "postgres")
                password = data.get("POSTGRES_PASSWORD", "password")
                db = data.get("POSTGRES_DB", "filmaura")
                data["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{user}:{password}@{server}:{port}/{db}"
        return data

    # Graph Database Configuration (Neo4j)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Vector Database Configuration (ChromaDB)
    CHROMA_PERSIST_DIR: str = "data/chroma"
    CHROMA_HOST: str | None = None
    CHROMA_PORT: int = 8000

    # LLM Providers Configuration (options: openai, gemini, mock)
    LLM_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = "mock-openai-api-key"
    GEMINI_API_KEY: str = "mock-gemini-api-key"
    LLM_MODEL: str = "mock-model"

    # Embedding Providers Configuration (options: local, openai, mock)
    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Cache Configuration (options: memory, redis)
    CACHE_PROVIDER: str = "memory"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    DEFAULT_CACHE_EXPIRE: int = 3600

    # Rate Limiter Configuration
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Ingestion Configuration
    TMDB_API_KEY: str | None = None
    TMDB_READ_ACCESS_TOKEN: str | None = None

    # Retrieval Configuration Settings
    RETRIEVAL_MAX_CANDIDATES: int = 20
    RERANKING_WEIGHTS: dict = {"semantic": 0.4, "graph": 0.3, "keyword": 0.1, "popularity": 0.2}
    VECTOR_SIMILARITY_THRESHOLD: float = 1.5
    GRAPH_TRAVERSAL_DEPTH: int = 2
    RETRIEVAL_CACHE_TTL: int = 3600
    TOKEN_BUDGET: int = 4000
    PLANNER_COST_WEIGHTS: dict = {"sql": 10, "graph": 30, "vector": 60}
    PARALLEL_TIMEOUT_MS: int = 5000
    CIRCUIT_BREAKER_FAILURES: int = 3
    CIRCUIT_BREAKER_COOLDOWN: int = 30

settings = Settings()
