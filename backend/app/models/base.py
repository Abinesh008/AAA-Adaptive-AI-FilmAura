from datetime import datetime
from sqlalchemy import Float, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

# JSON dialect variant for PostgreSQL JSONB support with SQLite fallback
JSON_TYPE = JSON().with_variant(JSONB(), "postgresql")

class AuditMixin:
    """Mixin for models containing curation metadata."""
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

class TimestampMixin:
    """Mixin for models containing creation and modification timestamps."""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
