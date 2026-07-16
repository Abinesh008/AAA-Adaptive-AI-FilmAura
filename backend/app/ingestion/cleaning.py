import re
import unicodedata
from typing import List, Dict, Any
from app.schemas.ontology import MovieOntologyInput, CastSchema, CrewSchema, MusicSchema, SceneSchema, DialogueSchema, AwardSchema, ReviewSchema
from app.core.logging import get_logger

logger = get_logger("app.ingestion.cleaning")

def normalize_text(text: str | None) -> str:
    """
    Standardize text: perform unicode NFKC normalization, strip whitespaces, remove HTML tags, normalize spacing.
    """
    if not text:
        return ""
    # Unicode NFKC normalization
    normalized = unicodedata.normalize("NFKC", text)
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]*>", "", normalized)
    # Normalize multiple whitespaces and newlines
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()

def normalize_name(name: str | None) -> str:
    """
    Standardize names (Title Case, stripped and normalized).
    """
    if not name:
        return "Unknown"
    cleaned = normalize_text(name)
    # Format Title Case
    return cleaned.title()

def normalize_title(title: str | None) -> str:
    """
    Standardize movie titles: removes appended release year, e.g. "Inception (2010)" -> "Inception".
    """
    if not title:
        return "Untitled Movie"
    cleaned = normalize_text(title)
    # Regex to strip trailing year pattern like " (2010)" or " [2010]"
    cleaned = re.sub(r"\s*[\(\[][0-9]{4}[\)\]]\s*$", "", cleaned)
    return cleaned.strip()

