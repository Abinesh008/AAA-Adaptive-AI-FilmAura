from datetime import date, datetime
from typing import List
from sqlalchemy import String, Integer, Table, Column, ForeignKey, Text, Date, Boolean, Float, BigInteger, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base

# ==============================================================================
# Association Tables (No Auto-ID Injection)
# ==============================================================================

# Association Table for Movies & Genres
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for Movies & Keywords
movie_keywords = Table(
    "movie_keywords",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for Movies & Studios
movie_studios = Table(
    "movie_studios",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("studio_id", Integer, ForeignKey("studios.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for Movies & Themes
movie_themes = Table(
    "movie_themes",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", Integer, ForeignKey("themes.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for Movies & Emotions
movie_emotions = Table(
    "movie_emotions",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("emotion_id", Integer, ForeignKey("emotions.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for Movies & Moods
movie_moods = Table(
    "movie_moods",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("mood_id", Integer, ForeignKey("moods.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for Movies & Streaming Providers
movie_streaming_providers = Table(
    "movie_streaming_providers",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("provider_id", Integer, ForeignKey("streaming_providers.id", ondelete="CASCADE"), primary_key=True)
)

# ==============================================================================
# Model Implementations
# ==============================================================================

class Genre(Base):
    __tablename__ = "genres"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_genres", 
        back_populates="genres"
    )

class Keyword(Base):
    __tablename__ = "keywords"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_keywords", 
        back_populates="keywords"
    )

class Studio(Base):
    __tablename__ = "studios"
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_studios",
        back_populates="studios"
    )

class Theme(Base):
    __tablename__ = "themes"
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_themes",
        back_populates="themes"
    )

class Emotion(Base):
    __tablename__ = "emotions"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_emotions",
        back_populates="emotions"
    )

class Mood(Base):
    __tablename__ = "moods"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_moods",
        back_populates="moods"
    )

class StreamingProvider(Base):
    __tablename__ = "streaming_providers"
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    availability: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    
    movies: Mapped[List["Movie"]] = relationship(
        secondary="movie_streaming_providers",
        back_populates="streaming_providers"
    )

class Person(Base):
    __tablename__ = "people"
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    external_person_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    provider_name: Mapped[str] = mapped_column(String(50), default="tmdb")

    cast_roles: Mapped[List["MovieCast"]] = relationship(back_populates="person")
    crew_roles: Mapped[List["MovieCrew"]] = relationship(back_populates="person")

class MovieCast(Base):
    __tablename__ = "movie_cast"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    character_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Extended Phase 2 character traits
    aliases: Mapped[list | None] = mapped_column(JSON, nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance: Mapped[str | None] = mapped_column(String(50), nullable=True)  # main, supporting, cameo
    relationships: Mapped[list | None] = mapped_column(JSON, nullable=True)
    personality_traits: Mapped[list | None] = mapped_column(JSON, nullable=True)
    motivations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    arc: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="cast")
    person: Mapped[Person] = relationship(back_populates="cast_roles")

class MovieCrew(Base):
    __tablename__ = "movie_crew"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    job: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="crew")
    person: Mapped[Person] = relationship(back_populates="crew_roles")

class Franchise(Base):
    __tablename__ = "franchises"
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(back_populates="franchise")

class MovieRelationship(Base):
    __tablename__ = "movie_relationships"
    from_movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    to_movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # sequel, prequel, remake, spinoff

class Scene(Base):
    __tablename__ = "scenes"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    scene_index: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    importance: Mapped[str | None] = mapped_column(Text, nullable=True)
    scene_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="scenes")
    dialogues: Mapped[List["Dialogue"]] = relationship(back_populates="scene", cascade="all, delete-orphan")

class Dialogue(Base):
    __tablename__ = "dialogues"
    scene_id: Mapped[int] = mapped_column(ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False)
    speaker: Mapped[str] = mapped_column(String(255), nullable=False)
    listener: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dialogue_text: Mapped[str] = mapped_column(Text, nullable=False)
    meaning: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotional_tone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subtext: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    scene: Mapped[Scene] = relationship(back_populates="dialogues")

class VisualCue(Base):
    __tablename__ = "visual_cues"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cue_type: Mapped[str | None] = mapped_column(String(100), nullable=True)  # palette, style, camera, lighting, motif
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="visual_cues")

class MemoryCue(Base):
    __tablename__ = "memory_cues"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="memory_cues")

class Music(Base):
    __tablename__ = "music"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    track_name: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="soundtrack")  # soundtrack, score, theme

    movie: Mapped["Movie"] = relationship(back_populates="music")

class Award(Base):
    __tablename__ = "awards"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    winner: Mapped[bool] = mapped_column(Boolean, default=True)

    movie: Mapped["Movie"] = relationship(back_populates="awards")

class Review(Base):
    __tablename__ = "reviews"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    critic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="reviews")

class MovieTwist(Base):
    __tablename__ = "movie_twists"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="twists")

class MovieConflict(Base):
    __tablename__ = "movie_conflicts"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="conflicts")

class MovieSubplot(Base):
    __tablename__ = "movie_subplots"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="subplots")

class Movie(Base):
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
    
    # Metadata for Phase 2 Enhancements
    confidence_score: Mapped[float | None] = mapped_column(Float, default=1.0, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), default="tmdb", nullable=True)

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
        cascade="all, delete-orphan"
    )
    crew: Mapped[List[MovieCrew]] = relationship(
        back_populates="movie", 
        cascade="all, delete-orphan"
    )
    scenes: Mapped[List[Scene]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    visual_cues: Mapped[List[VisualCue]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    memory_cues: Mapped[List[MemoryCue]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
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
        cascade="all, delete-orphan"
    )
    conflicts: Mapped[List[MovieConflict]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    subplots: Mapped[List[MovieSubplot]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    franchise: Mapped[Franchise | None] = relationship(back_populates="movies")
