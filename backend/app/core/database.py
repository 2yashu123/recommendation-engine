"""
database.py - SQLAlchemy engine and session configuration.

Reads DATABASE_URL from the root .env file.
Defaults to SQLite (sqlite:///./recommendation.db) for local development
and switches to PostgreSQL automatically when DATABASE_URL is updated.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from the root .env file
ROOT_ENV = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
)
load_dotenv(ROOT_ENV)

DEFAULT_SQLITE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "recommendation.db")
)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

# SQLite requires check_same_thread=False for FastAPI multi-threaded requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and closes it safely."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
