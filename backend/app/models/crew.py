from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base

class MovieCrew(Base):
    """MovieCrew model representing directors, writers, and technical crew roles."""
    __tablename__ = "movie_crew"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    job: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="crew")
    person: Mapped["Person"] = relationship(back_populates="crew_roles")
