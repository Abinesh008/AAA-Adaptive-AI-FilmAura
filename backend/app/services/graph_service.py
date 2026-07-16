from typing import List, Dict, Any, Tuple
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.schemas.ontology import MovieOntologyInput
from app.core.logging import get_logger
from datetime import datetime

logger = get_logger("app.services.graph_service")

class GraphService:
    """
    Manages schemas, constraints, indices, and Cypher population operations for Neo4j.
    """
    def __init__(self, graph_db: BaseKnowledgeGraph):
        self.db = graph_db

    def initialize_schema(self) -> None:
        """
        Create uniqueness constraints and indexes on startup to ensure graph integrity.
        """
        logger.info("Initializing Neo4j Knowledge Graph schemas and constraints...")
        
        # Define constraints
        constraints = [
            ("CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE", "Movie ID Constraint"),
            ("CREATE CONSTRAINT person_id_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE", "Person ID Constraint"),
            ("CREATE CONSTRAINT genre_name_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE", "Genre Name Constraint"),
            ("CREATE CONSTRAINT theme_name_unique IF NOT EXISTS FOR (t:Theme) REQUIRE t.name IS UNIQUE", "Theme Name Constraint"),
            ("CREATE CONSTRAINT emotion_name_unique IF NOT EXISTS FOR (e:Emotion) REQUIRE e.name IS UNIQUE", "Emotion Name Constraint"),
            ("CREATE CONSTRAINT mood_name_unique IF NOT EXISTS FOR (mo:Mood) REQUIRE mo.name IS UNIQUE", "Mood Name Constraint"),
            ("CREATE CONSTRAINT keyword_name_unique IF NOT EXISTS FOR (k:Keyword) REQUIRE k.name IS UNIQUE", "Keyword Name Constraint"),
            ("CREATE CONSTRAINT object_name_unique IF NOT EXISTS FOR (o:Object) REQUIRE o.name IS UNIQUE", "Object Name Constraint"),
            ("CREATE CONSTRAINT symbol_name_unique IF NOT EXISTS FOR (s:Symbol) REQUIRE s.name IS UNIQUE", "Symbol Name Constraint"),
            ("CREATE CONSTRAINT franchise_name_unique IF NOT EXISTS FOR (f:Franchise) REQUIRE f.name IS UNIQUE", "Franchise Name Constraint"),
            ("CREATE CONSTRAINT studio_name_unique IF NOT EXISTS FOR (s:Studio) REQUIRE s.name IS UNIQUE", "Studio Name Constraint"),
            ("CREATE CONSTRAINT provider_name_unique IF NOT EXISTS FOR (sp:StreamingProvider) REQUIRE sp.name IS UNIQUE", "StreamingProvider Name Constraint"),
            ("CREATE CONSTRAINT scene_id_unique IF NOT EXISTS FOR (s:Scene) REQUIRE s.id IS UNIQUE", "Scene ID Constraint"),
            ("CREATE CONSTRAINT dialogue_id_unique IF NOT EXISTS FOR (d:Dialogue) REQUIRE d.id IS UNIQUE", "Dialogue ID Constraint")
        ]
        
        for cypher, desc in constraints:
            try:
                self.db.execute_query(cypher)
                logger.debug(f"Neo4j schema: {desc} initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to create constraint ({desc}): {e}")

    def populate_movie(self, movie: MovieOntologyInput) -> None:
        """
        Populate a single movie and its entire ontology structure inside a Neo4j transaction.
        """
        logger.info(f"Populating Neo4j Knowledge Graph for: '{movie.title}' (ID: {movie.tmdb_id})")
        
        queries: List[Tuple[str, Dict[str, Any]]] = []
        
        # 1. Create/Update Movie node
        movie_cypher = (
            "MERGE (m:Movie {id: $tmdb_id}) "
            "SET m.title = $title, m.overview = $overview, m.year = $year, m.runtime = $runtime, "
            "    m.language = $language, m.country = $country, m.imdb_id = $imdb_id, "
            "    m.wikidata_id = $wikidata_id, m.tvdb_id = $tvdb_id, m.original_title = $original_title, "
            "    m.release_date = $release_date, m.budget = $budget, m.revenue = $revenue, "
            "    m.tagline = $tagline, m.status = $status, m.adult = $adult, m.popularity = $popularity, "
            "    m.vote_average = $vote_average, m.vote_count = $vote_count, m.plot = $plot, "
            "    m.plot_summary = $plot_summary, m.story_arc = $story_arc, m.ending_type = $ending_type, "
            "    m.timeline = $timeline, m.last_synced_at = $last_synced_at"
        )
        movie_params = {
            "tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "overview": movie.overview,
            "year": movie.release_year,
            "runtime": movie.runtime,
            "language": movie.language,
            "country": movie.country,
            "imdb_id": movie.imdb_id,
            "wikidata_id": movie.wikidata_id,
            "tvdb_id": movie.tvdb_id,
            "original_title": movie.original_title or movie.title,
            "release_date": movie.release_date,
            "budget": movie.budget,
            "revenue": movie.revenue,
            "tagline": movie.tagline,
            "status": movie.status or "Released",
            "adult": movie.adult,
            "popularity": movie.popularity,
            "vote_average": movie.vote_average,
            "vote_count": movie.vote_count,
            "plot": movie.plot,
            "plot_summary": movie.plot_summary,
            "story_arc": movie.story_arcs[0] if movie.story_arcs else None,
            "ending_type": movie.ending_type,
            "timeline": movie.timeline,
            "last_synced_at": datetime.utcnow().isoformat()
        }
        queries.append((movie_cypher, movie_params))

        # Clear existing non-structural relations (like genres, keywords, themes, emotions, moods, streaming, studios) 
        # to prevent ghost relations on updates
        clear_cypher = (
            "MATCH (m:Movie {id: $tmdb_id}) "
            "OPTIONAL MATCH (m)-[r:BELONGS_TO_GENRE|HAS_KEYWORD|HAS_THEME|HAS_EMOTION|HAS_MOOD|PRODUCED_BY|AVAILABLE_ON|PART_OF_FRANCHISE|HAS_MEMORY_CUE|HAS_VISUAL_CUE]->() "
            "DELETE r"
        )
        queries.append((clear_cypher, {"tmdb_id": movie.tmdb_id}))

        # 2. Link Genres
        for genre in movie.genres:
            genre_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (g:Genre {name: $genre_name}) "
                "MERGE (m)-[:BELONGS_TO_GENRE]->(g)"
            )
            queries.append((genre_cypher, {"tmdb_id": movie.tmdb_id, "genre_name": genre}))

        # 3. Link Keywords
        for kw in movie.keywords:
            kw_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (k:Keyword {name: $kw_name}) "
                "MERGE (m)-[:HAS_KEYWORD]->(k)"
            )
            queries.append((kw_cypher, {"tmdb_id": movie.tmdb_id, "kw_name": kw}))

        # 4. Link Themes
        for theme in movie.themes:
            theme_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (t:Theme {name: $theme_name}) "
                "MERGE (m)-[:HAS_THEME]->(t)"
            )
            queries.append((theme_cypher, {"tmdb_id": movie.tmdb_id, "theme_name": theme}))

        # 5. Link Emotions
        for emotion in movie.emotions:
            emotion_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (e:Emotion {name: $emotion_name}) "
                "MERGE (m)-[:HAS_EMOTION]->(e)"
            )
            queries.append((emotion_cypher, {"tmdb_id": movie.tmdb_id, "emotion_name": emotion}))

        # 6. Link Moods
        for mood in movie.moods:
            mood_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (mo:Mood {name: $mood_name}) "
                "MERGE (m)-[:HAS_MOOD]->(mo)"
            )
            queries.append((mood_cypher, {"tmdb_id": movie.tmdb_id, "mood_name": mood}))

        # 7. Link Studios
        for studio in movie.studios:
            studio_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (s:Studio {name: $studio_name}) "
                "MERGE (m)-[:PRODUCED_BY]->(s)"
            )
            queries.append((studio_cypher, {"tmdb_id": movie.tmdb_id, "studio_name": studio}))

        # 8. Link Streaming Providers
        for sp in movie.streaming_providers:
            provider_name = sp.get("name")
            if provider_name:
                sp_cypher = (
                    "MATCH (m:Movie {id: $tmdb_id}) "
                    "MERGE (p:StreamingProvider {name: $provider_name}) "
                    "MERGE (m)-[:AVAILABLE_ON {availability: $avail, region: $region}]->(p)"
                )
                queries.append((sp_cypher, {
                    "tmdb_id": movie.tmdb_id,
                    "provider_name": provider_name,
                    "avail": sp.get("availability", "subscription"),
                    "region": sp.get("region", "US")
                }))

        # 9. Link Franchise
        if movie.franchise:
            franchise_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (f:Franchise {name: $franchise_name}) "
                "MERGE (m)-[:PART_OF_FRANCHISE]->(f)"
            )
            queries.append((franchise_cypher, {"tmdb_id": movie.tmdb_id, "franchise_name": movie.franchise}))

        # 10. Link Cast (Actors) with character traits
        # Clean existing ACTED_IN relationships for this movie to prevent duplication/ghosts
        queries.append((
            "MATCH (m:Movie {id: $tmdb_id})-[r:ACTED_IN]->() DELETE r",
            {"tmdb_id": movie.tmdb_id}
        ))
        for idx, cast_member in enumerate(movie.cast):
            cast_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (p:Person {id: $person_id}) ON CREATE SET p.name = $name "
                "MERGE (m)-[r:ACTED_IN]->(p) "
                "SET r.character = $character, r.billing_order = $order, r.importance = $importance, "
                "    r.personality_traits = $traits, r.motivations = $motivations, r.arc = $arc"
            )
            queries.append((cast_cypher, {
                "tmdb_id": movie.tmdb_id,
                "person_id": cast_member.external_person_id,
                "name": cast_member.person_name,
                "character": cast_member.character_name,
                "order": idx,
                "importance": cast_member.importance or "supporting",
                "traits": cast_member.personality_traits,
                "motivations": cast_member.motivations,
                "arc": cast_member.arc or ""
            }))

        # 11. Link Crew (Directors, Writers, Composers, etc.)
        # Clean existing crew relationships for this movie
        queries.append((
            "MATCH (m:Movie {id: $tmdb_id})-[r:DIRECTED|PRODUCED|WROTE|COMPOSED]->() DELETE r",
            {"tmdb_id": movie.tmdb_id}
        ))
        for crew_member in movie.crew:
            job_lower = crew_member.job.lower().strip()
            rel_type = "DIRECTED"
            if "director" in job_lower:
                rel_type = "DIRECTED"
            elif "producer" in job_lower:
                rel_type = "PRODUCED"
            elif "writer" in job_lower or "screenplay" in job_lower:
                rel_type = "WROTE"
            elif "composer" in job_lower or "music" in job_lower:
                rel_type = "COMPOSED"
            else:
                # Default to fallback role relation
                rel_type = "HAS_CREW"
                
            crew_cypher = (
                f"MATCH (m:Movie {{id: $tmdb_id}}) "
                f"MERGE (p:Person {{id: $person_id}}) ON CREATE SET p.name = $name "
                f"MERGE (p)-[r:{rel_type}]->(m) "
                f"SET r.job = $job, r.department = $dept"
            )
            queries.append((crew_cypher, {
                "tmdb_id": movie.tmdb_id,
                "person_id": crew_member.external_person_id,
                "name": crew_member.person_name,
                "job": crew_member.job,
                "dept": crew_member.department
            }))

        # 12. Link Memory Cues
        for cue in movie.memory_cues:
            cue_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (mc:MemoryCue {description: $desc}) "
                "MERGE (m)-[:HAS_MEMORY_CUE]->(mc)"
            )
            queries.append((cue_cypher, {"tmdb_id": movie.tmdb_id, "desc": cue}))

        # 13. Link Visual Cues
        for cue in movie.visual_cues:
            cue_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (vc:VisualCue {description: $desc}) "
                "MERGE (m)-[:HAS_VISUAL_CUE]->(vc)"
            )
            queries.append((cue_cypher, {"tmdb_id": movie.tmdb_id, "desc": cue}))

        # 14. Link Scenes, Objects, Symbols, and dialogues (Idempotent updates)
        # Clear existing scene nodes and dialogues linked to this movie to prevent duplication
        clear_scenes_cypher = (
            "MATCH (m:Movie {id: $tmdb_id})-[:HAS_SCENE]->(s:Scene) "
            "OPTIONAL MATCH (s)-[:HAS_DIALOGUE]->(d:Dialogue) "
            "DETACH DELETE s, d"
        )
        queries.append((clear_scenes_cypher, {"tmdb_id": movie.tmdb_id}))

        for scene_idx, scene in enumerate(movie.scenes):
            scene_node_id = f"{movie.tmdb_id}_scene_{scene_idx}"
            scene_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (s:Scene {id: $scene_node_id}) "
                "SET s.description = $desc, s.summary = $summary, s.location = $location, "
                "    s.importance = $importance, s.type = $scene_type "
                "MERGE (m)-[:HAS_SCENE {scene_index: $idx}]->(s)"
            )
            queries.append((scene_cypher, {
                "tmdb_id": movie.tmdb_id,
                "scene_node_id": scene_node_id,
                "desc": scene.description,
                "summary": scene.summary or scene.description,
                "location": scene.location or "Unknown",
                "importance": scene.narrative_importance or "",
                "scene_type": scene.scene_type or "dialogue",
                "idx": scene_idx
            }))
            
            # Link Scene Objects
            for obj in scene.objects:
                obj_cypher = (
                    "MATCH (s:Scene {id: $scene_node_id}) "
                    "MERGE (o:Object {name: $obj_name}) "
                    "MERGE (s)-[:HAS_OBJECT]->(o)"
                )
                queries.append((obj_cypher, {
                    "scene_node_id": scene_node_id,
                    "obj_name": obj
                }))
                
            # Link Scene Symbols
            for symbol in scene.symbols:
                sym_cypher = (
                    "MATCH (s:Scene {id: $scene_node_id}) "
                    "MERGE (sy:Symbol {name: $sym_name}) "
                    "MERGE (s)-[:HAS_SYMBOL]->(sy)"
                )
                queries.append((sym_cypher, {
                    "scene_node_id": scene_node_id,
                    "sym_name": symbol
                }))

            # Link Scene Locations
            if scene.location:
                loc_cypher = (
                    "MATCH (s:Scene {id: $scene_node_id}) "
                    "MERGE (l:Location {name: $loc_name}) "
                    "MERGE (s)-[:LOCATED_IN]->(l)"
                )
                queries.append((loc_cypher, {
                    "scene_node_id": scene_node_id,
                    "loc_name": scene.location
                }))

            # Link Dialogues inside the scene
            for d_idx, d in enumerate(scene.dialogues):
                dialogue_node_id = f"{scene_node_id}_dial_{d_idx}"
                dial_cypher = (
                    "MATCH (s:Scene {id: $scene_node_id}) "
                    "MERGE (d:Dialogue {id: $dial_node_id}) "
                    "SET d.speaker = $speaker, d.listener = $listener, d.text = $text, "
                    "    d.meaning = $meaning, d.emotional_tone = $tone, d.subtext = $subtext "
                    "MERGE (s)-[:HAS_DIALOGUE]->(d)"
                )
                queries.append((dial_cypher, {
                    "scene_node_id": scene_node_id,
                    "dial_node_id": dialogue_node_id,
                    "speaker": d.speaker or d.character_name,
                    "listener": d.listener or "Unknown",
                    "text": d.text,
                    "meaning": d.meaning or "",
                    "tone": d.emotional_tone or "neutral",
                    "subtext": d.subtext or ""
                }))

        # 15. Contextual Elements (Locations and Historical periods)
        for loc in movie.locations:
            loc_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (l:Location {name: $loc_name}) "
                "MERGE (m)-[:LOCATED_IN]->(l)"
            )
            queries.append((loc_cypher, {"tmdb_id": movie.tmdb_id, "loc_name": loc}))
            
        for period in movie.historical_periods:
            period_cypher = (
                "MATCH (m:Movie {id: $tmdb_id}) "
                "MERGE (hp:HistoricalPeriod {name: $period_name}) "
                "MERGE (m)-[:OCCURS_IN_PERIOD]->(hp)"
            )
            queries.append((period_cypher, {"tmdb_id": movie.tmdb_id, "period_name": period}))

        # Run transaction
        self.db.run_transaction(queries)
        logger.info(f"Base graph transaction committed successfully for '{movie.title}'")

        # 16. Post Ingestion Similarity Linkages
        self._populate_similarity_linkages(movie.tmdb_id)

    def _populate_similarity_linkages(self, movie_id: str) -> None:
        """
        Dynamically run queries to build SIMILAR_THEME, SIMILAR_MOOD, and SIMILAR_EMOTION links
        between the updated movie node and other existing movie nodes.
        """
        logger.info(f"Recalculating similarity linkages for Movie ID {movie_id}...")
        
        queries = [
            # Link similar themes (movies sharing 2+ themes)
            ("""
            MATCH (m1:Movie {id: $movie_id})-[:HAS_THEME]->(t:Theme)<-[:HAS_THEME]-(m2:Movie)
            WHERE m1 <> m2
            WITH m1, m2, count(t) as shared_count
            WHERE shared_count >= 2
            MERGE (m1)-[r:SIMILAR_THEME]-(m2)
            SET r.shared_themes_count = shared_count
            """, {"movie_id": movie_id}),
            
            # Link similar moods (movies sharing 2+ moods)
            ("""
            MATCH (m1:Movie {id: $movie_id})-[:HAS_MOOD]->(mo:Mood)<-[:HAS_MOOD]-(m2:Movie)
            WHERE m1 <> m2
            WITH m1, m2, count(mo) as shared_count
            WHERE shared_count >= 2
            MERGE (m1)-[r:SIMILAR_MOOD]-(m2)
            SET r.shared_moods_count = shared_count
            """, {"movie_id": movie_id}),
            
            # Link similar emotions (movies sharing 2+ emotions)
            ("""
            MATCH (m1:Movie {id: $movie_id})-[:HAS_EMOTION]->(e:Emotion)<-[:HAS_EMOTION]-(m2:Movie)
            WHERE m1 <> m2
            WITH m1, m2, count(e) as shared_count
            WHERE shared_count >= 2
            MERGE (m1)-[r:SIMILAR_EMOTION]-(m2)
            SET r.shared_emotions_count = shared_count
            """, {"movie_id": movie_id})
        ]
        
        for cypher, params in queries:
            try:
                self.db.execute_query(cypher, params)
            except Exception as e:
                logger.warning(f"Failed to generate similarity relationship: {e}")
