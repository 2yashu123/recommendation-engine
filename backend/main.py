"""
main.py - FastAPI application entry point for the AI Recommendation Engine.

Day 6 updates:
- Extracted business logic to app/services/catalog_service.py
- Replaced deprecated @app.on_event("startup") with FastAPI lifespan
- Added GET /recommendations/popular (weighted rating fallback)
- Added POST /ratings (temporary CSV/in-memory rating storage with Pydantic validation)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.services.catalog_service import CatalogService

# Global service instance initialized during app startup
catalog_service: CatalogService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load processed movie data when the server starts."""
    global catalog_service
    catalog_service = CatalogService()
    print(f"Loaded {len(catalog_service.movies_df)} movies into CatalogService")
    yield


app = FastAPI(
    title="AI Recommendation Engine",
    description="Backend API for movie catalog, popular recommendations, and user ratings.",
    version="0.2.0",
    lifespan=lifespan,
)

# Allow Next.js frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
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
    """
    GET /recommendations/popular - Returns popular movies ranked by weighted rating.
    """
    svc = _get_service()
    items = svc.get_popular_items(limit=limit, min_ratings=min_ratings)
    return {
        "limit": limit,
        "min_ratings": min_ratings,
        "count": len(items),
        "items": items,
    }


@app.post("/ratings", status_code=status.HTTP_201_CREATED)
def create_rating(payload: RatingCreate):
    """
    POST /ratings - Saves a 1-5 user rating for a movie (in memory + temp CSV).
    """
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
