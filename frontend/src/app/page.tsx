"use client";

import { useState, useEffect } from "react";

// ---------------------------------------------------------------------------
// Types - define the shape of data we get from the backend API
// ---------------------------------------------------------------------------
interface Movie {
  movieId: number;
  title: string;
  genres: string;
  year: number | null;
  avg_rating: number;
  rating_count: number;
}

interface ItemsResponse {
  total: number;
  limit: number;
  offset: number;
  items: Movie[];
}

// ---------------------------------------------------------------------------
// API base URL - points to our FastAPI backend
// ---------------------------------------------------------------------------
const API_BASE = "http://localhost:8000";

// ---------------------------------------------------------------------------
// Star Rating Display Component (read-only)
// ---------------------------------------------------------------------------
function StarRating({ rating }: { rating: number }) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.25;
  return (
    <span className="text-yellow-500 text-sm" title={`${rating.toFixed(1)} / 5`}>
      {"★".repeat(fullStars)}
      {hasHalf && "½"}
      {"☆".repeat(5 - fullStars - (hasHalf ? 1 : 0))}
      <span className="text-zinc-500 ml-1 text-xs">({rating.toFixed(1)})</span>
    </span>
  );
}

// ---------------------------------------------------------------------------
// Movie Card Component
// ---------------------------------------------------------------------------
function MovieCard({ movie }: { movie: Movie }) {
  // Split genres string like "Action|Comedy" into individual badges
  const genreList = movie.genres === "(no genres listed)"
    ? []
    : movie.genres.split("|");

  return (
    <div className="border border-zinc-200 dark:border-zinc-700 rounded-lg p-4 hover:shadow-md transition-shadow bg-white dark:bg-zinc-900">
      {/* Title and Year */}
      <h3 className="font-semibold text-lg text-zinc-900 dark:text-zinc-100 mb-1">
        {movie.title}
      </h3>

      {/* Genre Badges */}
      <div className="flex flex-wrap gap-1 mb-2">
        {genreList.map((genre) => (
          <span
            key={genre}
            className="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
          >
            {genre}
          </span>
        ))}
      </div>

      {/* Rating and Count */}
      <div className="flex items-center justify-between">
        <StarRating rating={movie.avg_rating} />
        <span className="text-xs text-zinc-400">
          {movie.rating_count} rating{movie.rating_count !== 1 ? "s" : ""}
        </span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Catalog Page
// ---------------------------------------------------------------------------
export default function Home() {
  // State: list of movies, loading/error flags, pagination
  const [movies, setMovies] = useState<Movie[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20; // items per page

  // Fetch movies from the backend API whenever offset changes
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

  // Calculate current page number and total pages
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black p-6">
      <div className="max-w-5xl mx-auto">
        {/* Page Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
            🎬 AI Recommendation Engine
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 mt-2">
            Browse our catalog of {total.toLocaleString()} movies. Discover your next favorite film.
          </p>
        </header>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-16">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-zinc-500">Loading movies...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-center">
            <p className="text-red-600 dark:text-red-400 font-medium">⚠️ Error: {error}</p>
            <p className="text-sm text-red-500 mt-1">
              Make sure the backend is running at {API_BASE}
            </p>
            <button
              onClick={() => { setOffset(0); setError(null); setLoading(true); }}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
            >
              Retry
            </button>
          </div>
        )}

        {/* Movie Grid */}
        {!loading && !error && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {movies.map((movie) => (
                <MovieCard key={movie.movieId} movie={movie} />
              ))}
            </div>

            {/* Pagination Controls */}
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
      </div>
    </div>
  );
}
