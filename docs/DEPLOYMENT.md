# FilmAura Deployment Guide

This document describes how to deploy the FilmAura application platform in a production-ready cloud or local environment.

---

## 1. Infrastructure Overview

FilmAura uses a hybrid databases architecture:
1. **PostgreSQL 16**: Relational storage for user profiles and feedback.
2. **Neo4j 5.x**: Graph database for movie nodes and genre taxonomy traversal.
3. **ChromaDB**: Vector storage for semantic embeddings and movie plot queries.
4. **Redis 7.x**: High-performance caching, session, and rate-limiting store.

---

## 2. Environment Variables Configuration

Create a `.env` file in the backend root based on `.env.example`:

| Key | Description | Default | Required in Production |
|-----|-------------|---------|------------------------|
| `APP_ENV` | Mode profile (`development`, `production`, `testing`) | `development` | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL connection password | `password` | Yes (change default) |
| `NEO4J_PASSWORD` | Neo4j connection password | `password` | Yes (change default) |
| `CACHE_PROVIDER` | Cache engine (`memory`, `redis`) | `memory` | Yes (`redis`) |
| `REDIS_HOST` | Host address of Redis instance | `localhost` | Yes (`redis`) |
| `LLM_PROVIDER` | LLM execution driver (`openai`, `gemini`, `mock`) | `mock` | Yes |
| `OPENAI_API_KEY` | Secret credentials for OpenAI services | `mock-openai-key` | Yes (if `LLM_PROVIDER=openai`) |

---

## 3. Database Initialization & Backup Strategy

### Automated Migrations (Alembic)
Relational schemas are managed via Alembic. Run migrations inside the container:
```bash
docker compose exec web alembic upgrade head
```

### PostgreSQL Backups
Run pg_dump periodically:
```bash
docker compose exec db pg_dump -U postgres filmaura > filmaura_backup.sql
```

### Neo4j Backups
Use `neo4j-admin` tools to dump the store:
```bash
docker compose exec neo4j neo4j-admin database dump neo4j --to-path=/var/lib/neo4j/import
```

---

## 4. Disaster Recovery Strategy

1. **Database Recovery**: Restore the PostgreSQL schema from sql dumps:
   ```bash
   docker compose exec -T db psql -U postgres filmaura < filmaura_backup.sql
   ```
2. **ChromaDB Re-indexing**: If vector storage fails, run the re-indexing endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/reindex
   ```
3. **Graceful Fallbacks**: If Redis or Prometheus fails, the app degrades gracefully to memory and continues operating without service disruption.
