from sqlalchemy import String, Integer, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base

class Music(Base):
    """Music model tracking soundtrack, score, and theme tracks."""
    __tablename__ = "music"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    track_name: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="soundtrack")

    movie: Mapped["Movie"] = relationship(back_populates="music")

class Award(Base):
    """Award model recording nominations, wins, and ceremonies."""
    __tablename__ = "awards"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    winner: Mapped[bool] = mapped_column(Boolean, default=True)

    movie: Mapped["Movie"] = relationship(back_populates="awards")

class Review(Base):
    """Review model capturing critic sentiments and ratings."""
    __tablename__ = "reviews"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    critic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="reviews")
