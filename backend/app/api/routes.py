"""
routes.py - Organized FastAPI routes for health, catalog, recommendations, ratings, and interactions.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas import InteractionCreate, RatingCreate, RatingUpdate
from app.core.database import get_db
from app.services.db_catalog_service import (
    check_db_health,
    create_interaction_in_db,
    create_rating_in_db,
    delete_rating_in_db,
    get_item_by_id_from_db,
    get_items_from_db,
    get_popular_items_from_db,
    get_ratings_from_db,
    update_rating_in_db,
)

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """GET /health - Reports API and database connectivity status."""
    try:
        check_db_health(db)
        return {
            "status": "ok",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {exc}",
        )


@router.get("/items", tags=["Catalog"])
def get_items(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page (1-100)"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
):
    """GET /items - Returns a paginated list of movies."""
    try:
        return get_items_from_db(db, limit=limit, offset=offset)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@router.get("/items/{item_id}", tags=["Catalog"])
def get_item(item_id: int, db: Session = Depends(get_db)):
    """GET /items/{item_id} - Returns details for a single movie."""
    try:
        item = get_item_by_id_from_db(db, item_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found.")
    return item


@router.get("/recommendations/popular", tags=["Recommendations"])
def get_popular_recommendations(
    limit: int = Query(default=10, ge=1, le=50, description="Number of popular items (1-50)"),
    min_ratings: int = Query(default=50, ge=1, description="Minimum rating count threshold"),
    db: Session = Depends(get_db),
):
    """GET /recommendations/popular - Returns popular movies ranked by weighted rating."""
    try:
        items = get_popular_items_from_db(db, limit=limit, min_ratings=min_ratings)
        return {
            "limit": limit,
            "min_ratings": min_ratings,
            "count": len(items),
            "items": items,
        }
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@router.get("/recommendations/similar/{item_id}", tags=["Recommendations"])
def get_similar_recommendations(
    item_id: int,
    request: Request,
    k: int = Query(default=10, ge=1, le=50, description="Number of similar items (1-50)"),
    db: Session = Depends(get_db),
):
    """GET /recommendations/similar/{item_id} - Returns top-k content-similar movies."""
    source_item = get_item_by_id_from_db(db, item_id)
    recommender = getattr(request.app.state, "recommender", None)
    if source_item is None or recommender is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found.")

    similar_items = recommender.get_similar_items(item_id=item_id, k=k)
    return {
        "source_item": source_item,
        "k": k,
        "count": len(similar_items),
        "items": similar_items,
    }


@router.post("/ratings", status_code=status.HTTP_201_CREATED, tags=["Ratings"])
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
        raise HTTPException(status_code=404, detail=f"Movie with id {payload.movie_id} not found.")
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@router.get("/ratings", tags=["Ratings"])
def list_ratings(
    user_id: int | None = Query(default=None, ge=1, description="Filter ratings by user ID"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum ratings to return"),
    db: Session = Depends(get_db),
):
    """GET /ratings - Reads ratings from the database (optionally filtered by user_id)."""
    try:
        rows = get_ratings_from_db(db, user_id=user_id, limit=limit)
        return {"count": len(rows), "ratings": rows}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@router.put("/ratings/{rating_id}", tags=["Ratings"])
def update_rating(rating_id: int, payload: RatingUpdate, db: Session = Depends(get_db)):
    """PUT /ratings/{rating_id} - Updates an existing rating score."""
    try:
        updated = update_rating_in_db(db, rating_id=rating_id, new_score=payload.rating)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    if updated is None:
        raise HTTPException(status_code=404, detail=f"Rating with id {rating_id} not found.")
    return {"message": "Rating updated successfully", "rating": updated}


@router.delete("/ratings/{rating_id}", tags=["Ratings"])
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    """DELETE /ratings/{rating_id} - Deletes a rating from the database."""
    try:
        deleted = delete_rating_in_db(db, rating_id=rating_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Rating with id {rating_id} not found.")
    return {"message": f"Rating {rating_id} deleted successfully"}


@router.post("/interactions", status_code=status.HTTP_201_CREATED, tags=["Interactions"])
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    """POST /interactions - Logs a user interaction (view, click, similar_click)."""
    try:
        return create_interaction_in_db(
            db,
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            interaction_type=payload.interaction_type,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Movie with id {payload.movie_id} not found.")
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
