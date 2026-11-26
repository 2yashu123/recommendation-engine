# API Testing Results — AI Recommendation Engine

## 1. Automated Pytest Suite (`backend/tests/test_api.py`)

Command:
```powershell
.\venv\Scripts\pytest.exe -v
```

Real Output (`12 passed in 3.66s`):
```text
tests/test_api.py::test_health PASSED                                    [  8%]
tests/test_api.py::test_get_items_paginated PASSED                       [ 16%]
tests/test_api.py::test_get_single_item PASSED                           [ 25%]
tests/test_api.py::test_get_item_not_found PASSED                        [ 33%]
tests/test_api.py::test_popular_recommendations PASSED                   [ 41%]
tests/test_api.py::test_similar_recommendations_valid PASSED             [ 50%]
tests/test_api.py::test_similar_recommendations_not_found PASSED         [ 58%]
tests/test_api.py::test_similar_recommendations_invalid_k PASSED         [ 66%]
tests/test_api.py::test_ratings_crud_lifecycle PASSED                    [ 75%]
tests/test_api.py::test_ratings_validation_error PASSED                  [ 83%]
tests/test_api.py::test_create_interaction PASSED                        [ 91%]
tests/test_api.py::test_create_interaction_invalid_type PASSED           [100%]
```

---

## 2. Live HTTP Endpoint Examples & Real Outputs

### `GET /health` (HTTP 200)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2026-11-26T16:39:54.535896+00:00"
}
```

### `GET /items?limit=2&offset=0` (HTTP 200)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/items?limit=2&offset=0"
```
```json
{
  "total": 9742,
  "limit": 2,
  "offset": 0,
  "items": [
    {
      "movieId": 1,
      "title": "Toy Story (1995)",
      "clean_title": "Toy Story",
      "genres": "Adventure|Animation|Children|Comedy|Fantasy",
      "year": 1995,
      "avg_rating": 3.92,
      "rating_count": 215
    },
    {
      "movieId": 2,
      "title": "Jumanji (1995)",
      "clean_title": "Jumanji",
      "genres": "Adventure|Children|Fantasy",
      "year": 1995,
      "avg_rating": 3.43,
      "rating_count": 110
    }
  ]
}
```

### `GET /items/1` (HTTP 200)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/items/1"
```
```json
{
  "movieId": 1,
  "title": "Toy Story (1995)",
  "clean_title": "Toy Story",
  "genres": "Adventure|Animation|Children|Comedy|Fantasy",
  "year": 1995,
  "avg_rating": 3.92,
  "rating_count": 215
}
```

### `GET /recommendations/popular?limit=2` (HTTP 200)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/recommendations/popular?limit=2"
```
```json
{
  "limit": 2,
  "min_ratings": 50,
  "count": 2,
  "items": [
    {
      "movieId": 318,
      "title": "Shawshank Redemption, The (1994)",
      "clean_title": "Shawshank Redemption, The",
      "genres": "Crime|Drama",
      "year": 1994,
      "avg_rating": 4.43,
      "rating_count": 317,
      "weighted_score": 4.271
    },
    {
      "movieId": 2959,
      "title": "Fight Club (1999)",
      "clean_title": "Fight Club",
      "genres": "Action|Crime|Drama|Thriller",
      "year": 1999,
      "avg_rating": 4.27,
      "rating_count": 218,
      "weighted_score": 4.082
    }
  ]
}
```

### `GET /recommendations/similar/1?k=2` (HTTP 200)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/recommendations/similar/1?k=2"
```
```json
{
  "source_item": {
    "movieId": 1,
    "title": "Toy Story (1995)",
    "clean_title": "Toy Story",
    "genres": "Adventure|Animation|Children|Comedy|Fantasy",
    "year": 1995,
    "avg_rating": 3.92,
    "rating_count": 215
  },
  "k": 2,
  "count": 2,
  "items": [
    {
      "movieId": 3114,
      "title": "Toy Story 2 (1999)",
      "clean_title": "Toy Story 2",
      "genres": "Adventure|Animation|Children|Comedy|Fantasy",
      "year": 1999,
      "avg_rating": 3.86,
      "rating_count": 97,
      "similarity_score": 1.0
    },
    {
      "movieId": 78499,
      "title": "Toy Story 3 (2010)",
      "clean_title": "Toy Story 3",
      "genres": "Adventure|Animation|Children|Comedy|Fantasy|IMAX",
      "year": 2010,
      "avg_rating": 4.11,
      "rating_count": 55,
      "similarity_score": 0.8666
    }
  ]
}
```

### `POST /ratings` (HTTP 201)
```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/ratings" -ContentType "application/json" -Body '{"user_id":1,"movie_id":1,"rating":4.5}'
```
```json
{
  "message": "Rating saved successfully",
  "rating": {
    "id": 100837,
    "user_id": 1,
    "movie_id": 1,
    "rating": 4.5,
    "created_at": "2026-11-26T16:39:54.570392",
    "updated_at": "2026-11-26T16:39:54.570392"
  },
  "updated_movie": {
    "movieId": 1,
    "avg_rating": 3.92,
    "rating_count": 216
  }
}
```

### `GET /ratings?user_id=1&limit=2` (HTTP 200)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ratings?user_id=1&limit=2"
```
```json
{
  "count": 2,
  "ratings": [
    {
      "id": 100837,
      "user_id": 1,
      "movie_id": 1,
      "rating": 4.5,
      "created_at": "2026-11-26T16:39:54.570392",
      "updated_at": "2026-11-26T16:39:54.570392"
    },
    {
      "id": 16703,
      "user_id": 1,
      "movie_id": 2492,
      "rating": 4.0,
      "created_at": "2000-08-08T07:27:42",
      "updated_at": "2000-08-08T07:27:42"
    }
  ]
}
```

### `PUT /ratings/100837` (HTTP 200)
```powershell
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:8000/ratings/100837" -ContentType "application/json" -Body '{"rating":3.5}'
```
```json
{
  "message": "Rating updated successfully",
  "rating": {
    "id": 100837,
    "user_id": 1,
    "movie_id": 1,
    "rating": 3.5,
    "created_at": "2026-11-26T16:39:54.570392",
    "updated_at": "2026-11-26T16:39:54.596826"
  }
}
```

### `DELETE /ratings/100837` (HTTP 200)
```powershell
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:8000/ratings/100837"
```
```json
{
  "message": "Rating 100837 deleted successfully"
}
```

### `POST /interactions` (HTTP 201)
```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/interactions" -ContentType "application/json" -Body '{"user_id":1,"movie_id":1,"interaction_type":"view"}'
```
```json
{
  "message": "Interaction logged",
  "interaction": {
    "id": 1,
    "user_id": 1,
    "movie_id": 1,
    "interaction_type": "view",
    "created_at": "2026-11-26T16:39:54.631267"
  }
}
```
