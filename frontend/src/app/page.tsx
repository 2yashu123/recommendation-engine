"use client";

import { useState, useEffect } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface Movie {
  movieId: number;
  title: string;
  genres: string;
  year: number | null;
  avg_rating: number;
  rating_count: number;
  weighted_score?: number;
}

interface ItemsResponse {
  total: number;
  limit: number;
  offset: number;
  items: Movie[];
}

interface PopularResponse {
  limit: number;
  min_ratings: number;
  count: number;
  items: Movie[];
}

const API_BASE = "http://localhost:8000";

// ---------------------------------------------------------------------------
// Read-only Star Rating Display
// ---------------------------------------------------------------------------
function StarRating({ rating }: { rating: number }) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.25;
  return (
    <span className="text-yellow-500 text-sm" title={`${rating.toFixed(2)} / 5`}>
      {"★".repeat(fullStars)}
      {hasHalf && "½"}
      {"☆".repeat(Math.max(0, 5 - fullStars - (hasHalf ? 1 : 0)))}
      <span className="text-zinc-500 ml-1 text-xs">({rating.toFixed(2)})</span>
    </span>
  );
}

// ---------------------------------------------------------------------------
// Movie Card with Interactive 1-5 Star Rating Action
// ---------------------------------------------------------------------------
function MovieCard({
  movie,
  highlightBadge,
  onRated,
}: {
  movie: Movie;
  highlightBadge?: string;
  onRated?: (movieId: number, avgRating: number, ratingCount: number) => void;
}) {
  const [userRating, setUserRating] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [rateError, setRateError] = useState<string | null>(null);

  const genreList =
    movie.genres === "(no genres listed)" ? [] : movie.genres.split("|");

  async function handleRate(stars: number) {
    setSubmitting(true);
    setRateError(null);
    try {
      const res = await fetch(`${API_BASE}/ratings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: 1,
          movie_id: movie.movieId,
          rating: stars,
        }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Error ${res.status}`);
      }
      const data = await res.json();
      setUserRating(stars);
      if (onRated && data.updated_movie) {
        onRated(
          movie.movieId,
          data.updated_movie.avg_rating,
          data.updated_movie.rating_count
        );
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save rating";
      setRateError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="border border-zinc-200 dark:border-zinc-700 rounded-lg p-4 hover:shadow-md transition-shadow bg-white dark:bg-zinc-900 flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="font-semibold text-base text-zinc-900 dark:text-zinc-100">
            {movie.title}
          </h3>
          {highlightBadge && (
            <span className="shrink-0 px-2 py-0.5 text-[11px] font-medium rounded bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
              {highlightBadge}
            </span>
          )}
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          {genreList.map((genre) => (
            <span
              key={genre}
              className="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
            >
              {genre}
            </span>
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <StarRating rating={movie.avg_rating} />
          <span className="text-xs text-zinc-400">
            {movie.rating_count} rating{movie.rating_count !== 1 ? "s" : ""}
          </span>
        </div>

        {/* Interactive 1-5 Rating Action */}
        <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
          <span className="text-xs text-zinc-500">Rate:</span>
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                disabled={submitting}
                onClick={() => handleRate(star)}
                title={`Rate ${star} star${star > 1 ? "s" : ""}`}
                className={`px-1.5 py-0.5 text-xs rounded border transition-colors ${
                  userRating === star
                    ? "bg-yellow-400 border-yellow-500 text-zinc-900 font-bold"
                    : "border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-300 hover:bg-yellow-100 dark:hover:bg-yellow-900/30"
                } disabled:opacity-50`}
              >
                {star}★
              </button>
            ))}
          </div>
        </div>
        {userRating !== null && (
          <p className="text-[11px] text-green-600 dark:text-green-400 mt-1 text-right">
            Saved your rating: {userRating}/5
          </p>
        )}
        {rateError && (
          <p className="text-[11px] text-red-500 mt-1 text-right">{rateError}</p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Home & Catalog Page
// ---------------------------------------------------------------------------
export default function Home() {
  const [popular, setPopular] = useState<Movie[]>([]);
  const [popularLoading, setPopularLoading] = useState(true);
  const [popularError, setPopularError] = useState<string | null>(null);

  const [movies, setMovies] = useState<Movie[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 18;

  // Fetch Popular Right Now section
  useEffect(() => {
    setPopularLoading(true);
    setPopularError(null);
    fetch(`${API_BASE}/recommendations/popular?limit=6&min_ratings=50`)
      .then((res) => {
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        return res.json();
      })
      .then((data: PopularResponse) => {
        setPopular(data.items);
        setPopularLoading(false);
      })
      .catch((err) => {
        setPopularError(err.message || "Failed to load popular movies");
        setPopularLoading(false);
      });
  }, []);

  // Fetch paginated Catalog section
  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/items?limit=${limit}&offset=${offset}`)
      .then((res) => {
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        return res.json();
      })
      .then((data: ItemsResponse) => {
        setMovies(data.items);
        setTotal(data.total);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load movies");
        setLoading(false);
      });
  }, [offset]);

  // Update local card state when a user submits a rating
  function handleMovieRated(movieId: number, avgRating: number, ratingCount: number) {
    setMovies((prev) =>
      prev.map((m) =>
        m.movieId === movieId
          ? { ...m, avg_rating: avgRating, rating_count: ratingCount }
          : m
      )
    );
    setPopular((prev) =>
      prev.map((m) =>
        m.movieId === movieId
          ? { ...m, avg_rating: avgRating, rating_count: ratingCount }
          : m
      )
    );
  }

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black p-6">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
            🎬 AI Recommendation Engine
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 mt-2">
            Discover top-rated films and rate movies from our catalog of{" "}
            {total.toLocaleString()} titles.
          </p>
        </header>

        {/* Popular Right Now Section */}
        <section className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
              🔥 Popular Right Now
            </h2>
            <span className="text-xs text-zinc-500">
              Ranked by weighted rating (min. 50 reviews)
            </span>
          </div>

          {popularLoading && (
            <p className="text-sm text-zinc-500 py-4">Loading popular movies...</p>
          )}
          {popularError && (
            <p className="text-sm text-red-500 py-2">
              Could not load popular movies: {popularError}
            </p>
          )}
          {!popularLoading && !popularError && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {popular.map((movie, idx) => (
                <MovieCard
                  key={`pop-${movie.movieId}`}
                  movie={movie}
                  highlightBadge={`#${idx + 1} Popular`}
                  onRated={handleMovieRated}
                />
              ))}
            </div>
          )}
        </section>

        {/* Full Catalog Section */}
        <section>
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
            📚 Movie Catalog
          </h2>

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-zinc-500">Loading movies...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-center">
              <p className="text-red-600 dark:text-red-400 font-medium">
                ⚠️ Error: {error}
              </p>
              <p className="text-sm text-red-500 mt-1">
                Make sure the backend is running at {API_BASE}
              </p>
              <button
                onClick={() => {
                  setOffset(0);
                  setError(null);
                  setLoading(true);
                }}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {movies.map((movie) => (
                  <MovieCard
                    key={movie.movieId}
                    movie={movie}
                    onRated={handleMovieRated}
                  />
                ))}
              </div>

              <div className="flex items-center justify-center gap-4 mt-8">
                <button
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0}
                  className="px-4 py-2 rounded bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 disabled:opacity-40 hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors"
                >
                  ← Previous
                </button>
                <span className="text-sm text-zinc-500">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setOffset(offset + limit)}
                  disabled={offset + limit >= total}
                  className="px-4 py-2 rounded bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 disabled:opacity-40 hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors"
                >
                  Next →
                </button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
