import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.api import deps
from app.database.base_class import Base
from app.core.env_validation import validate_environment
from app.core.config import settings
from app.core.rate_limit import HybridRateLimiter
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.vector import BaseVectorStore

# Isolated SQLite in memory database for session endpoints checks
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MockGraph(BaseKnowledgeGraph):
    def check_connection(self) -> bool:
        return True
    def close(self):
        pass
    def execute_query(self, query: str, parameters: dict = None):
        return []
    def run_transaction(self, cypher_queries):
        return []

class MockVectorStore(BaseVectorStore):
    def add_documents(self, texts, embeddings, metadatas=None, ids=None, collection_name=None):
        return []
    def similarity_search(self, query_embedding, k=5, filter=None, collection_name=None):
        return []
    def delete_documents(self, ids, collection_name=None):
        pass
    def count(self, collection_name=None) -> int:
        return 42

@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[deps.get_db] = lambda: TestingSessionLocal()
    app.dependency_overrides[deps.get_knowledge_graph] = lambda: MockGraph()
    app.dependency_overrides[deps.get_vector_store] = lambda: MockVectorStore()
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_liveness_endpoint():
    """
    Verify the liveness probe returns alive.
    """
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_endpoint():
    """
    Verify the readiness probe checks database availability.
    """
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

def test_health_check_endpoint():
    """
    Verify the detailed health diagnostics check runs.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["postgres"] == "connected"
    assert data["neo4j"] == "connected"
    assert data["chromadb"] == "connected"

def test_version_metadata_endpoint():
    """
    Verify the platform version route returns correct descriptors.
    """
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == settings.APP_NAME
    assert data["version"] == "1.0.0"
    assert "release_version" in data
    assert "git_commit" in data

def test_prometheus_metrics_endpoint():
    """
    Verify the prometheus scraping route returns text/plain metrics.
    """
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "filmaura_" in response.text

def test_environment_validation_success():
    """
    Verify validation passes in default test/dev modes.
    """
    validate_environment()

def test_hybrid_rate_limiter_memory_fallback():
    """
    Verify the rate limiter runs and permits request keys using local memory.
    """
    limiter = HybridRateLimiter(requests_limit=2, window_seconds=2)
    assert limiter.is_allowed("127.0.0.1") is True
    assert limiter.is_allowed("127.0.0.1") is True
    assert limiter.is_allowed("127.0.0.1") is False
