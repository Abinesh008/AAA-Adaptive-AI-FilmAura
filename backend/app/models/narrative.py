from typing import List
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base
from app.models.base import AuditMixin

class Scene(Base, AuditMixin):
    """Scene model representing script acts and index sequences."""
    __tablename__ = "scenes"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    scene_index: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    importance: Mapped[str | None] = mapped_column(Text, nullable=True)
    scene_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="scenes")
    dialogues: Mapped[List["Dialogue"]] = relationship(
        back_populates="scene", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Dialogue(Base, AuditMixin):
    """Dialogue model capturing spoken words and structural tone."""
    __tablename__ = "dialogues"

    scene_id: Mapped[int] = mapped_column(ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False)
    speaker: Mapped[str] = mapped_column(String(255), nullable=False)
    listener: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dialogue_text: Mapped[str] = mapped_column(Text, nullable=False)
    meaning: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotional_tone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subtext: Mapped[str | None] = mapped_column(Text, nullable=True)

    scene: Mapped[Scene] = relationship(back_populates="dialogues")

class VisualCue(Base, AuditMixin):
    """VisualCue model capturing directors' cinematic styles and motifs."""
    __tablename__ = "visual_cues"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cue_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    movie: Mapped["Movie"] = relationship(back_populates="visual_cues")

class MemoryCue(Base, AuditMixin):
    """MemoryCue model mapping vague memory prompts to movies."""
    __tablename__ = "memory_cues"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="memory_cues")

class MovieTwist(Base, AuditMixin):
    """MovieTwist model representing key plot turns and spoilers."""
    __tablename__ = "movie_twists"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="twists")

class MovieConflict(Base, AuditMixin):
    """MovieConflict model capturing central character or narrative friction."""
    __tablename__ = "movie_conflicts"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="conflicts")

class MovieSubplot(Base, AuditMixin):
    """MovieSubplot model describing secondary plots and character arcs."""
    __tablename__ = "movie_subplots"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="subplots")
