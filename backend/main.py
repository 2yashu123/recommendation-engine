"""
main.py - FastAPI application entry point for the AI Recommendation Engine.

Day 10 updates:
- Organized all routes under app/api/routes.py
- Added /health and /interactions endpoints
- Attached ContentRecommender to app.state during lifespan startup
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.database import Base, SessionLocal, engine
from app.services.db_catalog_service import load_items_dataframe_from_db
from app.services.recommender import ContentRecommender


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure tables exist and fit TF-IDF ContentRecommender from database items."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        df = load_items_dataframe_from_db(db)
        app.state.recommender = ContentRecommender(df)
        print(f"Database connected. Loaded {len(df)} items & built TF-IDF matrix.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="AI Recommendation Engine",
    description="Backend API powered by FastAPI, SQLAlchemy, and scikit-learn.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def read_root():
    """Root status endpoint."""
    return {"status": "ok"}


app.include_router(api_router)
