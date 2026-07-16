from typing import List
from app.schemas.ontology import MovieOntologyInput
from app.core.logging import get_logger

logger = get_logger("app.ingestion.validation")

def validate_movie_ontology(movie: MovieOntologyInput) -> List[str]:
    """
    Perform thorough validation check on the movie ontology payload before database ingestion.
    Returns a list of validation error messages. An empty list implies validation succeeded.
    """
    errors = []
    
    # 1. Base validation
    if not movie.tmdb_id or not movie.tmdb_id.strip():
        errors.append("Validation Error: movie.tmdb_id is missing or blank.")
    elif not movie.tmdb_id.strip().isdigit():
        errors.append(f"Validation Error: movie.tmdb_id '{movie.tmdb_id}' is invalid (must be digits).")
        
    if not movie.title or not movie.title.strip():
        errors.append("Validation Error: movie.title is missing or blank.")
        
    if not movie.overview or len(movie.overview.strip()) < 10:
        errors.append("Validation Error: movie.overview is too short or missing.")
        
    # 2. Cast & Crew validation
    seen_cast_ids = set()
    cast_character_names = set()
    
    for idx, actor in enumerate(movie.cast):
        actor_name = actor.person_name.strip() if actor.person_name else ""
        if not actor_name:
            errors.append(f"Validation Warning: Cast index {idx} has an empty person name.")
            
        if not actor.external_person_id or not actor.external_person_id.strip():
            errors.append(f"Validation Error: Actor '{actor_name}' (index {idx}) is missing external_person_id.")
        else:
            pid = actor.external_person_id.strip()
            if pid in seen_cast_ids:
                errors.append(f"Validation Warning: Actor '{actor_name}' (ID {pid}) is duplicated in the cast list.")
            seen_cast_ids.add(pid)
            
        if actor.character_name and actor.character_name.strip():
            cast_character_names.add(actor.character_name.strip().lower())
            
    seen_crew_keys = set()
    for idx, member in enumerate(movie.crew):
        crew_name = member.person_name.strip() if member.person_name else ""
        if not member.external_person_id or not member.external_person_id.strip():
            errors.append(f"Validation Error: Crew member '{crew_name}' (index {idx}) is missing external_person_id.")
        else:
            ckey = (member.external_person_id.strip(), member.job.strip().lower())
            if ckey in seen_crew_keys:
                errors.append(f"Validation Warning: Crew member '{crew_name}' (ID {member.external_person_id.strip()}) duplicate role '{member.job}' detected.")
            seen_crew_keys.add(ckey)

    # 3. Scenes & Dialogues Speaker-Cast validation
    for s_idx, scene in enumerate(movie.scenes):
        if not scene.description or not scene.description.strip():
            errors.append(f"Validation Error: Scene index {s_idx} is missing a description.")
            
        for d_idx, d in enumerate(scene.dialogues):
            speaker = d.speaker or d.character_name
            if not speaker or not speaker.strip():
                errors.append(f"Validation Error: Dialogue {d_idx} in Scene {s_idx} has an empty speaker name.")
                continue
                
            speaker_clean = speaker.strip().lower()
            # If cast is defined and speaker is not found in cast, trigger relationship warnings
            if cast_character_names and speaker_clean not in cast_character_names:
                # Log warning but do not block ingestion (e.g. background voices or unnamed speaker might not be billed in top 10 cast)
                logger.debug(f"Validation Speaker Warning: Speaker '{speaker}' in scene {s_idx} is not listed in the movie cast characters.")

    # 4. Circular Prequel/Sequel loops validation
    clean_title = movie.title.strip().lower()
    for prequel in movie.prequels:
        if prequel.strip().lower() == clean_title:
            errors.append(f"Validation Error: Movie cannot be listed as its own prequel ('{movie.title}').")
            
    for sequel in movie.sequels:
        if sequel.strip().lower() == clean_title:
            errors.append(f"Validation Error: Movie cannot be listed as its own sequel ('{movie.title}').")

    return errors
