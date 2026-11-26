-- ============================================================================
-- AI Recommendation Engine - Relational Database Schema
-- Compatible with SQLite (local development) and PostgreSQL (production)
-- ============================================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Items (Movies) Table
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,               -- Maps to MovieLens movieId
    title VARCHAR(255) NOT NULL,
    clean_title VARCHAR(255),
    genres VARCHAR(255) NOT NULL,
    year INTEGER,
    avg_rating REAL DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Ratings Table
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Use SERIAL in PostgreSQL
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    rating REAL NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- 4. Interactions Table (clicks, views, similar_item_clicks)
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Use SERIAL in PostgreSQL
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    interaction_type VARCHAR(50) NOT NULL, -- e.g. 'view', 'click', 'similar_click'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings (user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_item_id ON ratings (item_id);
CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions (user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_item_id ON interactions (item_id);
