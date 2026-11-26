"""
catalog_service.py - Business logic for item catalog, popular recommendations,
and temporary CSV/in-memory rating storage (to be migrated to SQLite/PostgreSQL on Day 9).
"""

import os
from datetime import datetime, timezone
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed")
MOVIES_CSV = os.path.join(DATA_DIR, "movies_clean.csv")
USER_RATINGS_CSV = os.path.join(DATA_DIR, "user_ratings_temp.csv")


class CatalogService:
    """Manages loading movies, computing popular rankings, and storing user ratings."""

    def __init__(self):
        self.movies_df: pd.DataFrame = pd.DataFrame()
        self.user_ratings: list[dict] = []
        self.load_data()

    def load_data(self) -> None:
        """Load cleaned movie data and any previously saved temporary ratings."""
        if os.path.exists(MOVIES_CSV):
            self.movies_df = pd.read_csv(MOVIES_CSV)
        else:
            self.movies_df = pd.DataFrame()

        if os.path.exists(USER_RATINGS_CSV):
            df = pd.read_csv(USER_RATINGS_CSV)
            self.user_ratings = df.to_dict(orient="records")

    def _row_to_dict(self, row: pd.Series) -> dict:
        """Convert a DataFrame row into a clean JSON-serializable movie dictionary."""
        return {
            "movieId": int(row["movieId"]),
            "title": str(row["title"]),
            "clean_title": str(row.get("clean_title", row["title"])),
            "genres": str(row["genres"]),
            "year": int(row["year"]) if pd.notna(row.get("year")) else None,
            "avg_rating": round(float(row["avg_rating"]), 2),
            "rating_count": int(row["rating_count"]),
        }

    def get_items(self, limit: int = 20, offset: int = 0) -> dict:
        """Return a paginated slice of movies."""
        total = len(self.movies_df)
        page = self.movies_df.iloc[offset : offset + limit]
        items = [self._row_to_dict(row) for _, row in page.iterrows()]
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
        }

    def get_item_by_id(self, item_id: int) -> dict | None:
        """Return a single movie by movieId, or None if not found."""
        if self.movies_df.empty:
            return None
        match = self.movies_df[self.movies_df["movieId"] == item_id]
        if match.empty:
            return None
        return self._row_to_dict(match.iloc[0])

    def get_popular_items(self, limit: int = 10, min_ratings: int = 50) -> list[dict]:
        """
        Rank movies using the IMDb Weighted Rating (WR) formula:
            WR = (v / (v + m)) * R + (m / (v + m)) * C
        where:
            v = rating_count for the movie
            m = min_ratings threshold (filters out movies with too few votes)
            R = avg_rating for the movie
            C = mean avg_rating across all rated movies
        """
        if self.movies_df.empty:
            return []

        rated = self.movies_df[self.movies_df["rating_count"] > 0]
        if rated.empty:
            return []

        C = float(rated["avg_rating"].mean())
        qualified = rated[rated["rating_count"] >= min_ratings].copy()

        # Fallback if min_ratings is higher than any movie's count
        if qualified.empty:
            qualified = rated.copy()

        v = qualified["rating_count"]
        R = qualified["avg_rating"]
        m = min_ratings

        qualified["weighted_score"] = ((v / (v + m)) * R) + ((m / (v + m)) * C)
        top = qualified.sort_values(by="weighted_score", ascending=False).head(limit)

        results = []
        for _, row in top.iterrows():
            item = self._row_to_dict(row)
            item["weighted_score"] = round(float(row["weighted_score"]), 3)
            results.append(item)
        return results

    def add_rating(self, user_id: int, movie_id: int, rating: float) -> dict:
        """
        Store a user rating (1.0 - 5.0) in memory and append to a temporary CSV file.
        Also updates the in-memory movie statistics so the UI sees the change immediately.
        """
        idx_matches = self.movies_df.index[self.movies_df["movieId"] == movie_id].tolist()
        if not idx_matches:
            raise KeyError(f"Movie {movie_id} not found")

        idx = idx_matches[0]
        entry = {
            "id": len(self.user_ratings) + 1,
            "user_id": user_id,
            "movie_id": movie_id,
            "rating": float(rating),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.user_ratings.append(entry)

        # Persist to temporary CSV
        os.makedirs(DATA_DIR, exist_ok=True)
        pd.DataFrame(self.user_ratings).to_csv(USER_RATINGS_CSV, index=False)

        # Update in-memory movie avg_rating and rating_count
        old_count = int(self.movies_df.at[idx, "rating_count"])
        old_avg = float(self.movies_df.at[idx, "avg_rating"])
        new_count = old_count + 1
        new_avg = round(((old_avg * old_count) + float(rating)) / new_count, 2)
        self.movies_df.at[idx, "rating_count"] = new_count
        self.movies_df.at[idx, "avg_rating"] = new_avg

        return {
            "message": "Rating saved successfully",
            "rating": entry,
            "updated_movie": {
                "movieId": movie_id,
                "avg_rating": new_avg,
                "rating_count": new_count,
            },
        }
