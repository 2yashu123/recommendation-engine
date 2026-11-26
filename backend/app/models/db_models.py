"""
db_models.py - SQLAlchemy ORM models for users, items, ratings, and interactions.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)  # MovieLens movieId
    title = Column(String(255), nullable=False)
    clean_title = Column(String(255), nullable=True)
    genres = Column(String(255), nullable=False)
    year = Column(Integer, nullable=True)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)

    ratings = relationship("Rating", back_populates="item", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="item", cascade="all, delete-orphan")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="ratings")
    item = relationship("Item", back_populates="ratings")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)  # view, click, similar_click
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="interactions")
    item = relationship("Item", back_populates="interactions")
