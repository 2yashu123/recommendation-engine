"""
schemas.py - Pydantic request validation schemas for the API.
"""

from typing import Literal
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    user_id: int = Field(default=1, ge=1, description="User ID (>= 1)")
    movie_id: int = Field(..., ge=1, description="Movie ID (>= 1)")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating score between 0.5 and 5.0")


class RatingUpdate(BaseModel):
    rating: float = Field(..., ge=0.5, le=5.0, description="Updated rating score (0.5 to 5.0)")


class InteractionCreate(BaseModel):
    user_id: int = Field(default=1, ge=1, description="User ID (>= 1)")
    movie_id: int = Field(..., ge=1, description="Movie ID (>= 1)")
    interaction_type: Literal["view", "click", "similar_click"] = Field(
        ..., description="Type of user interaction"
    )
