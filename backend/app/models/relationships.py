from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base_class import Base

class MovieRelationship(Base):
    """MovieRelationship model storing structural links between movies (e.g. sequels, spin-offs)."""
    __tablename__ = "movie_relationships"

    from_movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    to_movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
