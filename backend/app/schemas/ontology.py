from pydantic import BaseModel, Field
from typing import List, Dict, Any

class CastSchema(BaseModel):
    character_name: str
    person_name: str
    external_person_id: str
    
    # Extended Character traits
    aliases: List[str] = []
    biography: str | None = None
    importance: str | None = "supporting"  # main, supporting, cameo
    relationships: List[Dict[str, Any]] = []  # e.g., [{"target": "Ariadne", "type": "mentor"}]
    personality_traits: List[str] = []
    motivations: List[str] = []
    arc: str | None = None

    # Metadata fields
    confidence_score: float | None = 1.0
    generated_by: str | None = None
    generated_at: str | None = None
    source: str | None = "tmdb"

class CrewSchema(BaseModel):
    person_name: str
    external_person_id: str
    job: str
    department: str

class DialogueSchema(BaseModel):
    character_name: str
    text: str
    speaker: str | None = None
    listener: str | None = None
    meaning: str | None = None
    emotional_tone: str | None = None
    subtext: str | None = None

    # Metadata fields
    confidence_score: float | None = 1.0
    generated_by: str | None = None
    generated_at: str | None = None
    source: str | None = "tmdb"

class SceneSchema(BaseModel):
    description: str
    summary: str | None = None
    location: str | None = None
    participating_characters: List[str] = []
    emotions: List[str] = []
    narrative_importance: str | None = None
    scene_type: str | None = "dialogue"  # action, exposition, climax, suspense, dialogue
    memorable_events: List[str] = []
    dialogues: List[DialogueSchema] = []
    objects: List[str] = []
    symbols: List[str] = []

    # Metadata fields
    confidence_score: float | None = 1.0
    generated_by: str | None = None
    generated_at: str | None = None
    source: str | None = "tmdb"

class AwardSchema(BaseModel):
    name: str
    category: str
    year: int
    winner: bool = True

class MusicSchema(BaseModel):
    track_name: str
    artist: str | None = None
    type: str = "soundtrack"  # soundtrack, score, theme

class ReviewSchema(BaseModel):
    critic_name: str
    rating: float | None = None
    text: str

class MovieOntologyInput(BaseModel):
    """
    Unified validation schema representing the complete hierarchical movie ontology.
    """
    title: str
    overview: str
    release_year: int
    runtime: int | None = None
    language: str | None = "en"
    country: str | None = "US"
    tmdb_id: str  # External primary key
    
    # Universal External Identifiers
    imdb_id: str | None = None
    wikidata_id: str | None = None
    tvdb_id: str | None = None

    # Extended Core Metadata
    original_title: str | None = None
    release_date: str | None = None
    budget: int | None = None
    revenue: int | None = None
    tagline: str | None = None
    status: str | None = "Released"
    adult: bool | None = False
    popularity: float | None = 0.0
    vote_average: float | None = 0.0
    vote_count: int | None = 0

    # Emotional & Categorical taxonomies
    genres: List[str] = []
    subgenres: List[str] = []
    themes: List[str] = []
    emotions: List[str] = []
    moods: List[str] = []
    keywords: List[str] = []
    
    # Cast & Crew structures
    cast: List[CastSchema] = []
    crew: List[CrewSchema] = []
    
    # Narrative elements
    scenes: List[SceneSchema] = []
    story_arcs: List[str] = []
    narrative_styles: List[str] = []
    plot: str | None = None
    plot_summary: str | None = None
    beginning: str | None = None
    middle: str | None = None
    climax: str | None = None
    ending: str | None = None
    ending_type: str | None = None
    timeline: str | None = None
    twists: List[str] = []
    conflicts: List[str] = []
    subplots: List[str] = []

    # Sensory & recall cues
    memory_cues: List[str] = []
    visual_cues: List[str] = []
    music: List[MusicSchema] = []
    
    # Visual Information
    color_palette: List[str] = []
    cinematography_style: str | None = None
    camera_style: str | None = None
    lighting: str | None = None
    symbolism: List[str] = []
    visual_motifs: List[str] = []
    recurring_imagery: List[str] = []

    # Contextual elements
    locations: List[str] = []
    historical_periods: List[str] = []
    awards: List[AwardSchema] = []
    franchises: List[str] = []
    streaming_platforms: List[str] = []
    collections: List[str] = []
    
    # Streaming Provider details (name, availability, region)
    streaming_providers: List[Dict[str, Any]] = []

    # Production
    studios: List[str] = []

    # Franchise/Prequel/Sequel
    franchise: str | None = None
    sequels: List[str] = []
    prequels: List[str] = []
    shared_universe: str | None = None

    # Reviews
    reviews: List[ReviewSchema] = []
    target_audiences: List[str] = []

    # Metadata fields
    confidence_score: float | None = 1.0
    generated_by: str | None = None
    generated_at: str | None = None
    source: str | None = "tmdb"

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Inception",
                "overview": "A thief who steals corporate secrets through the use of dream-sharing technology...",
                "release_year": 2010,
                "runtime": 148,
                "language": "en",
                "country": "US",
                "tmdb_id": "27205",
                "genres": ["Action", "Science Fiction"],
                "subgenres": ["Heist", "Mind-bending"],
                "themes": ["Nature of Reality", "Grief", "Subconscious"],
                "emotions": ["Suspense", "Melancholy"],
                "moods": ["Atmospheric", "Intense"],
                "keywords": ["dream", "subconscious", "heist", "memory"],
                "cast": [
                    {
                        "character_name": "Cobb", 
                        "person_name": "Leonardo DiCaprio", 
                        "external_person_id": "6193",
                        "importance": "main",
                        "personality_traits": ["haunted", "obsessive", "analytical"],
                        "motivations": ["return to his children"]
                    }
                ],
                "crew": [
                    {"person_name": "Christopher Nolan", "external_person_id": "525", "job": "Director", "department": "Directing"}
                ],
                "scenes": [
                    {
                        "description": "The rotating hallway fight scene",
                        "narrative_importance": "Shows the effect of physical gravity changes on subconscious layers",
                        "dialogues": [],
                        "objects": ["spinning top"],
                        "symbols": ["spinning top", "wedding ring"]
                    }
                ],
                "memory_cues": ["A spinning top that never stops falling", "rotating hotel hallway"],
                "visual_cues": ["Folding cityscapes", "cool blue tones", "mirrors"],
                "music": [
                    {"track_name": "Time", "artist": "Hans Zimmer", "type": "score"}
                ]
            }
        }
    }
