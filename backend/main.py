"""
main.py - FastAPI application entry point for the AI Recommendation Engine.

Day 9 updates:
- Switched catalog, popular items, and ratings CRUD to SQLAlchemy database
- Added full CRUD for ratings: POST /ratings, GET /ratings, PUT /ratings/{id}, DELETE /ratings/{id}
- Kept TF-IDF ContentRecommender working from database items
"""

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine, get_db
from app.services.db_catalog_service import (
    create_rating_in_db,
    delete_rating_in_db,
    get_item_by_id_from_db,
    get_items_from_db,
    get_popular_items_from_db,
    get_ratings_from_db,
    load_items_dataframe_from_db,
    update_rating_in_db,
)
from app.services.recommender import ContentRecommender

recommender: ContentRecommender | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure tables exist and fit TF-IDF ContentRecommender from database items."""
    global recommender
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        df = load_items_dataframe_from_db(db)
        recommender = ContentRecommender(df)
        print(f"Database connected. Loaded {len(df)} items & built TF-IDF matrix.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="AI Recommendation Engine",
    description="Backend API powered by SQLAlchemy, FastAPI, and scikit-learn.",
    version="0.4.0",
    lifespan=lifespan,
)

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
    user_id: int = Field(default=1, ge=1, description="User ID")
    movie_id: int = Field(..., ge=1, description="Movie ID")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating score (0.5 to 5.0)")


class RatingUpdate(BaseModel):
    rating: float = Field(..., ge=0.5, le=5.0, description="Updated rating score (0.5 to 5.0)")


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
    db: Session = Depends(get_db),
):
    """GET /items - Returns a paginated list of movies from the database."""
    return get_items_from_db(db, limit=limit, offset=offset)


@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    """GET /items/{item_id} - Returns details for a single movie."""
    item = get_item_by_id_from_db(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found.")
    return item


@app.get("/recommendations/popular")
def get_popular_recommendations(
    limit: int = Query(default=10, ge=1, le=50, description="Number of popular items"),
    min_ratings: int = Query(default=50, ge=1, description="Minimum rating count threshold"),
    db: Session = Depends(get_db),
):
    """GET /recommendations/popular - Returns popular movies ranked by weighted rating."""
    items = get_popular_items_from_db(db, limit=limit, min_ratings=min_ratings)
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
    db: Session = Depends(get_db),
):
    """GET /recommendations/similar/{item_id} - Returns top-k content-similar movies."""
    source_item = get_item_by_id_from_db(db, item_id)
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
def create_rating(payload: RatingCreate, db: Session = Depends(get_db)):
    """POST /ratings - Creates a new rating in the database."""
    try:
        return create_rating_in_db(
            db,
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            rating_val=payload.rating,
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with id {payload.movie_id} not found.",
        )


@app.get("/ratings")
def list_ratings(
    user_id: int | None = Query(default=None, ge=1, description="Filter ratings by user ID"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum ratings to return"),
    db: Session = Depends(get_db),
):
    """GET /ratings - Reads ratings from the database (optionally filtered by user_id)."""
    rows = get_ratings_from_db(db, user_id=user_id, limit=limit)
    return {"count": len(rows), "ratings": rows}


@app.put("/ratings/{rating_id}")
def update_rating(rating_id: int, payload: RatingUpdate, db: Session = Depends(get_db)):
    """PUT /ratings/{rating_id} - Updates an existing rating score in the database."""
    updated = update_rating_in_db(db, rating_id=rating_id, new_score=payload.rating)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Rating with id {rating_id} not found.")
    return {"message": "Rating updated successfully", "rating": updated}


@app.delete("/ratings/{rating_id}")
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    """DELETE /ratings/{rating_id} - Deletes a rating from the database."""
    deleted = delete_rating_in_db(db, rating_id=rating_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Rating with id {rating_id} not found.")
    return {"message": f"Rating {rating_id} deleted successfully"}
