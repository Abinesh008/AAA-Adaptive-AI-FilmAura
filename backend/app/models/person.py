from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base

class Person(Base):
    """Person model storing metadata for actors, directors, and crew members."""
    __tablename__ = "people"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    external_person_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    provider_name: Mapped[str] = mapped_column(String(50), default="tmdb")

    cast_roles: Mapped[List["MovieCast"]] = relationship(back_populates="person", lazy="selectin")
    crew_roles: Mapped[List["MovieCrew"]] = relationship(back_populates="person", lazy="selectin")
