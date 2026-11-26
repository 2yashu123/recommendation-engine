"""
db_loader.py - Creates database tables and loads cleaned MovieLens data from
data/processed/ into the database (SQLite or PostgreSQL).

Also prints a connectivity check, table row counts, and 5 sample rows.
"""

import os
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import text
from app.core.database import engine, SessionLocal, Base, DATABASE_URL
from app.models.db_models import User, Item, Rating

DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed")
)
MOVIES_CSV = os.path.join(DATA_DIR, "movies_clean.csv")
RATINGS_CSV = os.path.join(DATA_DIR, "ratings_clean.csv")


def init_and_load():
    print("=" * 60)
    print("DATABASE INITIALIZATION & DATA LOADER")
    print("=" * 60)
    safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"Target DB: {safe_url}")

    # 1. Connectivity check
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Connectivity check: OK (SELECT 1 succeeded)")

    # 2. Create tables
    Base.metadata.create_all(bind=engine)
    print("Tables created/verified: users, items, ratings, interactions")

    db = SessionLocal()
    try:
        existing_items = db.query(Item).count()
        if existing_items > 0:
            print(f"Database already populated ({existing_items} items). Skipping duplicate load.")
        else:
            # Load cleaned CSVs
            movies_df = pd.read_csv(MOVIES_CSV)
            ratings_df = pd.read_csv(RATINGS_CSV)

            # Insert unique users from ratings
            unique_user_ids = sorted(ratings_df["userId"].unique().tolist())
            user_mappings = [
                {"id": int(uid), "username": f"user_{int(uid)}"}
                for uid in unique_user_ids
            ]
            db.bulk_insert_mappings(User, user_mappings)
            db.commit()
            print(f"Inserted {len(user_mappings)} users")

            # Insert items (movies)
            item_mappings = []
            for _, row in movies_df.iterrows():
                item_mappings.append({
                    "id": int(row["movieId"]),
                    "title": str(row["title"]),
                    "clean_title": str(row.get("clean_title", row["title"])),
                    "genres": str(row["genres"]),
                    "year": int(row["year"]) if pd.notna(row.get("year")) else None,
                    "avg_rating": round(float(row["avg_rating"]), 2),
                    "rating_count": int(row["rating_count"]),
                })
            db.bulk_insert_mappings(Item, item_mappings)
            db.commit()
            print(f"Inserted {len(item_mappings)} items")

            # Insert ratings in batches
            rating_mappings = []
            for _, row in ratings_df.iterrows():
                ts = datetime.fromtimestamp(int(row["timestamp"]), tz=timezone.utc)
                rating_mappings.append({
                    "user_id": int(row["userId"]),
                    "item_id": int(row["movieId"]),
                    "rating": float(row["rating"]),
                    "created_at": ts,
                    "updated_at": ts,
                })
            batch_size = 10000
            for start in range(0, len(rating_mappings), batch_size):
                db.bulk_insert_mappings(Rating, rating_mappings[start : start + batch_size])
                db.commit()
            print(f"Inserted {len(rating_mappings)} ratings")

        # 3. Print verification summary & 5 sample rows
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY (Table Row Counts)")
        print("=" * 60)
        for tbl in ["users", "items", "ratings", "interactions"]:
            cnt = db.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"  {tbl:15s}: {cnt:,} rows")

        print("\nSample 5 rows from items table:")
        rows = db.execute(
            text("SELECT id, title, genres, avg_rating, rating_count FROM items LIMIT 5")
        ).fetchall()
        for r in rows:
            print(f"  id={r[0]} | {r[1]} | {r[2]} | avg={r[3]} | count={r[4]}")

        print("\nSample 5 rows from ratings table:")
        r_rows = db.execute(
            text("SELECT id, user_id, item_id, rating FROM ratings LIMIT 5")
        ).fetchall()
        for r in r_rows:
            print(f"  id={r[0]} | user_id={r[1]} | item_id={r[2]} | rating={r[3]}")

    finally:
        db.close()


if __name__ == "__main__":
    init_and_load()
