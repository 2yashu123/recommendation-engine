"""
main.py - FastAPI application entry point for the AI Recommendation Engine.

This is the central file that creates the FastAPI app, configures CORS,
and includes all API routes. Run with:
    uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Recommendation Engine",
    description="Backend API for movie recommendations using content-based filtering.",
    version="0.1.0",
)

# Allow the Next.js frontend (localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load processed data into memory on startup
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "movies_clean.csv")

# Global dataframe - loaded once when the server starts
movies_df: pd.DataFrame = pd.DataFrame()


@app.on_event("startup")
def load_data():
    """Load the cleaned movie dataset when the server starts."""
    global movies_df
    try:
        movies_df = pd.read_csv(DATA_PATH)
        print(f"Loaded {len(movies_df)} movies from {DATA_PATH}")
    except FileNotFoundError:
        print(f"WARNING: {DATA_PATH} not found. Run the data pipeline first.")
        print("  cd backend && python -m app.services.data_loader")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    """Health check - returns API status."""
    return {"status": "ok"}


@app.get("/items")
def get_items(
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
):
    """
    GET /items - Returns a paginated list of movies.

    Query parameters:
    - limit: how many items to return (1-100, default 20)
    - offset: how many items to skip (default 0)

    Returns a JSON object with total count and the list of items.
    """
    if movies_df.empty:
        raise HTTPException(status_code=503, detail="Data not loaded. Run the data pipeline first.")

    total = len(movies_df)
    # Slice the dataframe for pagination
    page = movies_df.iloc[offset : offset + limit]

    # Convert to list of dicts for JSON response
    items = []
    for _, row in page.iterrows():
        items.append({
            "movieId": int(row["movieId"]),
            "title": row["title"],
            "genres": row["genres"],
            "year": int(row["year"]) if pd.notna(row.get("year")) else None,
            "avg_rating": float(row["avg_rating"]),
            "rating_count": int(row["rating_count"]),
        })

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """
    GET /items/{item_id} - Returns details for a single movie.

    Path parameter:
    - item_id: the movieId to look up

    Returns 404 if the movie is not found.
    """
    if movies_df.empty:
        raise HTTPException(status_code=503, detail="Data not loaded. Run the data pipeline first.")

    # Find the movie by movieId
    match = movies_df[movies_df["movieId"] == item_id]

    if match.empty:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found.")

    row = match.iloc[0]
    return {
        "movieId": int(row["movieId"]),
        "title": row["title"],
        "clean_title": row.get("clean_title", row["title"]),
        "genres": row["genres"],
        "year": int(row["year"]) if pd.notna(row.get("year")) else None,
        "avg_rating": float(row["avg_rating"]),
        "rating_count": int(row["rating_count"]),
    }
