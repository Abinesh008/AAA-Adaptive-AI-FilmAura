from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.base_class import Base

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
