from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base
from app.models.base import AuditMixin, JSON_TYPE

class MovieCast(Base, AuditMixin):
    """MovieCast model associating actors with movies and character traits."""
    __tablename__ = "movie_cast"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    character_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Extended traits utilizing JSONB (Postgres) and JSON (SQLite)
    aliases: Mapped[list | None] = mapped_column(JSON_TYPE, nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance: Mapped[str | None] = mapped_column(String(50), nullable=True)  # main, supporting, cameo
    relationships: Mapped[list | None] = mapped_column(JSON_TYPE, nullable=True)
    personality_traits: Mapped[list | None] = mapped_column(JSON_TYPE, nullable=True)
    motivations: Mapped[list | None] = mapped_column(JSON_TYPE, nullable=True)
    arc: Mapped[str | None] = mapped_column(Text, nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="cast")
    person: Mapped["Person"] = relationship(back_populates="cast_roles")
