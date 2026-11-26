# API Reference — AI Recommendation Engine

**Base URL:** `http://127.0.0.1:8000`  
**Interactive Docs (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## 1. Health Check

### `GET /health`
Verifies that the FastAPI service and SQLAlchemy database connection are operational.
- **Response (`200 OK`):**
  ```json
  {
    "status": "ok",
    "database": "connected",
    "timestamp": "2026-11-26T16:40:00+00:00"
  }
  ```
- **Errors:** `503 Service Unavailable` if the database cannot be reached.

---

## 2. Item Catalog

### `GET /items`
Returns a paginated list of movies from the database.
- **Query Params:** `limit` (1–100, default `20`), `offset` (>= 0, default `0`)
- **Response (`200 OK`):**
  ```json
  {
    "total": 9742,
    "limit": 20,
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
      }
    ]
  }
  ```
- **Errors:** `422 Unprocessable Entity` for invalid query bounds.

### `GET /items/{item_id}`
Returns details for a single movie by ID.
- **Path Param:** `item_id` (integer)
- **Response (`200 OK`):** Single movie JSON object.
- **Errors:** `404 Not Found` if `item_id` does not exist.

---

## 3. Recommendations

### `GET /recommendations/popular`
Returns top movies ranked by IMDb Weighted Rating with a minimum rating count threshold.
- **Query Params:** `limit` (1–50, default `10`), `min_ratings` (>= 1, default `50`)
- **Response (`200 OK`):** List of top items including `weighted_score`.

### `GET /recommendations/similar/{item_id}`
Returns top-K content-similar movies using TF-IDF + cosine similarity on title and genres.
- **Path Param:** `item_id` (integer)
- **Query Param:** `k` (1–50, default `10`)
- **Response (`200 OK`):** `source_item` plus `items` sorted by `similarity_score`.
- **Errors:** `404 Not Found` if `item_id` is missing; `422` if `k` is outside `1–50`.

---

## 4. Ratings CRUD

### `POST /ratings`
Creates a new rating (`0.5`–`5.0`) and recalculates the movie's average rating and count.
- **Request Body:**
  ```json
  { "user_id": 1, "movie_id": 1, "rating": 5.0 }
  ```
- **Response (`201 Created`):** Saved rating object and `updated_movie` stats.
- **Errors:** `404` if `movie_id` is missing; `422` if `rating` is outside `0.5–5.0`.

### `GET /ratings`
Lists stored ratings, optionally filtered by `user_id`.
- **Query Params:** `user_id` (optional int), `limit` (1–200, default `50`)
- **Response (`200 OK`):** `{"count": ..., "ratings": [...]}`

### `PUT /ratings/{rating_id}`
Updates an existing rating score and recalculates item statistics.
- **Request Body:** `{"rating": 4.0}`
- **Response (`200 OK`):** Updated rating object.
- **Errors:** `404 Not Found` if `rating_id` does not exist; `422` if score is invalid.

### `DELETE /ratings/{rating_id}`
Deletes a rating by ID and recalculates item statistics.
- **Response (`200 OK`):** `{"message": "Rating <id> deleted successfully"}`
- **Errors:** `404 Not Found` if `rating_id` does not exist.

---

## 5. User Interactions

### `POST /interactions`
Logs an implicit user interaction (`view`, `click`, or `similar_click`).
- **Request Body:**
  ```json
  { "user_id": 1, "movie_id": 1, "interaction_type": "view" }
  ```
- **Response (`201 Created`):** Logged interaction object.
- **Errors:** `404` if `movie_id` is missing; `422` if `interaction_type` is invalid.
