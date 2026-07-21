from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base_class import Base

class Franchise(Base):
    """Franchise model grouping movies belonging to shared universes or sequences."""
    __tablename__ = "franchises"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    movies: Mapped[List["Movie"]] = relationship(back_populates="franchise")
