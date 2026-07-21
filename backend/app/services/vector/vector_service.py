from typing import List, Dict, Any
from datetime import datetime, timezone
from app.core.interfaces.vector import BaseVectorStore
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.schemas.ontology import MovieOntologyInput
from app.services.base import BaseService

class VectorService(BaseService):
    """
    Handles semantic chunk generation, metadata formatting, embedding generation,
    and storage across multiple target collections inside ChromaDB.
    """
    def __init__(self, vector_store: BaseVectorStore, embedding_provider: BaseEmbeddingProvider):
        super().__init__()
        self.store = vector_store
        self.embedding = embedding_provider

    def populate_movie(self, movie: MovieOntologyInput) -> None:
        """
        Generate search chunks for a movie across multiple collections, embed them,
        and index them into ChromaDB.
        """
        self.logger.info(f"Populating ChromaDB Vector indexes for: '{movie.title}' (ID: {movie.tmdb_id})")
        
        timestamp_str = datetime.now(timezone.utc).isoformat()
        
        base_meta = {
            "movie_id": movie.tmdb_id,
            "title": movie.title,
            "release_year": movie.release_year,
            "source_information": "tmdb_ingestion",
            "timestamp": timestamp_str,
            "embedding_model": self.embedding.model_name,
            "embedding_version": self.embedding.version,
            "source_provider": self.embedding.provider_name,
            "generated_at": timestamp_str
        }

        # 1. Collection: movie_overviews
        overview_text = (
            f"Title: {movie.title}\n"
            f"Year: {movie.release_year}\n"
            f"Genres: {', '.join(movie.genres)}\n"
            f"Tagline: {movie.tagline or ''}\n"
            f"Overview: {movie.overview}"
        )
        ov_meta = {
            **base_meta,
            "ontology_references": f"genres:{','.join(movie.genres)}|keywords:{','.join(movie.keywords[:10])}",
            "confidence_score": movie.confidence_score or 1.0,
            "generated_by": movie.generated_by or "tmdb",
            "generated_at": movie.generated_at or timestamp_str,
            "source": movie.source or "tmdb"
        }
        self._embed_and_index([overview_text], [ov_meta], [f"{movie.tmdb_id}_overview"], "movie_overviews")

        # 2. Collection: characters
        char_texts = []
        char_metas = []
        char_ids = []
        for actor in movie.cast:
            char_text = (
                f"Character: {actor.character_name}\n"
                f"Actor: {actor.person_name}\n"
                f"Movie: {movie.title} ({movie.release_year})\n"
                f"Importance: {actor.importance or 'supporting'}\n"
                f"Personality Traits: {', '.join(actor.personality_traits)}\n"
                f"Motivations: {', '.join(actor.motivations)}\n"
                f"Biography: {actor.biography or ''}\n"
                f"Character Arc: {actor.arc or ''}"
            )
            char_texts.append(char_text)
            char_metas.append({
                **base_meta,
                "character_id": actor.external_person_id,
                "character_name": actor.character_name,
                "actor_name": actor.person_name,
                "importance": actor.importance or "supporting",
                "ontology_references": f"traits:{','.join(actor.personality_traits)}|motivations:{','.join(actor.motivations)}",
                "confidence_score": actor.confidence_score or 1.0,
                "generated_by": actor.generated_by or "tmdb",
                "generated_at": actor.generated_at or timestamp_str,
                "source": actor.source or "tmdb"
            })
            char_ids.append(f"{movie.tmdb_id}_char_{actor.external_person_id}")
        if char_texts:
            self._embed_and_index(char_texts, char_metas, char_ids, "characters")

        # 3. Collection: scenes
        scene_texts = []
        scene_metas = []
        scene_ids = []
        for idx, scene in enumerate(movie.scenes):
            scene_text = (
                f"Movie: {movie.title} ({movie.release_year})\n"
                f"Scene {idx}: {scene.description}\n"
                f"Summary: {scene.summary or ''}\n"
                f"Location: {scene.location or 'Unknown'}\n"
                f"Importance: {scene.narrative_importance or 'Standard'}\n"
                f"Scene Type: {scene.scene_type or 'dialogue'}\n"
                f"Objects present: {', '.join(scene.objects)}\n"
                f"Symbols used: {', '.join(scene.symbols)}"
            )
            scene_texts.append(scene_text)
            scene_metas.append({
                **base_meta,
                "scene_id": str(idx),
                "location": scene.location or "Unknown",
                "scene_type": scene.scene_type or "dialogue",
                "ontology_references": f"objects:{','.join(scene.objects)}|symbols:{','.join(scene.symbols)}|emotions:{','.join(scene.emotions)}",
                "confidence_score": scene.confidence_score or 1.0,
                "generated_by": scene.generated_by or "tmdb",
                "generated_at": scene.generated_at or timestamp_str,
                "source": scene.source or "tmdb"
            })
            scene_ids.append(f"{movie.tmdb_id}_scene_{idx}")
        if scene_texts:
            self._embed_and_index(scene_texts, scene_metas, scene_ids, "scenes")

        # 4. Collection: dialogues
        dial_texts = []
        dial_metas = []
        dial_ids = []
        for idx, scene in enumerate(movie.scenes):
            for d_idx, d in enumerate(scene.dialogues):
                speaker = d.speaker or d.character_name
                d_text = (
                    f"Movie: {movie.title} ({movie.release_year})\n"
                    f"Scene Setting: {scene.location or 'Unknown setting'}\n"
                    f"Speaker: {speaker}\n"
                    f"Listener: {d.listener or 'Unknown'}\n"
                    f"Dialogue: \"{d.text}\"\n"
                    f"Meaning: {d.meaning or ''}\n"
                    f"Emotional Tone: {d.emotional_tone or 'neutral'}\n"
                    f"Subtext context: {d.subtext or 'Direct dialogue'}"
                )
                dial_texts.append(d_text)
                dial_metas.append({
                    **base_meta,
                    "scene_id": str(idx),
                    "speaker": speaker,
                    "listener": d.listener or "Unknown",
                    "emotional_tone": d.emotional_tone or "neutral",
                    "ontology_references": f"subtext:{d.subtext or ''}",
                    "confidence_score": d.confidence_score or 1.0,
                    "generated_by": d.generated_by or "tmdb",
                    "generated_at": d.generated_at or timestamp_str,
                    "source": d.source or "tmdb"
                })
                dial_ids.append(f"{movie.tmdb_id}_scene_{idx}_dial_{d_idx}")
        if dial_texts:
            self._embed_and_index(dial_texts, dial_metas, dial_ids, "dialogues")

        # 5. Collection: themes
        theme_texts = []
        theme_metas = []
        theme_ids = []
        for idx, theme in enumerate(movie.themes):
            t_text = (
                f"Movie: {movie.title} ({movie.release_year})\n"
                f"Theme analyzed: {theme}"
            )
            theme_texts.append(t_text)
            theme_metas.append({
                **base_meta,
                "theme": theme,
                "ontology_references": f"theme:{theme}",
                "confidence_score": movie.confidence_score or 1.0,
                "generated_by": movie.generated_by or "tmdb",
                "generated_at": movie.generated_at or timestamp_str,
                "source": movie.source or "tmdb"
            })
            theme_ids.append(f"{movie.tmdb_id}_theme_{idx}")
        if theme_texts:
            self._embed_and_index(theme_texts, theme_metas, theme_ids, "themes")

        # 6. Collection: memory_cues
        cue_texts = []
        cue_metas = []
        cue_ids = []
        for idx, cue in enumerate(movie.memory_cues):
            c_text = (
                f"Movie: {movie.title} ({movie.release_year})\n"
                f"Memory Cue / Recall Trigger: {cue}"
            )
            cue_texts.append(c_text)
            cue_metas.append({
                **base_meta,
                "ontology_references": "recall_cue",
                "confidence_score": movie.confidence_score or 1.0,
                "generated_by": movie.generated_by or "tmdb",
                "generated_at": movie.generated_at or timestamp_str,
                "source": movie.source or "tmdb"
            })
            cue_ids.append(f"{movie.tmdb_id}_memory_cue_{idx}")
        if cue_texts:
            self._embed_and_index(cue_texts, cue_metas, cue_ids, "memory_cues")

        # 7. Collection: visual_cues
        vis_texts = []
        vis_metas = []
        vis_ids = []
        for idx, cue in enumerate(movie.visual_cues):
            v_text = (
                f"Movie: {movie.title} ({movie.release_year})\n"
                f"Visual Cue / Motif: {cue}"
            )
            vis_texts.append(v_text)
            vis_metas.append({
                **base_meta,
                "ontology_references": "visual_motif",
                "confidence_score": movie.confidence_score or 1.0,
                "generated_by": movie.generated_by or "tmdb",
                "generated_at": movie.generated_at or timestamp_str,
                "source": movie.source or "tmdb"
            })
            vis_ids.append(f"{movie.tmdb_id}_visual_cue_{idx}")
        if vis_texts:
            self._embed_and_index(vis_texts, vis_metas, vis_ids, "visual_cues")

    def _embed_and_index(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str], collection_name: str) -> None:
        """
        Private helper to generate embeddings and index into a specific Chroma collection.
        """
        self.logger.info(f"Generating vector embeddings for {len(texts)} chunks in '{collection_name}'...")
        embeddings = self.embedding.embed_documents(texts)
        
        self.logger.debug(f"Writing vectors into collection '{collection_name}'...")
        self.store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
            collection_name=collection_name
        )
