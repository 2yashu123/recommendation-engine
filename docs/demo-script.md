# Demo Video Script (2–5 Minutes)

**Title:** AI Recommendation Engine — Phase 1 Progress Demo  
**Presenter:** Yashaswini M G  
**Repository:** https://github.com/2yashu123/recommendation-engine  
**Target Duration:** ~3–4 minutes

---

## 1. Introduction & Problem Solved (~30 seconds)
> "Hi, I'm Yashaswini M G, and this is my Phase 1 demo for the **AI Recommendation Engine** project.  
> Users browsing large catalogs—like thousands of movies—often face choice overload and leave without finding what they like. This project solves that by building a full-stack recommendation system that surfaces popular items for new users and will deliver personalized content-based suggestions."

## 2. Tech Stack & Project Structure (~45 seconds)
*(Show VS Code / Explorer tree and `docs/architecture.png`)*
> "On the frontend, I'm using **Next.js 16** with TypeScript and Tailwind CSS. On the backend, I'm using **Python FastAPI** with **pandas** and **scikit-learn** for data processing and ML. For deployment, I prepared `docker-compose.yml` for **PostgreSQL with pgvector** and **Redis**, and for local development I'm using **SQLite with SQLAlchemy** so the database is portable.  
> Everything is organized cleanly into `frontend/`, `backend/app/`, `data/raw/` and `data/processed/`, `db/`, `notebooks/`, and `docs/`."

## 3. Live Walkthrough Order (~2 minutes)

### Step A: Show Cleaned Data (`data/processed/movies_clean.csv`)
> "First, I downloaded the MovieLens `ml-latest-small` dataset and wrote `data_loader.py` using pandas to drop missing values, remove duplicates, parse genres, and compute average ratings and rating counts across 9,742 movies and 100,836 ratings."

### Step B: Show FastAPI Swagger UI (`http://localhost:8000/docs`)
*(Start backend: `uvicorn main:app --reload --port 8000`)*
> "Here is the live FastAPI backend at `http://localhost:8000/docs`. We have:
> - `GET /` returning `{"status": "ok"}`
> - `GET /items` returning paginated movies (`limit` and `offset`)
> - `GET /items/{item_id}` for a single movie, returning `404` if not found
> - `GET /recommendations/popular` which ranks movies using the IMDb weighted rating formula with a minimum of 50 ratings
> - `POST /ratings` which validates a 1–5 star score with Pydantic and saves it."

*(Execute `GET /recommendations/popular?limit=3` live in Swagger UI to show the JSON response)*

### Step C: Show Next.js Frontend (`http://localhost:3000`)
*(Start frontend: `npm run dev`)*
> "Now looking at the Next.js frontend at `http://localhost:3000`:
> - At the top is the **Popular Right Now** section connected to `/recommendations/popular`, showing top-ranked classics like *The Shawshank Redemption* and *Fight Club*.
> - Below that is the **Movie Catalog** connected to `/items` with genre badges, star ratings, and Previous/Next pagination.
> - Every movie card also has **1★–5★ rating buttons** that POST directly to `/ratings` and immediately update the rating count and average on screen."

*(Click a star rating button live on Toy Story to show the "Saved your rating" confirmation and updated count)*

## 4. Challenges & Next Steps (~30 seconds)
> "Two main challenges I ran into were: first, Docker virtualization isn't enabled in my BIOS yet, so I set up SQLAlchemy to support SQLite locally while staying ready to switch to PostgreSQL later; and second, an SSL certificate issue when downloading MovieLens, which I resolved with a custom opener in `data_loader.py`.  
> Next, I'll add TF-IDF content-based similar item recommendations, migrate data into SQLite tables with full CRUD, and add automated pytest tests. Thank you for watching!"
