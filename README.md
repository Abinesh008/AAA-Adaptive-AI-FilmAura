# AAA – Adaptive AI FilmAura
> Beyond Genres. Into Memories.

AAA - Adaptive AI FilmAura is a real-world, production-grade AI platform designed to identify movies even when users provide vague, incomplete, emotional, visual, symbolic, or memory-based descriptions. It understands a user's cinematic taste and viewing psychology to make personalized recommendations.

---

## Technical Stack

- **Backend**: Python 3.14 + FastAPI
- **Database (Relational)**: PostgreSQL + SQLAlchemy ORM 2.0 + Alembic (migrations)
- **Knowledge Graph**: Neo4j
- **Vector Database**: ChromaDB
- **Caching**: Local memory cache (and Redis adapter)
- **Containerization**: Docker & Docker Compose

---

## Repository Structure

```text
AAA-Adaptive-AI-FilmAura/
├── backend/
│   ├── app/
│   │   ├── api/             # API Router, endpoints (health, version) and deps
│   │   ├── core/            # Config, logging, interfaces, providers, middle, exceptions, managers
│   │   │   ├── interfaces/  # Abstract Base Classes (LLM, Embeddings, Vector, Graph, Cache)
│   │   │   └── providers/   # Concrete provider implementations (OpenAI, Gemini, Chroma, Neo4j, Redis)
│   │   ├── database/        # Session configs & SQLAlchemy models
│   │   ├── models/          # Declarative DB models
│   │   ├── schemas/         # Pydantic schemas (common, etc.)
│   │   ├── services/        # Service wrappers
│   │   ├── repositories/    # Database Repository wrappers
│   │   └── main.py          # FastAPI application initialization
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── scripts/                 # Startup/helper scripts
├── docker-compose.yml       # Local infrastructure orchestrator
└── README.md                # This file
```

---

## Local Setup

### 1. Configure Environments
Copy `backend/.env.example` to `backend/.env` and edit the connection details or API keys:
```bash
cp backend/.env.example backend/.env
```

### 2. Run Infrastructure (Docker)
Ensure Docker is running, then spin up the required database containers (PostgreSQL, Neo4j):
```bash
docker-compose up -d
```

### 3. Run FastAPI Application Locally
From the `backend` directory, activate the virtual environment and run uvicorn:
```bash
cd backend
# Windows:
.\venv\Scripts\activate
uvicorn app.main:app --reload

# macOS/Linux:
source venv/bin/activate
uvicorn app.main:app --reload
```

---

## Development Guidelines

### Abstract Provider Interfaces
All third-party services (LLMs, Embeddings, Vector DBs, Caches, Graphs) are accessed via abstract interfaces under `app/core/interfaces`. To swap providers, edit the environment variable (e.g. `LLM_PROVIDER="gemini"`) or implement a new provider inside `app/core/providers/`.

### Logging & Health Checks
Structured logging traces requests with Correlation IDs. System operations are monitored via standard FastAPI HTTP endpoints:
- Liveness check: `GET /live`
- Readiness check: `GET /ready`
- Complete database diagnostics: `GET /health`
- Version info: `GET /version`
- Prometheus scraping target: `GET /metrics`

---

## Production Operations & Documentation

Detailed deployment guides, configurations, and architecture diagrams can be found in the `docs/` directory:
- [Docker Containerization Guide](file:///c:/Users/USER/Documents/AAA-Adaptive-AI-FilmAura/docs/DOCKER.md)
- [Production Deployment Guide](file:///c:/Users/USER/Documents/AAA-Adaptive-AI-FilmAura/docs/DEPLOYMENT.md)
- [System Infrastructure Design](file:///c:/Users/USER/Documents/AAA-Adaptive-AI-FilmAura/docs/INFRASTRUCTURE.md)

