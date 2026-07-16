import json
import re
from typing import List, Dict, Any
from app.core.interfaces.llm import BaseLLMProvider
from app.schemas.ontology import MovieOntologyInput, SceneSchema, DialogueSchema, CastSchema
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger("app.ingestion.enrichment")

class MovieEnricher:
    """
    Enriches basic TMDb movie metadata with deep cinematic features.
    Supports real LLM generation or dynamic high-quality mock fallbacks.
    """
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    def enrich_movie(self, movie: MovieOntologyInput) -> MovieOntologyInput:
        """
        Enrich a movie payload using the LLM provider or fallback mock logic.
        This is a non-blocking step and fails gracefully.
        """
        logger.info(f"Initiating semantic enrichment for movie: '{movie.title}' (ID: {movie.tmdb_id})")
        
        # Check if we should use mock logic
        is_mock_llm = settings.LLM_PROVIDER.lower().strip() == "mock"
        
        if is_mock_llm:
            logger.info("LLM Provider is configured as MOCK. Executing mock enricher...")
            enriched_data = self._generate_mock_enrichment(movie)
        else:
            try:
                enriched_data = self._generate_llm_enrichment(movie)
            except Exception as e:
                logger.error(f"LLM enrichment failed for movie '{movie.title}': {e}. Falling back to clean mock generation.")
                enriched_data = self._generate_mock_enrichment(movie)
                
        # Merge enriched data into the base movie payload
        return self._merge_enrichment(movie, enriched_data)

    def _generate_llm_enrichment(self, movie: MovieOntologyInput) -> Dict[str, Any]:
        """
        Query the configured LLM provider to extract deep cinematic structures.
        """
        # Build prompt listing genres, overview, keywords, cast, crew
        cast_chars = ", ".join([f"{c.person_name} as {c.character_name}" for c in movie.cast[:5]])
        crew_jobs = ", ".join([f"{cr.person_name} ({cr.job})" for cr in movie.crew[:3]])
        
        prompt = f"""
You are an expert film scholar and cinematic database editor. Analyze the following movie:
Title: {movie.title}
Release Year: {movie.release_year}
Genres: {", ".join(movie.genres)}
Keywords: {", ".join(movie.keywords)}
Cast: {cast_chars}
Crew: {crew_jobs}
Overview: {movie.overview}

Enrich this movie with deep narrative, visual, and symbolic metadata. You MUST respond with a single, valid JSON object following EXACTLY this schema:
{{
  "story_arc": "Brief description of the structure of the narrative arc",
  "beginning": "Overview of the introduction/setup",
  "middle": "Overview of the confrontation/rising action",
  "climax": "Overview of the climax",
  "ending": "Overview of the resolution",
  "ending_type": "Ambiguous, Happy, Tragical, Cliffhanger, Twist, or Open",
  "timeline": "Chronological, Non-linear, Flashbacks, or Time-loop",
  "twists": ["Major plot twist 1", "Major plot twist 2"],
  "conflicts": ["Primary conflict 1", "Secondary conflict 2"],
  "subplots": ["Subplot A", "Subplot B"],
  "themes": ["Theme A", "Theme B"],
  "moods": ["Mood A", "Mood B"],
  "emotions": ["Emotion A", "Emotion B"],
  "memory_cues": ["Uniquely memorable scene or object recall cue 1", "Recall cue 2"],
  "visual_cues": ["Visual cue 1", "Visual cue 2"],
  "color_palette": ["Dominant color 1", "Dominant color 2"],
  "cinematography_style": "Style description (e.g. handheld, wide-angle, static)",
  "camera_style": "Camera movement description (e.g. tracking shots, steady)",
  "lighting": "Lighting description (e.g. low-key noir, high-key bright, natural)",
  "symbolism": ["Symbol name and what it represents"],
  "visual_motifs": ["Motif 1", "Motif 2"],
  "recurring_imagery": ["Imagery 1"],
  "scenes": [
    {{
      "description": "Short name/description of a key iconic scene",
      "summary": "Full detailed summary of what occurs in this scene",
      "location": "Physical setting of this scene",
      "participating_characters": ["Character name 1", "Character name 2"],
      "emotions": ["Suspense", "Awe"],
      "narrative_importance": "Why this scene matters to the overall story",
      "scene_type": "exposition, action, dialogue, suspense, or climax",
      "memorable_events": ["Key event A"],
      "objects": ["important object name"],
      "symbols": ["symbol name"],
      "dialogues": [
        {{
          "character_name": "Speaker character name",
          "text": "Exact or closely paraphrased dialogue line",
          "listener": "Listener character name",
          "meaning": "What this dialogue reveals plot-wise",
          "emotional_tone": "Tense, emotional, cold, etc.",
          "subtext": "The hidden psychological meaning under the line"
        }}
      ]
    }}
  ]
}}

Do NOT include any markdown code blocks, backticks (```json), or extra text in your output. Return ONLY the raw JSON string.
"""
        logger.info(f"Querying LLM for cinematic analysis prompt...")
        llm_response = self.llm.generate(prompt)
        
        # Clean response in case LLM wrapped it in markdown code blocks
        clean_json = re.sub(r"^```(?:json)?\s*", "", llm_response, flags=re.IGNORECASE)
        clean_json = re.sub(r"\s*```$", "", clean_json)
        clean_json = clean_json.strip()
        
        return json.loads(clean_json)

    def _generate_mock_enrichment(self, movie: MovieOntologyInput) -> Dict[str, Any]:
        """
        Generate a dynamic, high-quality mock enrichment payload if offline.
        Uses hardcoded rich cinematic elements for Inception/Interstellar,
        and derives sensible heuristic fallbacks for any other movie.
        """
        title_lower = movie.title.lower()
        
        # 1. Check for Inception (ID: 27205)
        if "inception" in title_lower or movie.tmdb_id == "27205":
            return {
                "story_arc": "A complex five-layer dream heist mirroring the steps of film production.",
                "beginning": "Dom Cobb washing ashore on a beach, meeting an elderly Saito, before waking up in a double-layer dream heist that fails.",
                "middle": "Cobb recruits Ariadne as the dream architect, builds a team, plans the inception heist on Robert Fischer, and descends through the rain-soaked city and hotel dream layers.",
                "climax": "The rotating hallway gravity fight and the snow fortress assault, followed by Cobb descending into Limbo to find Saito.",
                "ending": "Cobb wakes up on the plane, passes customs, returns home, and spins his top totem—leaving the scene before it falls.",
                "ending_type": "Ambiguous",
                "timeline": "Non-linear",
                "twists": [
                    "Cobb was the one who performed inception on his wife Mal, which drove her to commit suicide.",
                    "Saito grows extremely old in Limbo because of time dilation differences across dream layers."
                ],
                "conflicts": [
                    "Man vs Self: Cobb fighting his projection of Mal which represents his deep guilt.",
                    "Man vs Society: Cobb being an exiled fugitive unable to see his children."
                ],
                "subplots": [
                    "Robert Fischer reconciling with his dying father Maurice through a manufactured catharsis.",
                    "Ariadne exploring Cobb's subconscious vault of memories."
                ],
                "themes": ["Grief and Guilt", "Subjectivity of Reality", "Catharsis of Reconciliation"],
                "moods": ["Atmospheric", "Intense", "Mind-bending", "Tense"],
                "emotions": ["Intrigue", "Suspense", "Melancholy", "Wonder"],
                "memory_cues": [
                    "A spinning silver top that never stops falling",
                    "A brass wedding ring that Cobb only wears while dreaming"
                ],
                "visual_cues": [
                    "Paris streets folding in on themselves like a mirror",
                    "Cool blue clinical office lighting contrasted with warm amber dream hotel interiors"
                ],
                "color_palette": ["steel blue", "deep amber", "snow white", "charcoal"],
                "cinematography_style": "Sleek, high-contrast anamorphic widescreen photography with wide-angle spatial depth.",
                "camera_style": "Sweeping crane movements, tracking steadycam shots, and handheld action framing.",
                "lighting": "High-contrast low-key lighting in corporate settings, shifting to warm natural lighting in Limbo.",
                "symbolism": ["The spinning top represents Cobb's sanity and attachment to reality"],
                "visual_motifs": ["Water/rain as a trigger for waking up", "elevators descending into subconscious memory floors"],
                "recurring_imagery": ["spinning totems", "shattering glass", "trains crashing through city streets"],
                "scenes": [
                    {
                        "description": "Cobb teaches Ariadne dream architecture, causing Paris to fold in on itself",
                        "summary": "Dom Cobb demonstrates how dream worlds are built by training Ariadne in a Parisian cafe, showing her how thoughts can bend physics, eventually folding the entire Parisian street grid overhead.",
                        "location": "Paris Cafe / Subconscious Street",
                        "participating_characters": ["Cobb", "Ariadne"],
                        "emotions": ["Awe", "Intrigue"],
                        "narrative_importance": "Establishes the rules of dream manipulation and structural boundaries.",
                        "scene_type": "exposition",
                        "memorable_events": ["Paris street folding over itself"],
                        "objects": ["Cafe table", "mirrors"],
                        "symbols": ["folded city grid"],
                        "dialogues": [
                            {
                                "character_name": "Cobb",
                                "text": "You create the world of the dream. We bring the subject into that dream, and they fill it with their subconscious.",
                                "listener": "Ariadne",
                                "meaning": "Explains the division of labor in the heist: architect builds the maze, subject populates it.",
                                "emotional_tone": "Tense",
                                "subtext": "Cobb is withholding that his own subconscious projection of Mal will invade the maze."
                            }
                        ]
                    }
                ]
            }

        # 2. Check for Interstellar (ID: 157336)
        elif "interstellar" in title_lower or movie.tmdb_id == "157336":
            return {
                "story_arc": "An epic space odyssey structured around relativity, gravity, and father-daughter bonds.",
                "beginning": "A dying Earth plagued by crop blight, forcing former pilot Cooper to discover a secret NASA facility.",
                "middle": "Cooper leaves his family to pilot the Endurance through a wormhole, visiting Miller's water planet and Mann's ice world.",
                "climax": "Cooper ejects into the black hole Gargantua's event horizon, entering a five-dimensional tesseract.",
                "ending": "Cooper communicates gravity data to his daughter Murphy, wakes up on a space colony, and reunites with an elderly Murph.",
                "ending_type": "Happy",
                "timeline": "Non-linear",
                "twists": [
                    "The wormhole was not placed by aliens, but by future humans who evolved to master five dimensions.",
                    "Professor Brand lied about Plan A, knowing the gravity equations could never be solved without black hole data."
                ],
                "conflicts": [
                    "Man vs Nature: Humanity struggling to survive against a dying planetary ecosystem.",
                    "Man vs Time: Cooper battling the devastating effects of time dilation."
                ],
                "subplots": [
                    "Murphy growing up to become a scientist under Professor Brand's tutelage.",
                    "Dr. Mann's psychological breakdown and desperate betrayal of the mission."
                ],
                "themes": ["Love Transcending Dimensions", "Sacrifice for the Species", "Limits of Human Isolation"],
                "moods": ["Epic", "Melancholy", "Awe-inspiring"],
                "emotions": ["Sadness", "Awe", "Excitement", "Hope"],
                "memory_cues": [
                    "A ticking wristwatch second hand spelling out coordinates in Morse code",
                    "A massive black hole with a glowing accretion disk"
                ],
                "visual_cues": [
                    "Dust storms swallowing agricultural farmhouses",
                    "Infinite tesseract grids folding across bookshelves"
                ],
                "color_palette": ["dusty brown", "nasa silver", "space black", "icy white"],
                "cinematography_style": "Grand scale widescreen photography mixing documentary-like IMAX footage with CGI.",
                "camera_style": "Steadicam shots, mount-fixed spacecraft cameras, and slow-pacing panoramas.",
                "lighting": "Natural sun flare, harsh stellar reflections in vacuums, and amber-toned cabin glow.",
                "symbolism": ["The watch symbolizes the emotional tether of time connecting Cooper and Murphy"],
                "visual_motifs": ["Dust as a timer of dying Earth", "cornfields representing agricultural survival"],
                "recurring_imagery": ["ticking clocks", "wormholes", "black holes", "tidal waves"],
                "scenes": [
                    {
                        "description": "Cooper enters the Tesseract",
                        "summary": "Cooper ejects from his spaceship into the center of the Gargantua black hole and finds himself in a multi-dimensional bookcase structure that overlooks his daughter's bedroom at various points in time.",
                        "location": "Tesseract (Sub-dimensional space)",
                        "participating_characters": ["Cooper", "TARS"],
                        "emotions": ["Wonder", "Grief"],
                        "narrative_importance": "Resolves the gravitational query and connects the past and future timelines.",
                        "scene_type": "climax",
                        "memorable_events": ["Cooper communicating via Morse code watch"],
                        "objects": ["Wristwatch", "Books"],
                        "symbols": ["The bookcase as time's physical representation"],
                        "dialogues": [
                            {
                                "character_name": "Cooper",
                                "text": "Love, TARS. It's the one thing we're capable of perceiving that transcends dimensions of time and space.",
                                "listener": "TARS",
                                "meaning": "Asserts the core thesis of the film: human emotion is a quantifiable force.",
                                "emotional_tone": "Emotional",
                                "subtext": "Cooper realizes his love for Murph is the key to navigating the Tesseract."
                            }
                        ]
                    }
                ]
            }

        # 3. Dynamic Heuristic Fallback (For any other movie)
        else:
            first_sentence = movie.overview.split(".")[0] if movie.overview else "A compelling story of struggle and conflict."
            char_names = [c.character_name for c in movie.cast[:3]] if movie.cast else ["Protagonist"]
            director = next((cr.person_name for cr in movie.crew if cr.job == "Director"), "the Director")
            
            return {
                "story_arc": f"A traditional three-act narrative centered on the journey of {', '.join(char_names[:2])}.",
                "beginning": f"Introduces the setting and core characters, leading up to the inciting incident: {first_sentence}.",
                "middle": f"Rising action as the characters encounter conflicts, leading to escalating stakes and personal growth.",
                "climax": "A dramatic final confrontation where the primary themes and character motivations collide.",
                "ending": "A resolution resolving the primary character arcs and bringing closure to the story.",
                "ending_type": "Open",
                "timeline": "Chronological",
                "twists": ["A key reveal that shifts the main characters' perspectives on their objective."],
                "conflicts": [f"Man vs Circumstance: Characters struggle with the core conflict of '{movie.title}'."],
                "subplots": ["A secondary storyline exploring relationships and secondary character growth."],
                "themes": ["Identity", "Choice", "Consequences of Action"],
                "moods": ["Cinematic", "Atmospheric"],
                "emotions": ["Intrigue", "Suspense"],
                "memory_cues": [f"An iconic item or scene that represents the struggle in '{movie.title}'."],
                "visual_cues": [f"Stylistic visual direction reflecting the tone of '{movie.title}'."],
                "color_palette": ["cool steel", "warm amber"],
                "cinematography_style": "Contemporary cinematic staging with standard camera coverage.",
                "camera_style": "Steadicam and tripod-fixed pans.",
                "lighting": "Natural lighting suited to the dramatic setting.",
                "symbolism": ["A key object symbol representing character freedom"],
                "visual_motifs": ["Contrasting shadows highlighting emotional shifts"],
                "recurring_imagery": ["reflections in glass"],
                "scenes": [
                    {
                        "description": f"The pivotal confrontation scene in '{movie.title}'",
                        "summary": f"The main characters meet to resolve their differences and face the reality of the situation.",
                        "location": "Dramatic location set",
                        "participating_characters": char_names[:2],
                        "emotions": ["Tension"],
                        "narrative_importance": "Drives the characters toward the final act resolution.",
                        "scene_type": "dialogue",
                        "memorable_events": ["Key dialogue exchange"],
                        "objects": ["pivotal item"],
                        "symbols": ["confrontation setting"],
                        "dialogues": [
                            {
                                "character_name": char_names[0] if char_names else "Protagonist",
                                "text": "We have to see this through to the end, no matter what.",
                                "listener": char_names[1] if len(char_names) > 1 else "Antagonist",
                                "meaning": "Highlights the commitment of the protagonist to resolving the conflict.",
                                "emotional_tone": "Tense",
                                "subtext": "Expresses fear of failure combined with duty."
                            }
                        ]
                    }
                ]
            }

    def _merge_enrichment(self, movie: MovieOntologyInput, enriched: Dict[str, Any]) -> MovieOntologyInput:
        """
        Merge the generated enrichment dictionary back into a new MovieOntologyInput.
        """
        # Parse scenes
        cleaned_scenes = []
        for s in enriched.get("scenes", []):
            dialogues = []
            for d in s.get("dialogues", []):
                dialogues.append(DialogueSchema(
                    character_name=d.get("character_name", "Character"),
                    text=d.get("text", ""),
                    speaker=d.get("character_name"),
                    listener=d.get("listener"),
                    meaning=d.get("meaning"),
                    emotional_tone=d.get("emotional_tone"),
                    subtext=d.get("subtext")
                ))
            
            cleaned_scenes.append(SceneSchema(
                description=s.get("description", "Scene"),
                summary=s.get("summary"),
                location=s.get("location"),
                participating_characters=s.get("participating_characters", []),
                emotions=s.get("emotions", []),
                narrative_importance=s.get("narrative_importance"),
                scene_type=s.get("scene_type"),
                memorable_events=s.get("memorable_events", []),
                dialogues=dialogues,
                objects=s.get("objects", []),
                symbols=s.get("symbols", [])
            ))

        # Copy original movie data, overriding enriched lists
        original_data = movie.model_dump()
        
        # Override thematic arrays (union lists to preserve TMDb items)
        original_data["themes"] = list(set(movie.themes + enriched.get("themes", [])))
        original_data["moods"] = list(set(movie.moods + enriched.get("moods", [])))
        original_data["emotions"] = list(set(movie.emotions + enriched.get("emotions", [])))
        original_data["memory_cues"] = list(set(movie.memory_cues + enriched.get("memory_cues", [])))
        original_data["visual_cues"] = list(set(movie.visual_cues + enriched.get("visual_cues", [])))
        
        # Set narrative details
        original_data["plot"] = enriched.get("plot")
        original_data["plot_summary"] = enriched.get("plot_summary")
        original_data["beginning"] = enriched.get("beginning")
        original_data["middle"] = enriched.get("middle")
        original_data["climax"] = enriched.get("climax")
        original_data["ending"] = enriched.get("ending")
        original_data["ending_type"] = enriched.get("ending_type")
        original_data["timeline"] = enriched.get("timeline")
        original_data["story_arcs"] = list(set(movie.story_arcs + [enriched.get("story_arc")] if enriched.get("story_arc") else movie.story_arcs))
        
        original_data["twists"] = enriched.get("twists", [])
        original_data["conflicts"] = enriched.get("conflicts", [])
        original_data["subplots"] = enriched.get("subplots", [])
        
        # Set visual details
        original_data["color_palette"] = enriched.get("color_palette", [])
        original_data["cinematography_style"] = enriched.get("cinematography_style")
        original_data["camera_style"] = enriched.get("camera_style")
        original_data["lighting"] = enriched.get("lighting")
        original_data["symbolism"] = enriched.get("symbolism", [])
        original_data["visual_motifs"] = enriched.get("visual_motifs", [])
        original_data["recurring_imagery"] = enriched.get("recurring_imagery", [])
        
        # Overwrite scenes list
        original_data["scenes"] = cleaned_scenes

        return MovieOntologyInput(**original_data)