def clean_movie_data(movie: MovieOntologyInput) -> MovieOntologyInput:
    """
    Cleans, validates, and normalizes a MovieOntologyInput payload.
    Resolves aliases, strips excess characters, and handles empty fields.
    """
    logger.info(f"Cleaning movie data for: '{movie.title}' (ID: {movie.tmdb_id})")
    
    # 1. Clean Title and Overview
    cleaned_title = normalize_title(movie.title)
    cleaned_overview = normalize_text(movie.overview)
    
    # 2. Clean taxonomic lists (unique, lowercase/namecase, normalized text)
    cleaned_genres = list(set([normalize_name(g) for g in movie.genres if g]))
    cleaned_subgenres = list(set([normalize_name(sg) for sg in movie.subgenres if sg]))
    cleaned_themes = list(set([normalize_name(t) for t in movie.themes if t]))
    cleaned_emotions = list(set([normalize_name(e) for e in movie.emotions if e]))
    cleaned_moods = list(set([normalize_name(m) for m in movie.moods if m]))
    cleaned_keywords = list(set([normalize_text(k).lower() for k in movie.keywords if k]))
    
    # 3. Clean Cast
    cleaned_cast = []
    seen_cast = set() # Avoid duplicate actors in the same movie
    for actor in movie.cast:
        actor_name = normalize_name(actor.person_name)
        char_name = normalize_name(actor.character_name)
        
        # Unique check by external ID
        if actor.external_person_id not in seen_cast:
            seen_cast.add(actor.external_person_id)
            
            # Clean character subfields
            cleaned_aliases = list(set([normalize_name(a) for a in actor.aliases if a]))
            cleaned_bio = normalize_text(actor.biography) if actor.biography else None
            cleaned_traits = list(set([normalize_text(t).lower() for t in actor.personality_traits if t]))
            cleaned_motivations = list(set([normalize_text(m).lower() for m in actor.motivations if m]))
            cleaned_arc = normalize_text(actor.arc) if actor.arc else None
            cleaned_importance = actor.importance.strip().lower() if actor.importance else "supporting"
            if cleaned_importance not in ("main", "supporting", "cameo"):
                cleaned_importance = "supporting"
                
            cleaned_relationships = []
            for r in actor.relationships:
                target = normalize_name(r.get("target"))
                rel_type = normalize_text(r.get("type")).lower()
                if target and rel_type:
                    cleaned_relationships.append({"target": target, "type": rel_type})

            cleaned_cast.append(CastSchema(
                character_name=char_name,
                person_name=actor_name,
                external_person_id=actor.external_person_id.strip(),
                aliases=cleaned_aliases,
                biography=cleaned_bio,
                importance=cleaned_importance,
                relationships=cleaned_relationships,
                personality_traits=cleaned_traits,
                motivations=cleaned_motivations,
                arc=cleaned_arc
            ))
            
    # 4. Clean Crew
    cleaned_crew = []
    seen_crew = set() # Avoid duplicate crew assignments
    for member in movie.crew:
        crew_name = normalize_name(member.person_name)
        job = normalize_name(member.job)
        dept = normalize_name(member.department)
        crew_key = (member.external_person_id.strip(), job)
        if crew_key not in seen_crew:
            seen_crew.add(crew_key)
            cleaned_crew.append(CrewSchema(
                person_name=crew_name,
                external_person_id=member.external_person_id.strip(),
                job=job,
                department=dept
            ))

    # 5. Clean Scenes & Dialogues
    cleaned_scenes = []
    for scene in movie.scenes:
        desc = normalize_text(scene.description)
        summary = normalize_text(scene.summary) if scene.summary else desc
        location = normalize_name(scene.location) if scene.location else None
        importance = normalize_text(scene.narrative_importance) if scene.narrative_importance else None
        scene_type = scene.scene_type.strip().lower() if scene.scene_type else "dialogue"
        
        cleaned_dialogues = []
        for d in scene.dialogues:
            speaker = normalize_name(d.speaker or d.character_name)
            listener = normalize_name(d.listener) if d.listener else None
            meaning = normalize_text(d.meaning) if d.meaning else None
            emotional_tone = normalize_text(d.emotional_tone).lower() if d.emotional_tone else None
            subtext = normalize_text(d.subtext) if d.subtext else None
            
            cleaned_dialogues.append(DialogueSchema(
                character_name=speaker,
                speaker=speaker,
                listener=listener,
                text=normalize_text(d.text),
                meaning=meaning,
                emotional_tone=emotional_tone,
                subtext=subtext
            ))
            
        cleaned_objects = list(set([normalize_text(o).lower() for o in scene.objects if o]))
        cleaned_symbols = list(set([normalize_text(s).lower() for s in scene.symbols if s]))
        cleaned_events = list(set([normalize_text(e) for e in scene.memorable_events if e]))
        cleaned_emotions = list(set([normalize_name(em) for em in scene.emotions if em]))
        
        cleaned_scenes.append(SceneSchema(
            description=desc,
            summary=summary,
            location=location,
            participating_characters=list(set([normalize_name(pc) for pc in scene.participating_characters if pc])),
            emotions=cleaned_emotions,
            narrative_importance=importance,
            scene_type=scene_type,
            memorable_events=cleaned_events,
            dialogues=cleaned_dialogues,
            objects=cleaned_objects,
            symbols=cleaned_symbols
        ))

    # 6. Clean cues, music, and awards
    cleaned_memory_cues = list(set([normalize_text(mc) for mc in movie.memory_cues if mc]))
    cleaned_visual_cues = list(set([normalize_text(vc) for vc in movie.visual_cues if vc]))
    
    cleaned_music = []
    seen_music = set()
    for m in movie.music:
        track = normalize_name(m.track_name)
        artist = normalize_name(m.artist) if m.artist else None
        m_type = m.type.strip().lower() if m.type else "soundtrack"
        music_key = (track, artist)
        if music_key not in seen_music:
            seen_music.add(music_key)
            cleaned_music.append(MusicSchema(
                track_name=track,
                artist=artist,
                type=m_type
            ))
            
    cleaned_awards = []
    seen_awards = set()
    for a in movie.awards:
        a_name = normalize_name(a.name)
        category = normalize_text(a.category)
        award_key = (a_name, category, a.year)
        if award_key not in seen_awards:
            seen_awards.add(award_key)
            cleaned_awards.append(AwardSchema(
                name=a_name,
                category=category,
                year=a.year,
                winner=a.winner
            ))
            
    cleaned_reviews = []
    for r in movie.reviews:
        cleaned_reviews.append(ReviewSchema(
            critic_name=normalize_name(r.critic_name),
            rating=r.rating,
            text=normalize_text(r.text)
        ))

    # 7. Map details
    return MovieOntologyInput(
        title=cleaned_title,
        overview=cleaned_overview,
        release_year=movie.release_year,
        runtime=movie.runtime,
        language=movie.language.strip() if movie.language else "en",
        country=movie.country.strip() if movie.country else "US",
        tmdb_id=movie.tmdb_id.strip(),
        imdb_id=movie.imdb_id.strip() if movie.imdb_id else None,
        wikidata_id=movie.wikidata_id.strip() if movie.wikidata_id else None,
        tvdb_id=movie.tvdb_id.strip() if movie.tvdb_id else None,
        original_title=normalize_title(movie.original_title) if movie.original_title else cleaned_title,
        release_date=movie.release_date.strip() if movie.release_date else None,
        budget=movie.budget,
        revenue=movie.revenue,
        tagline=normalize_text(movie.tagline) if movie.tagline else None,
        status=normalize_name(movie.status) if movie.status else "Released",
        adult=movie.adult,
        popularity=movie.popularity,
        vote_average=movie.vote_average,
        vote_count=movie.vote_count,
        genres=cleaned_genres,
        subgenres=cleaned_subgenres,
        themes=cleaned_themes,
        emotions=cleaned_emotions,
        moods=cleaned_moods,
        keywords=cleaned_keywords,
        cast=cleaned_cast,
        crew=cleaned_crew,
        scenes=cleaned_scenes,
        memory_cues=cleaned_memory_cues,
        visual_cues=cleaned_visual_cues,
        music=cleaned_music,
        awards=cleaned_awards,
        reviews=cleaned_reviews,
        story_arcs=list(set([normalize_text(sa) for sa in movie.story_arcs if sa])),
        narrative_styles=list(set([normalize_text(ns) for ns in movie.narrative_styles if ns])),
        plot=normalize_text(movie.plot) if movie.plot else None,
        plot_summary=normalize_text(movie.plot_summary) if movie.plot_summary else None,
        beginning=normalize_text(movie.beginning) if movie.beginning else None,
        middle=normalize_text(movie.middle) if movie.middle else None,
        climax=normalize_text(movie.climax) if movie.climax else None,
        ending=normalize_text(movie.ending) if movie.ending else None,
        ending_type=normalize_name(movie.ending_type) if movie.ending_type else None,
        timeline=normalize_text(movie.timeline) if movie.timeline else None,
        twists=list(set([normalize_text(t) for t in movie.twists if t])),
        conflicts=list(set([normalize_text(c) for c in movie.conflicts if c])),
        subplots=list(set([normalize_text(s) for s in movie.subplots if s])),
        color_palette=list(set([normalize_text(cp).lower() for cp in movie.color_palette if cp])),
        cinematography_style=normalize_text(movie.cinematography_style) if movie.cinematography_style else None,
        camera_style=normalize_text(movie.camera_style) if movie.camera_style else None,
        lighting=normalize_text(movie.lighting) if movie.lighting else None,
        symbolism=list(set([normalize_text(sy) for sy in movie.symbolism if sy])),
        visual_motifs=list(set([normalize_text(vm) for vm in movie.visual_motifs if vm])),
        recurring_imagery=list(set([normalize_text(ri) for ri in movie.recurring_imagery if ri])),
        locations=list(set([normalize_name(l) for l in movie.locations if l])),
        historical_periods=list(set([normalize_name(hp) for hp in movie.historical_periods if hp])),
        franchises=list(set([normalize_name(f) for f in movie.franchises if f])),
        streaming_platforms=list(set([normalize_name(sp) for sp in movie.streaming_platforms if sp])),
        collections=list(set([normalize_name(c) for c in movie.collections if c])),
        streaming_providers=movie.streaming_providers,
        studios=list(set([normalize_name(s) for s in movie.studios if s])),
        franchise=normalize_name(movie.franchise) if movie.franchise else None,
        sequels=list(set([normalize_title(s) for s in movie.sequels if s])),
        prequels=list(set([normalize_title(p) for p in movie.prequels if p])),
        shared_universe=normalize_name(movie.shared_universe) if movie.shared_universe else None,
        target_audiences=list(set([normalize_name(ta) for ta in movie.target_audiences if ta]))
    )
