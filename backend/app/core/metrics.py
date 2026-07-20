from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from time import time

# Create a dedicated registry to avoid duplicate metrics registrations during reloads
REGISTRY = CollectorRegistry()

# 1. API latency and counts
HTTP_REQUESTS_TOTAL = Counter(
    "filmaura_http_requests_total",
    "Total count of HTTP requests processed",
    ["method", "endpoint", "status"],
    registry=REGISTRY
)

HTTP_REQUEST_LATENCY = Histogram(
    "filmaura_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=REGISTRY
)

# 2. Recommendation latency
RECOMMENDATION_LATENCY = Histogram(
    "filmaura_recommendation_duration_seconds",
    "Recommendation generation latency in seconds",
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY
)

# 3. Agent latency
AGENT_LATENCY = Histogram(
    "filmaura_agent_query_duration_seconds",
    "AI Agent reasoning loop latency in seconds",
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 20.0),
    registry=REGISTRY
)

# 4. Retrieval latency
RETRIEVAL_LATENCY = Histogram(
    "filmaura_retrieval_duration_seconds",
    "Hybrid multi-source retrieval search latency in seconds",
    buckets=(0.05, 0.2, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY
)

# 5. Authentication metrics
AUTH_EVENTS = Counter(
    "filmaura_auth_events_total",
    "Total count of authentication attempts",
    ["event_type", "status"],  # event_type: login, register; status: success, failure
    registry=REGISTRY
)

# 6. Cache hit ratio
CACHE_REQUESTS = Counter(
    "filmaura_cache_requests_total",
    "Total count of caching requests",
    ["status"],  # status: hit, miss
    registry=REGISTRY
)

# 7. Active Sessions
ACTIVE_USERS = Gauge(
    "filmaura_active_users_count",
    "Current active user counts tracked on system",
    registry=REGISTRY
)

def get_metrics_payload() -> tuple[bytes, str]:
    """
    Generates latest Prometheus scraping registry formatted payload.
    """
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
