"""
data_loader.py - Data cleaning and preprocessing for MovieLens ml-latest-small.

This module loads raw CSV files from data/raw/ml-latest-small/,
cleans them (handle missing values, remove duplicates, parse genres),
computes per-movie statistics (average rating, rating count),
and saves the processed data to data/processed/.
"""

import pandas as pd
import os

# Paths relative to the project root
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw", "ml-latest-small")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed")


def load_and_clean_movies(raw_dir: str = RAW_DIR) -> pd.DataFrame:
    """
    Load movies.csv, clean it, and parse genres.

    Steps:
    1. Read the CSV file
    2. Drop rows with missing title or genres
    3. Remove duplicate movieId entries
    4. Split the pipe-separated genres string into a list
    5. Add a 'year' column extracted from the title (if present)
    """
    movies_path = os.path.join(raw_dir, "movies.csv")
    print(f"Loading movies from {movies_path}...")
    movies = pd.read_csv(movies_path)

    # Check initial shape
    print(f"  Raw movies: {len(movies)} rows")

    # Drop rows where title or genres are missing
    movies = movies.dropna(subset=["title", "genres"])
    print(f"  After dropping missing: {len(movies)} rows")

    # Remove duplicate movieIds (keep first occurrence)
    movies = movies.drop_duplicates(subset=["movieId"], keep="first")
    print(f"  After removing duplicates: {len(movies)} rows")

    # Parse genres: split "Action|Comedy|Drama" into ["Action", "Comedy", "Drama"]
    # For CSV storage, we'll keep it as pipe-separated but also create a list column
    movies["genres_list"] = movies["genres"].apply(
        lambda g: g.split("|") if g != "(no genres listed)" else []
    )

    # Extract year from title like "Toy Story (1995)"
    movies["year"] = movies["title"].str.extract(r"\((\d{4})\)$")
    movies["year"] = pd.to_numeric(movies["year"], errors="coerce")

    # Clean title: remove the year suffix for a cleaner display name
    movies["clean_title"] = movies["title"].str.replace(r"\s*\(\d{4}\)$", "", regex=True)

    return movies


def load_and_clean_ratings(raw_dir: str = RAW_DIR) -> pd.DataFrame:
    """
    Load ratings.csv, clean it, and validate rating values.

    Steps:
    1. Read the CSV file
    2. Drop rows with missing userId, movieId, or rating
    3. Remove duplicate (userId, movieId) pairs (keep latest by timestamp)
    4. Ensure ratings are within 0.5-5.0 range
    """
    ratings_path = os.path.join(raw_dir, "ratings.csv")
    print(f"Loading ratings from {ratings_path}...")
    ratings = pd.read_csv(ratings_path)

    print(f"  Raw ratings: {len(ratings)} rows")

    # Drop rows with missing essential fields
    ratings = ratings.dropna(subset=["userId", "movieId", "rating"])
    print(f"  After dropping missing: {len(ratings)} rows")

    # Sort by timestamp so we keep the latest rating when removing duplicates
    ratings = ratings.sort_values("timestamp", ascending=True)

    # Remove duplicate (userId, movieId) pairs, keeping the latest rating
    ratings = ratings.drop_duplicates(subset=["userId", "movieId"], keep="last")
    print(f"  After removing duplicates: {len(ratings)} rows")

    # Validate rating range (MovieLens uses 0.5 to 5.0 in 0.5 steps)
    ratings = ratings[(ratings["rating"] >= 0.5) & (ratings["rating"] <= 5.0)]
    print(f"  After validating range: {len(ratings)} rows")

    return ratings


def compute_movie_stats(movies: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    """
    Compute average rating and rating count for each movie.

    Merges movie metadata with aggregated rating statistics to create
    a single enriched dataset ready for the API.
    """
    # Aggregate ratings per movie
    stats = ratings.groupby("movieId").agg(
        avg_rating=("rating", "mean"),
        rating_count=("rating", "count")
    ).reset_index()

    # Round average rating to 2 decimal places
    stats["avg_rating"] = stats["avg_rating"].round(2)

    # Merge movie info with rating stats (left join to keep movies with no ratings)
    enriched = movies.merge(stats, on="movieId", how="left")

    # Fill NaN for movies with no ratings
    enriched["avg_rating"] = enriched["avg_rating"].fillna(0.0)
    enriched["rating_count"] = enriched["rating_count"].fillna(0).astype(int)

    print(f"  Enriched dataset: {len(enriched)} movies, "
          f"{len(enriched[enriched['rating_count'] > 0])} with ratings")

    return enriched


def save_processed_data(movies_enriched: pd.DataFrame, ratings: pd.DataFrame,
                        processed_dir: str = PROCESSED_DIR):
    """
    Save cleaned and enriched data to CSV files in data/processed/.
    """
    os.makedirs(processed_dir, exist_ok=True)

    # Save enriched movies (drop the list column for CSV compatibility)
    movies_csv = movies_enriched.drop(columns=["genres_list"], errors="ignore")
    movies_path = os.path.join(processed_dir, "movies_clean.csv")
    movies_csv.to_csv(movies_path, index=False)
    print(f"Saved enriched movies to {movies_path} ({len(movies_csv)} rows)")

    # Save cleaned ratings
    ratings_path = os.path.join(processed_dir, "ratings_clean.csv")
    ratings.to_csv(ratings_path, index=False)
    print(f"Saved cleaned ratings to {ratings_path} ({len(ratings)} rows)")


def run_pipeline():
    """Run the full data cleaning pipeline."""
    print("=" * 60)
    print("DATA CLEANING PIPELINE - MovieLens ml-latest-small")
    print("=" * 60)

    # Step 1: Load and clean movies
    movies = load_and_clean_movies()

    # Step 2: Load and clean ratings
    ratings = load_and_clean_ratings()

    # Step 3: Compute per-movie statistics
    enriched = compute_movie_stats(movies, ratings)

    # Step 4: Save processed data
    save_processed_data(enriched, ratings)

    # Step 5: Print summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE - Summary")
    print("=" * 60)
    print(f"Total movies:          {len(enriched)}")
    print(f"Movies with ratings:   {len(enriched[enriched['rating_count'] > 0])}")
    print(f"Total clean ratings:   {len(ratings)}")
    print(f"Unique users:          {ratings['userId'].nunique()}")
    print(f"Rating range:          {ratings['rating'].min()} - {ratings['rating'].max()}")
    print(f"Top genres:            {', '.join(enriched['genres'].value_counts().head(5).index.tolist())}")
    print(f"\nSample enriched movie:")
    sample = enriched[enriched["rating_count"] > 10].iloc[0]
    print(f"  {sample['title']} | Genres: {sample['genres']} | "
          f"Avg: {sample['avg_rating']} | Count: {sample['rating_count']}")

    return enriched, ratings


if __name__ == "__main__":
    run_pipeline()
