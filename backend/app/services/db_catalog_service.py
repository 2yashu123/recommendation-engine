"""
db_catalog_service.py - Database-backed CRUD & recommendation helpers using SQLAlchemy.
"""

from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.db_models import User, Item, Rating, Interaction


def item_to_dict(item: Item) -> dict:
    """Convert an Item ORM object into the API dictionary format."""
    return {
        "movieId": item.id,
        "title": item.title,
        "clean_title": item.clean_title or item.title,
        "genres": item.genres,
        "year": item.year,
        "avg_rating": round(float(item.avg_rating or 0.0), 2),
        "rating_count": int(item.rating_count or 0),
    }


def rating_to_dict(r: Rating) -> dict:
    """Convert a Rating ORM object into a dictionary."""
    return {
        "id": r.id,
        "user_id": r.user_id,
        "movie_id": r.item_id,
        "rating": float(r.rating),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }


def get_items_from_db(db: Session, limit: int = 20, offset: int = 0) -> dict:
    total = db.query(func.count(Item.id)).scalar() or 0
    rows = db.query(Item).order_by(Item.id.asc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [item_to_dict(i) for i in rows],
    }


def get_item_by_id_from_db(db: Session, item_id: int) -> dict | None:
    item = db.query(Item).filter(Item.id == item_id).first()
    return item_to_dict(item) if item else None


def get_popular_items_from_db(db: Session, limit: int = 10, min_ratings: int = 50) -> list[dict]:
    """Compute IMDb weighted rating from the items table in the database."""
    global_avg = db.query(func.avg(Item.avg_rating)).filter(Item.rating_count > 0).scalar()
    if global_avg is None:
        return []
    C = float(global_avg)

    qualified = db.query(Item).filter(Item.rating_count >= min_ratings).all()
    if not qualified:
        qualified = db.query(Item).filter(Item.rating_count > 0).all()

    scored = []
    m = min_ratings
    for item in qualified:
        v = item.rating_count
        R = item.avg_rating
        wr = ((v / (v + m)) * R) + ((m / (v + m)) * C)
        d = item_to_dict(item)
        d["weighted_score"] = round(float(wr), 3)
        scored.append(d)

    scored.sort(key=lambda x: x["weighted_score"], reverse=True)
    return scored[:limit]


def _recalculate_item_stats(db: Session, item: Item) -> None:
    """Recompute avg_rating and rating_count for an item from the ratings table."""
    agg = db.query(
        func.count(Rating.id),
        func.avg(Rating.rating)
    ).filter(Rating.item_id == item.id).first()
    count = int(agg[0] or 0)
    avg = round(float(agg[1] or 0.0), 2)
    item.rating_count = count
    item.avg_rating = avg
    db.commit()
    db.refresh(item)


def create_rating_in_db(db: Session, user_id: int, movie_id: int, rating_val: float) -> dict:
    item = db.query(Item).filter(Item.id == movie_id).first()
    if not item:
        raise KeyError(f"Movie with id {movie_id} not found.")

    # Ensure user exists (create automatically if new user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username=f"user_{user_id}")
        db.add(user)
        db.commit()

    new_rating = Rating(user_id=user_id, item_id=movie_id, rating=float(rating_val))
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    _recalculate_item_stats(db, item)

    return {
        "message": "Rating saved successfully",
        "rating": rating_to_dict(new_rating),
        "updated_movie": {
            "movieId": item.id,
            "avg_rating": item.avg_rating,
            "rating_count": item.rating_count,
        },
    }


def get_ratings_from_db(db: Session, user_id: int | None = None, limit: int = 50) -> list[dict]:
    query = db.query(Rating)
    if user_id is not None:
        query = query.filter(Rating.user_id == user_id)
    rows = query.order_by(Rating.id.desc()).limit(limit).all()
    return [rating_to_dict(r) for r in rows]


def update_rating_in_db(db: Session, rating_id: int, new_score: float) -> dict | None:
    rating_obj = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating_obj:
        return None
    rating_obj.rating = float(new_score)
    rating_obj.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rating_obj)

    item = db.query(Item).filter(Item.id == rating_obj.item_id).first()
    if item:
        _recalculate_item_stats(db, item)

    return rating_to_dict(rating_obj)


def delete_rating_in_db(db: Session, rating_id: int) -> bool:
    rating_obj = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating_obj:
        return False
    item_id = rating_obj.item_id
    db.delete(rating_obj)
    db.commit()

    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        _recalculate_item_stats(db, item)

    return True


def load_items_dataframe_from_db(db: Session) -> pd.DataFrame:
    """Load all items from the database into a pandas DataFrame for TF-IDF fitting."""
    items = db.query(Item).order_by(Item.id.asc()).all()
    if not items:
        return pd.DataFrame()
    return pd.DataFrame([item_to_dict(i) for i in items])
