"""
test_api.py - Pytest integration tests for all AI Recommendation Engine API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.db_models import Interaction


@pytest.fixture(scope="module")
def client():
    """Provide a TestClient with FastAPI lifespan initialized."""
    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


def test_get_items_paginated(client):
    res = client.get("/items?limit=5&offset=0")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert len(body["items"]) == 5


def test_get_single_item(client):
    res = client.get("/items/1")
    assert res.status_code == 200
    assert res.json()["movieId"] == 1


def test_get_item_not_found(client):
    res = client.get("/items/999999")
    assert res.status_code == 404


def test_popular_recommendations(client):
    res = client.get("/recommendations/popular?limit=5&min_ratings=50")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 5
    assert "weighted_score" in body["items"][0]


def test_similar_recommendations_valid(client):
    res = client.get("/recommendations/similar/1?k=5")
    assert res.status_code == 200
    body = res.json()
    assert body["source_item"]["movieId"] == 1
    assert body["count"] == 5
    assert "similarity_score" in body["items"][0]


def test_similar_recommendations_not_found(client):
    res = client.get("/recommendations/similar/999999")
    assert res.status_code == 404


def test_similar_recommendations_invalid_k(client):
    res = client.get("/recommendations/similar/1?k=100")
    assert res.status_code == 422


def test_ratings_crud_lifecycle(client):
    # Create
    res = client.post("/ratings", json={"user_id": 1, "movie_id": 1, "rating": 4.5})
    assert res.status_code == 201
    rating_id = res.json()["rating"]["id"]

    # Read
    res_get = client.get("/ratings?user_id=1&limit=10")
    assert res_get.status_code == 200
    assert any(r["id"] == rating_id for r in res_get.json()["ratings"])

    # Update
    res_put = client.put(f"/ratings/{rating_id}", json={"rating": 3.0})
    assert res_put.status_code == 200
    assert res_put.json()["rating"]["rating"] == 3.0

    # Delete
    res_del = client.delete(f"/ratings/{rating_id}")
    assert res_del.status_code == 200


def test_ratings_validation_error(client):
    res = client.post("/ratings", json={"user_id": 1, "movie_id": 1, "rating": 7.0})
    assert res.status_code == 422


def test_create_interaction(client):
    res = client.post(
        "/interactions",
        json={"user_id": 1, "movie_id": 1, "interaction_type": "view"},
    )
    assert res.status_code == 201
    interaction_id = res.json()["interaction"]["id"]
    assert res.json()["interaction"]["interaction_type"] == "view"

    # Cleanup test interaction row
    db = SessionLocal()
    try:
        obj = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if obj:
            db.delete(obj)
            db.commit()
    finally:
        db.close()


def test_create_interaction_invalid_type(client):
    res = client.post(
        "/interactions",
        json={"user_id": 1, "movie_id": 1, "interaction_type": "invalid_type"},
    )
    assert res.status_code == 422
