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
  similarity_score?: number;
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

interface SimilarResponse {
  source_item: Movie;
  k: number;
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
// Movie Card with Rating Action & "Find Similar" Button
// ---------------------------------------------------------------------------
function MovieCard({
  movie,
  highlightBadge,
  isSelected,
  onSelectSimilar,
  onRated,
}: {
  movie: Movie;
  highlightBadge?: string;
  isSelected?: boolean;
  onSelectSimilar?: (movie: Movie) => void;
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
    <div
      className={`border rounded-lg p-4 hover:shadow-md transition-shadow bg-white dark:bg-zinc-900 flex flex-col justify-between ${
        isSelected
          ? "border-blue-500 ring-2 ring-blue-300 dark:ring-blue-800"
          : "border-zinc-200 dark:border-zinc-700"
      }`}
    >
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

        {onSelectSimilar && (
          <button
            type="button"
            onClick={() => onSelectSimilar(movie)}
            className="mt-2.5 w-full py-1.5 px-3 text-xs font-medium rounded bg-indigo-50 text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-950 dark:text-indigo-300 dark:hover:bg-indigo-900 transition-colors"
          >
            ✨ Find Similar Movies
          </button>
        )}

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

  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
  const [similarLoading, setSimilarLoading] = useState(false);
  const [similarError, setSimilarError] = useState<string | null>(null);

  const [movies, setMovies] = useState<Movie[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 18;

  // Fetch Popular Right Now
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

  // Fetch Catalog
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

  // Fetch Similar Items when a movie is selected
  async function handleSelectSimilar(movie: Movie) {
    setSelectedMovie(movie);
    setSimilarLoading(true);
    setSimilarError(null);
    try {
      const res = await fetch(
        `${API_BASE}/recommendations/similar/${movie.movieId}?k=6`
      );
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Error ${res.status}`);
      }
      const data: SimilarResponse = await res.json();
      setSimilarMovies(data.items);
      // Scroll smoothly to the Similar Items section
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load similar movies";
      setSimilarError(msg);
      setSimilarMovies([]);
    } finally {
      setSimilarLoading(false);
    }
  }

  function handleMovieRated(movieId: number, avgRating: number, ratingCount: number) {
    const updater = (list: Movie[]) =>
      list.map((m) =>
        m.movieId === movieId
          ? { ...m, avg_rating: avgRating, rating_count: ratingCount }
          : m
      );
    setMovies(updater);
    setPopular(updater);
    setSimilarMovies(updater);
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
            Discover top-rated films, click &quot;Find Similar Movies&quot; for content-based recommendations, and rate titles from our catalog of{" "}
            {total.toLocaleString()} movies.
          </p>
        </header>

        {/* Similar Items Panel (shown when a movie is clicked) */}
        {selectedMovie && (
          <section className="mb-10 p-5 rounded-xl border-2 border-indigo-300 dark:border-indigo-800 bg-indigo-50/50 dark:bg-indigo-950/20">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <h2 className="text-xl font-semibold text-indigo-950 dark:text-indigo-200">
                  ✨ Similar to &quot;{selectedMovie.title}&quot;
                </h2>
                <p className="text-xs text-indigo-700 dark:text-indigo-400 mt-0.5">
                  Content-based recommendations via TF-IDF + Cosine Similarity ({selectedMovie.genres})
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setSelectedMovie(null);
                  setSimilarMovies([]);
                }}
                className="px-3 py-1 text-xs rounded bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-300"
              >
                ✕ Close
              </button>
            </div>

            {similarLoading && (
              <p className="text-sm text-indigo-600 py-4">
                Computing TF-IDF similarity...
              </p>
            )}
            {similarError && (
              <p className="text-sm text-red-500 py-2">Error: {similarError}</p>
            )}
            {!similarLoading && !similarError && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {similarMovies.map((movie) => (
                  <MovieCard
                    key={`sim-${movie.movieId}`}
                    movie={movie}
                    highlightBadge={
                      movie.similarity_score !== undefined
                        ? `${Math.round(movie.similarity_score * 100)}% match`
                        : undefined
                    }
                    onSelectSimilar={handleSelectSimilar}
                    onRated={handleMovieRated}
                  />
                ))}
              </div>
            )}
          </section>
        )}

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
                  isSelected={selectedMovie?.movieId === movie.movieId}
                  onSelectSimilar={handleSelectSimilar}
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
                    isSelected={selectedMovie?.movieId === movie.movieId}
                    onSelectSimilar={handleSelectSimilar}
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
