"""
main.py - FastAPI application entry point for the AI Recommendation Engine.

Day 8 updates:
- Initialized ContentRecommender (TF-IDF + cosine similarity) on startup
- Added GET /recommendations/similar/{item_id}?k=10 with 404/422 validation
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.services.catalog_service import CatalogService
from app.services.recommender import ContentRecommender

catalog_service: CatalogService | None = None
recommender: ContentRecommender | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load processed movie data and build TF-IDF similarity matrix on startup."""
    global catalog_service, recommender
    catalog_service = CatalogService()
    recommender = ContentRecommender(catalog_service.movies_df)
    print(f"Loaded {len(catalog_service.movies_df)} movies & built TF-IDF matrix")
    yield


app = FastAPI(
    title="AI Recommendation Engine",
    description="Backend API for movie catalog, popular fallback, content-based similarity, and user ratings.",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RatingCreate(BaseModel):
    user_id: int = Field(default=1, ge=1, description="ID of the user submitting the rating")
    movie_id: int = Field(..., ge=1, description="ID of the movie being rated")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating score between 1 and 5")


def _get_service() -> CatalogService:
    """Helper to ensure data is loaded before serving requests."""
    if catalog_service is None or catalog_service.movies_df.empty:
        raise HTTPException(
            status_code=503,
            detail="Dataset not loaded. Run python -m app.services.data_loader first.",
        )
    return catalog_service


@app.get("/")
def read_root():
    """Health check - returns API status."""
    return {"status": "ok"}


@app.get("/items")
def get_items(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page (1-100)"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
):
    """GET /items - Returns a paginated list of movies."""
    svc = _get_service()
    return svc.get_items(limit=limit, offset=offset)


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """GET /items/{item_id} - Returns details for a single movie."""
    svc = _get_service()
    item = svc.get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found.")
    return item


@app.get("/recommendations/popular")
def get_popular_recommendations(
    limit: int = Query(default=10, ge=1, le=50, description="Number of popular items"),
    min_ratings: int = Query(default=50, ge=1, description="Minimum rating count threshold"),
):
    """GET /recommendations/popular - Returns popular movies ranked by weighted rating."""
    svc = _get_service()
    items = svc.get_popular_items(limit=limit, min_ratings=min_ratings)
    return {
        "limit": limit,
        "min_ratings": min_ratings,
        "count": len(items),
        "items": items,
    }


@app.get("/recommendations/similar/{item_id}")
def get_similar_recommendations(
    item_id: int,
    k: int = Query(default=10, ge=1, le=50, description="Number of similar items (1-50)"),
):
    """
    GET /recommendations/similar/{item_id} - Returns top-k content-similar movies
    using TF-IDF on title and genres.
    """
    svc = _get_service()
    source_item = svc.get_item_by_id(item_id)
    if source_item is None or recommender is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found.")

    similar_items = recommender.get_similar_items(item_id=item_id, k=k)
    return {
        "source_item": source_item,
        "k": k,
        "count": len(similar_items),
        "items": similar_items,
    }


@app.post("/ratings", status_code=status.HTTP_201_CREATED)
def create_rating(payload: RatingCreate):
    """POST /ratings - Saves a 1-5 user rating for a movie."""
    svc = _get_service()
    try:
        return svc.add_rating(
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            rating=payload.rating,
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with id {payload.movie_id} not found.",
        )
