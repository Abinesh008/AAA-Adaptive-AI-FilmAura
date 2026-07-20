# FilmAura Infrastructure Architecture

This document maps out the system infrastructure, CI/CD pipelines, security middlewares, caching hierarchies, and monitoring patterns.

---

## 1. System Architecture

```mermaid
graph TD
    User[Web Client] -->|HTTP / TLS| FE[Frontend Container - Port 3000]
    FE -->|API request| BE[Backend Gateway Container - Port 8000]
    
    subgraph Storage Layer
        BE -->|Relational SQL| PG[(PostgreSQL - Port 5432)]
        BE -->|Graph Queries| N4J[(Neo4j Graph - Port 7687)]
        BE -->|Vector Search| CHR[(ChromaDB - Port 8000)]
    end

    subgraph Speed Layer
        BE -->|Cache & Rate Limit| RED[(Redis - Port 6379)]
    end

    subgraph Monitoring Layer
        PRM[Prometheus - Port 9090] -->|Scrape /metrics| BE
        GRF[Grafana - Port 3001] -->|Query| PRM
    end
```

---

## 2. CI/CD Workflows

GitHub Actions execute checks on three workflows:
1. **Backend Pipeline**:
   - Spawns a PostgreSQL container.
   - Installs dependencies.
   - Compiles app scripts.
   - Runs `pytest` suite.
2. **Frontend Pipeline**:
   - Sets up Node.js.
   - Installs npm modules.
   - Validates TypeScript styles.
   - Compiles Next.js standalone pages.
3. **Release Pipeline**:
   - Validates Docker compilation builds.

---

## 3. Caching and Degradation Logic

If the Redis connection fails or cache is offline, `RedisCacheManager` delegates automatically to `InMemoryCacheManager`.
Likewise, the sliding-window rate limiter will fall back to local dict caches, preventing user request failures.

---

## 4. Security Controls

Security hardening parameters:
- **HTTP Secure Headers**: CSP, HSTS, X-Content-Type-Options, X-Frame-Options are injected via FastAPI middleware.
- **CORS Restricted Origins**: Restricts cross-origin requests to trusted frontends in production mode.
