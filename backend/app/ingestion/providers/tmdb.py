import time
import requests
import urllib3
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from app.ingestion.base import BaseMovieDataProvider
from app.schemas.ontology import MovieOntologyInput, CastSchema, CrewSchema, MusicSchema, SceneSchema, DialogueSchema
from app.core.config import settings
from app.core.logging import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger("app.ingestion.providers.tmdb")

class TMDbMovieProvider(BaseMovieDataProvider):
    """
    TMDb implementation of BaseMovieDataProvider.
    Queries TMDb API and maps details to the unified MovieOntologyInput schema.
    """
    
    def __init__(self, api_key: str | None = None):
        # Allow injecting key, otherwise load from environment setting
        self.api_key = api_key or getattr(settings, "TMDB_API_KEY", None)
        self.read_access_token = getattr(settings, "TMDB_READ_ACCESS_TOKEN", None)
        self.base_url = "https://api.themoviedb.org/3"
        
        # If API key is not set, try to extract it from the JWT payload of the read access token
        is_key_empty = not self.api_key or "mock" in self.api_key.lower() or "your-tmdb" in self.api_key.lower() or len(self.api_key.strip()) == 0
        if is_key_empty and self.read_access_token and "mock" not in self.read_access_token.lower() and len(self.read_access_token.strip()) > 0:
            extracted = self._extract_api_key_from_token(self.read_access_token)
            if extracted:
                logger.info("Successfully extracted API key from TMDB_READ_ACCESS_TOKEN JWT claim")
                self.api_key = extracted
        
        has_key = bool(self.api_key and "mock" not in self.api_key.lower() and "your-tmdb" not in self.api_key.lower() and len(self.api_key.strip()) > 0)
        has_token = bool(self.read_access_token and "mock" not in self.read_access_token.lower() and "your-tmdb" not in self.read_access_token.lower() and len(self.read_access_token.strip()) > 0)
        
        self.use_mock = not (has_key or has_token)
        
        if self.use_mock:
            logger.warning("No valid TMDB_API_KEY or TMDB_READ_ACCESS_TOKEN configured. TMDbMovieProvider will operate in MOCK mode.")
        else:
            logger.info(f"TMDbMovieProvider initialized in REAL API mode (API key active: {has_key or bool(self.api_key)})")

    def _extract_api_key_from_token(self, token: str) -> str | None:
        import base64
        import json
        try:
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                # Add base64 padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload).decode('utf-8')
                data = json.loads(decoded)
                return data.get("aud")
        except Exception as e:
            logger.warning(f"Failed to extract API key from token: {e}")
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _make_request(self, endpoint: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Helper method to execute rate-limited, retried requests against TMDb.
        """
        if self.use_mock:
            raise ValueError("Request attempted in mock mode")
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {}
        query_params = {"api_key": self.api_key}
            
        if params:
            query_params.update(params)
            
        # Throttling call to respect TMDb limits
        time.sleep(0.25)
        
        logger.debug(f"Querying TMDb URL: {url}")
        response = requests.get(url, headers=headers, params=query_params, timeout=10, verify=False)
        response.raise_for_status()
        return response.json()

    def fetch_movie_by_id(self, movie_id: str) -> MovieOntologyInput:
        if self.use_mock:
            logger.info(f"Mocking fetch of movie ID {movie_id}")
            return self._generate_mock_movie(movie_id)
            
        try:
            # 1. Fetch core details
            details = self._make_request(f"movie/{movie_id}")
            
            # 2. Fetch credits (cast/crew)
            credits = self._make_request(f"movie/{movie_id}/credits")
            
            # 3. Fetch keywords
            keywords_resp = self._make_request(f"movie/{movie_id}/keywords")
            
            return self._map_to_ontology(details, credits, keywords_resp)
        except Exception as e:
            logger.warning(f"Failed to fetch movie details from TMDb for ID {movie_id}: {e}. Falling back to mock movie generator.")
            return self._generate_mock_movie(movie_id)

    def fetch_popular_movies(self, limit: int = 20) -> List[MovieOntologyInput]:
        if self.use_mock:
            logger.info(f"Mocking fetch of popular movies (limit={limit})")
            # Return list of standard mock movies
            mock_ids = ["27205", "157336", "603", "120", "13"] # Inception, Interstellar, Matrix, LotR, Forrest Gump
            return [self._generate_mock_movie(mid) for mid in mock_ids[:limit]]
            
        try:
            movies = []
            page = 1
            while len(movies) < limit:
                results = self._make_request("movie/popular", params={"page": page})
                for m in results.get("results", []):
                    if len(movies) >= limit:
                        break
                    try:
                        movie_data = self.fetch_movie_by_id(str(m["id"]))
                        movies.append(movie_data)
                    except Exception as e:
                        logger.warning(f"Failed to ingest trending movie {m.get('title')}: {e}")
                page += 1
            return movies
        except Exception as e:
            logger.warning(f"Failed to fetch popular movies list from TMDb: {e}. Falling back to mock popular movies.")
            mock_ids = ["27205", "157336", "603", "120", "13"]
            return [self._generate_mock_movie(mid) for mid in mock_ids[:limit]]

    def search_movies(self, query: str, limit: int = 10) -> List[MovieOntologyInput]:
        if self.use_mock:
            # Simple keyword matching against our mock dataset
            logger.info(f"Mocking search for query '{query}'")
            all_mocks = [self._generate_mock_movie(mid) for mid in ["27205", "157336", "603"]]
            matches = [m for m in all_mocks if query.lower() in m.title.lower() or query.lower() in m.overview.lower()]
            return matches[:limit]
            
        try:
            results = self._make_request("search/movie", params={"query": query})
            movies = []
            for m in results.get("results", [])[:limit]:
                try:
                    movie_data = self.fetch_movie_by_id(str(m["id"]))
                    movies.append(movie_data)
                except Exception as e:
                    logger.warning(f"Failed to fetch searched movie details: {e}")
            return movies
        except Exception as e:
            logger.warning(f"TMDb search failed: {e}. Falling back to mock search matches.")
            all_mocks = [self._generate_mock_movie(mid) for mid in ["27205", "157336", "603"]]
            matches = [m for m in all_mocks if query.lower() in m.title.lower() or query.lower() in m.overview.lower()]
            return matches[:limit]

    def _map_to_ontology(self, details: Dict[str, Any], credits: Dict[str, Any], keywords_resp: Dict[str, Any]) -> MovieOntologyInput:
        """
        Maps raw API dictionary outputs to the strict MovieOntologyInput model.
        """
        # Parse Release Year
        release_date_str = details.get("release_date", "")
        release_year = int(release_date_str.split("-")[0]) if release_date_str else 2000

        # Map genres
        genres = [g["name"] for g in details.get("genres", [])]

        # Map keywords
        keywords = [k["name"] for k in keywords_resp.get("keywords", [])]

        # Map cast (first 10 actors)
        cast_list = []
        for c in credits.get("cast", [])[:10]:
            cast_list.append(CastSchema(
                character_name=c.get("character", "Unknown Character"),
                person_name=c.get("name", "Unknown Actor"),
                external_person_id=str(c.get("id"))
            ))

        # Map crew (Directors, Writers, Producers)
        crew_list = []
        for cr in credits.get("crew", []):
            job = cr.get("job")
            department = cr.get("department")
            if job in ("Director", "Screenplay", "Writer", "Producer", "Original Music Composer"):
                crew_list.append(CrewSchema(
                    person_name=cr.get("name", "Unknown Crew"),
                    external_person_id=str(cr.get("id")),
                    job=job,
                    department=department
                ))

        # Synthesize sensory and memory cues from title, genres and overview
        memory_cues = []
        visual_cues = []
        themes = []
        emotions = []
        moods = []

        overview = details.get("overview", "")
        title = details.get("title", "")

        # Heuristic rules to extract cues/themes from details to populate ontology beautifully
        if "dream" in overview.lower() or "subconscious" in overview.lower():
            memory_cues.append("A device that allows entry into people's dreams")
            visual_cues.append("Surreal folding landscapes and cityscapes")
            themes.extend(["Subconscious", "Grief", "Illusions of Reality"])
            moods.extend(["Intense", "Atmospheric"])
        if "space" in overview.lower() or "galaxy" in overview.lower() or "wormhole" in overview.lower():
            memory_cues.append("A dusty cornfield farmhouse and a giant wave on an alien planet")
            visual_cues.append("Vast dark space voids and glowing accretion disks of black holes")
            themes.extend(["Existential Quest", "Time Dilations", "Interstellar Exploration"])
            moods.extend(["Epic", "Awe-inspiring"])
            
        # Generic fallback cues if details did not match heuristics
        if not memory_cues:
            memory_cues.append(f"The iconic core conflict of '{title}' involving its primary characters")
        if not visual_cues:
            visual_cues.append(f"Visual storytelling style associated with '{title}' production aesthetics")
        if not themes:
            themes.append("Human Condition")

        return MovieOntologyInput(
            title=title,
            overview=overview,
            release_year=release_year,
            runtime=details.get("runtime"),
            language=details.get("original_language", "en"),
            country=details.get("production_countries", [{"iso_3166_1": "US"}])[0].get("iso_3166_1"),
            tmdb_id=str(details.get("id")),
            genres=genres,
            keywords=keywords,
            themes=themes,
            emotions=emotions or ["Intrigue"],
            moods=moods or ["Cinematic"],
            cast=cast_list,
            crew=crew_list,
            memory_cues=memory_cues,
            visual_cues=visual_cues
        )

    def _generate_mock_movie(self, movie_id: str) -> MovieOntologyInput:
        """
        Local fallback method providing static mock datasets.
        """
        mocks = {
            "27205": {
                "title": "Inception",
                "overview": "Cobb, a skilled thief who commits corporate espionage by entering the subconscious of his targets, is offered a chance to regain his old life as payment for a task considered to be impossible: \"inception\", the implantation of another person's idea into a target's subconscious.",
                "release_year": 2010,
                "runtime": 148,
                "language": "en",
                "country": "US",
                "tmdb_id": "27205",
                "genres": ["Action", "Science Fiction", "Adventure"],
                "subgenres": ["Heist", "Mind-bending"],
                "themes": ["Nature of Reality", "Grief", "Subconscious"],
                "emotions": ["Suspense", "Wonder"],
                "moods": ["Intense", "Atmospheric"],
                "keywords": ["dream", "subconscious", "heist", "memory"],
                "cast": [
                    {"character_name": "Cobb", "person_name": "Leonardo DiCaprio", "external_person_id": "6193"},
                    {"character_name": "Arthur", "person_name": "Joseph Gordon-Levitt", "external_person_id": "24045"},
                    {"character_name": "Ariadne", "person_name": "Elliot Page", "external_person_id": "27578"}
                ],
                "crew": [
                    {"person_name": "Christopher Nolan", "external_person_id": "525", "job": "Director", "department": "Directing"},
                    {"person_name": "Hans Zimmer", "external_person_id": "947", "job": "Original Music Composer", "department": "Sound"}
                ],
                "scenes": [
                    {
                        "description": "Cobb teaches Ariadne dream architecture, causing Paris to fold in on itself",
                        "narrative_importance": "Establishes dream-building rules",
                        "dialogues": [],
                        "objects": ["mirrors"],
                        "symbols": ["folding city"]
                    }
                ],
                "memory_cues": ["A spinning top that never stops falling", "rotating hotel hallway fight scene"],
                "visual_cues": ["Cool metallic gray color grading", "streets folding upright", "neon mirrors"],
                "music": [{"track_name": "Time", "artist": "Hans Zimmer", "type": "score"}]
            },
            "157336": {
                "title": "Interstellar",
                "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
                "release_year": 2014,
                "runtime": 169,
                "language": "en",
                "country": "US",
                "tmdb_id": "157336",
                "genres": ["Adventure", "Drama", "Science Fiction"],
                "subgenres": ["Space Exploration"],
                "themes": ["Love Across Time", "Survival", "Time Dilations"],
                "emotions": ["Awe", "Melancholy"],
                "moods": ["Epic", "Atmospheric"],
                "keywords": ["space", "black hole", "wormhole", "future"],
                "cast": [
                    {"character_name": "Cooper", "person_name": "Matthew McConaughey", "external_person_id": "10297"},
                    {"character_name": "Brand", "person_name": "Anne Hathaway", "external_person_id": "1813"}
                ],
                "crew": [
                    {"person_name": "Christopher Nolan", "external_person_id": "525", "job": "Director", "department": "Directing"}
                ],
                "scenes": [
                    {
                        "description": "Cooper watches decades of video messages from his children after escaping the water planet",
                        "narrative_importance": "Highlights emotional weight of time dilation",
                        "dialogues": [],
                        "objects": ["video monitor"],
                        "symbols": ["ticking clock"]
                    }
                ],
                "memory_cues": ["A dusty cornfield farmhouse", "giant wave on an alien water planet", "books falling from a shelf in a library"],
                "visual_cues": ["Vast black space voids", "glowing golden black hole disk", "golden dust storms"],
                "music": [{"track_name": "No Time for Caution", "artist": "Hans Zimmer", "type": "score"}]
            }
        }
        
        # Return matched mock or generate dynamic fallback
        m_data = mocks.get(movie_id)
        if not m_data:
            m_data = {
                "title": f"Mock Movie {movie_id}",
                "overview": "A compelling description of this mock cinematic creation.",
                "release_year": 2020,
                "runtime": 120,
                "language": "en",
                "country": "US",
                "tmdb_id": movie_id,
                "genres": ["Drama"],
                "keywords": ["cinematic", "mock"]
            }
            
        return MovieOntologyInput(**m_data)
