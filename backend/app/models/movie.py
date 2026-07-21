from datetime import date, datetime
from typing import List
from sqlalchemy import String, Integer, ForeignKey, Text, Date, Boolean, Float, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base
from app.models.base import AuditMixin

# Import actual model classes for relationships mapping
from app.models.franchise import Franchise
from app.models.taxonomy import Genre, Keyword, Studio, Theme, Emotion, Mood, StreamingProvider
from app.models.cast import MovieCast
from app.models.crew import MovieCrew
from app.models.narrative import Scene, VisualCue, MemoryCue, MovieTwist, MovieConflict, MovieSubplot
from app.models.media import Music, Award, Review

class Movie(Base, AuditMixin):
    """Movie metadata model storing comprehensive descriptive, narrative, and sync attributes."""
    __tablename__ = "movies"
    
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    overview: Mapped[str] = mapped_column(Text, nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    runtime: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tmdb_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    provider_name: Mapped[str] = mapped_column(String(50), default="tmdb")
    
    # Universal External Identifiers
    imdb_id: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    wikidata_id: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    tvdb_id: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)

    # Core Metadata extensions
    original_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    revenue: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tagline: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    adult: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    popularity: Mapped[float | None] = mapped_column(Float, nullable=True)
    vote_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    vote_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Narrative extensions
    plot: Mapped[str | None] = mapped_column(Text, nullable=True)
    plot_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    story_arc: Mapped[str | None] = mapped_column(Text, nullable=True)
    beginning: Mapped[str | None] = mapped_column(Text, nullable=True)
    middle: Mapped[str | None] = mapped_column(Text, nullable=True)
    climax: Mapped[str | None] = mapped_column(Text, nullable=True)
    ending: Mapped[str | None] = mapped_column(Text, nullable=True)
    ending_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timeline: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Sync Tracking
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Franchise link
    franchise_id: Mapped[int | None] = mapped_column(ForeignKey("franchises.id", ondelete="SET NULL"), nullable=True)

    # Mapped Relationships
    genres: Mapped[List[Genre]] = relationship(
        secondary="movie_genres", 
        back_populates="movies"
    )
    keywords: Mapped[List[Keyword]] = relationship(
        secondary="movie_keywords", 
        back_populates="movies"
    )
    studios: Mapped[List[Studio]] = relationship(
        secondary="movie_studios",
        back_populates="movies"
    )
    themes: Mapped[List[Theme]] = relationship(
        secondary="movie_themes",
        back_populates="movies"
    )
    emotions: Mapped[List[Emotion]] = relationship(
        secondary="movie_emotions",
        back_populates="movies"
    )
    moods: Mapped[List[Mood]] = relationship(
        secondary="movie_moods",
        back_populates="movies"
    )
    streaming_providers: Mapped[List[StreamingProvider]] = relationship(
        secondary="movie_streaming_providers",
        back_populates="movies"
    )
    cast: Mapped[List[MovieCast]] = relationship(
        back_populates="movie", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    crew: Mapped[List[MovieCrew]] = relationship(
        back_populates="movie", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    scenes: Mapped[List[Scene]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    visual_cues: Mapped[List[VisualCue]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    memory_cues: Mapped[List[MemoryCue]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    music: Mapped[List[Music]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    awards: Mapped[List[Award]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    reviews: Mapped[List[Review]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    twists: Mapped[List[MovieTwist]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    conflicts: Mapped[List[MovieConflict]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    subplots: Mapped[List[MovieSubplot]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    franchise: Mapped[Franchise | None] = relationship(back_populates="movies")

# Backward compatibility exports
from app.models.person import Person
from app.models.cast import MovieCast
from app.models.crew import MovieCrew
from app.models.franchise import Franchise
from app.models.taxonomy import Genre, Keyword, Studio, Theme, Emotion, Mood, StreamingProvider
from app.models.narrative import Scene, Dialogue, VisualCue, MemoryCue, MovieTwist, MovieConflict, MovieSubplot
from app.models.media import Music, Award, Review
from app.models.relationships import MovieRelationship
from app.models.user import UserPreferenceProfile, UserInteractionHistory
from app.models.association_tables import (
    movie_genres,
    movie_keywords,
    movie_studios,
    movie_themes,
    movie_emotions,
    movie_moods,
    movie_streaming_providers
)
