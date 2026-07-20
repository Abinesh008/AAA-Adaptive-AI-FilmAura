# FilmAura Docker & Containerization Guide

This document covers running FilmAura services using Docker and Docker Compose.

---

## 1. Container Architecture

FilmAura orchestrates 7 services inside a unified bridge network:
- `db` (Postgres, port `5432`)
- `neo4j` (Graph, HTTP `7474`, Bolt `7687`)
- `chroma` (Vector store, port `8001` host map)
- `redis` (Cache, port `6379`)
- `web` (FastAPI backend, port `8000`)
- `frontend` (Next.js frontend, port `3000`)
- `prometheus` (Metrics, port `9090`)
- `grafana` (Observability, port `3001` host map)

---

## 2. Setup & Execution

### Pre-requisites
- Docker installed (version 20+)
- Docker Compose installed (version 2+)

### Running in Development
Start local containers with hot-reload volume mounts:
```bash
docker compose up --build
```
This automatically merges settings from `docker-compose.yml` and `docker-compose.override.yml`.

### Running in Production
For production deployment, run without the development override options:
```bash
docker compose -f docker-compose.yml up -d --build
```

---

## 3. Health checks and Graceful Shutdowns

Each container defines a healthcheck status:
- **Postgres**: uses `pg_isready` to confirm query responsiveness.
- **Neo4j**: checks cypher shell execution.
- **Backend/Frontend**: checks root-level `/live` ping pages.

Containers are shut down gracefully by docker daemon using `SIGTERM` signals, letting backend complete pending client connections and close neo4j session pools cleanly (handled in FastAPI lifespan event handlers).
