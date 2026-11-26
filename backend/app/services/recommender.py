"""
recommender.py - Content-based recommendation engine using TF-IDF & Cosine Similarity.

Builds a TF-IDF matrix over movie titles and genres using scikit-learn,
then finds the top-K most similar movies for any given movieId.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentRecommender:
    """Computes content-based item similarity using TF-IDF on title + genres."""

    def __init__(self, movies_df: pd.DataFrame):
        self.movies_df = movies_df.reset_index(drop=True)
        self.id_to_idx: dict[int, int] = {}
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = None
        self._fit()

    def _fit(self) -> None:
        """Build the TF-IDF feature matrix from movie title and genres."""
        if self.movies_df.empty:
            return

        # Map each movieId to its DataFrame row index for fast lookup
        self.id_to_idx = {
            int(mid): idx for idx, mid in enumerate(self.movies_df["movieId"])
        }

        # Combine clean_title and genres into a single text representation
        titles = self.movies_df["clean_title"].fillna(self.movies_df["title"]).astype(str)
        genres = (
            self.movies_df["genres"]
            .fillna("")
            .astype(str)
            .str.replace("(no genres listed)", "", regex=False)
            .str.replace("|", " ", regex=False)
        )
        # Weight genres slightly by repeating them so genre match stays strong
        content_text = titles + " " + genres + " " + genres

        self.tfidf_matrix = self.vectorizer.fit_transform(content_text)

    def get_similar_items(self, item_id: int, k: int = 10) -> list[dict]:
        """
        Return the top-k most similar movies to item_id based on cosine similarity.

        Raises KeyError if item_id is not found.
        """
        if item_id not in self.id_to_idx or self.tfidf_matrix is None:
            raise KeyError(f"Item with id {item_id} not found.")

        idx = self.id_to_idx[item_id]

        # Compute cosine similarity between target movie vector and all movies
        sim_scores = cosine_similarity(
            self.tfidf_matrix[idx], self.tfidf_matrix
        ).flatten()

        # Exclude the source movie itself by setting its score to -1
        sim_scores[idx] = -1.0

        # Get top-k indices sorted by highest similarity score
        top_indices = sim_scores.argsort()[::-1][:k]

        results = []
        for i in top_indices:
            row = self.movies_df.iloc[i]
            results.append({
                "movieId": int(row["movieId"]),
                "title": str(row["title"]),
                "clean_title": str(row.get("clean_title", row["title"])),
                "genres": str(row["genres"]),
                "year": int(row["year"]) if pd.notna(row.get("year")) else None,
                "avg_rating": round(float(row["avg_rating"]), 2),
                "rating_count": int(row["rating_count"]),
                "similarity_score": round(float(sim_scores[i]), 4),
            })
        return results
