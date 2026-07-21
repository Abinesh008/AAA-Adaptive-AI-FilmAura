from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base

class Genre(Base):
    """Genre categorization for movies."""
    __tablename__ = "genres"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_genres", 
        back_populates="genres",
        lazy="selectin"
    )

class Keyword(Base):
    """Keyword descriptor for specific plot elements and objects."""
    __tablename__ = "keywords"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_keywords", 
        back_populates="keywords",
        lazy="selectin"
    )

class Studio(Base):
    """Production studio that released the movie."""
    __tablename__ = "studios"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_studios",
        back_populates="studios",
        lazy="selectin"
    )

class Theme(Base):
    """Theme conceptual descriptor representing motifs and message topics."""
    __tablename__ = "themes"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_themes",
        back_populates="themes",
        lazy="selectin"
    )

class Emotion(Base):
    """Emotion classification representing feelings evoked by the movie."""
    __tablename__ = "emotions"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_emotions",
        back_populates="emotions",
        lazy="selectin"
    )

class Mood(Base):
    """Mood descriptor mapping stylistic tone characteristics."""
    __tablename__ = "moods"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_moods",
        back_populates="moods",
        lazy="selectin"
    )

class StreamingProvider(Base):
    """StreamingProvider model tracking availability and regional catalogs."""
    __tablename__ = "streaming_providers"

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    availability: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)

    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_streaming_providers",
        back_populates="streaming_providers",
        lazy="selectin"
    )
