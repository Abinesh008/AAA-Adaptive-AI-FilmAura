from abc import ABC, abstractmethod
from typing import List
from app.schemas.ontology import MovieOntologyInput

class BaseMovieDataProvider(ABC):
    """
    Abstract base class for Movie Data Providers (e.g. TMDb, OMDb, IMDb, custom datasets).
    Decouples raw API sources from the main ingestion pipeline.
    """
    
    @abstractmethod
    def fetch_movie_by_id(self, movie_id: str) -> MovieOntologyInput:
        """
        Fetch rich movie details and format them into the unified MovieOntologyInput schema.
        """
        pass

    @abstractmethod
    def fetch_popular_movies(self, limit: int = 20) -> List[MovieOntologyInput]:
        """
        Fetch a list of popular/trending movies from the provider source.
        """
        pass

    @abstractmethod
    def search_movies(self, query: str, limit: int = 10) -> List[MovieOntologyInput]:
        """
        Search for movies matching a string query.
        """
        pass
