# Progress Review — Phase 1 (Day 7 Honest Status)

**Project:** AI Recommendation Engine  
**Author:** Yashaswini M G  
**Repository:** https://github.com/2yashu123/recommendation-engine  
**Review Date:** Phase 1, Day 7

---

## 1. Day 7 Verification Checklist

*Only items that have been actually built, run, and verified are marked complete.*

| Area | Item | Status | Verification Note |
|------|------|--------|-------------------|
| **Environment** | Python 3.12.10 + `backend/venv` | ✅ Done | Verified; FastAPI, pandas, scikit-learn, uvicorn installed |
| **Environment** | Node.js v20.18.0 + npm 10.8.2 | ✅ Done | Verified; Next.js 16 dependencies installed |
| **Environment** | Git 2.55.0 + GitHub repo | ✅ Done | Repo `recommendation-engine` created and linked |
| **Environment** | Docker Engine & PostgreSQL | ⏳ Deferred | Docker Engine unreachable (BIOS virtualization disabled); using SQLite for dev |
| **Structure** | Modular folder layout (`docs/folder-structure.md`) | ✅ Done | `backend/app/{api,core,models,services}`, `frontend/src/{app,components,lib}`, `data/{raw,processed}`, `db/`, `notebooks/`, `docs/` |
| **Structure** | `.gitignore` & `.env.example` | ✅ Done | `.env`, `venv/`, `node_modules/`, `.next/`, `data/raw/`, `*.pdf` excluded |
| **Docs** | System modules & architecture (`docs/modules.md`, `docs/architecture.md`, `architecture.png`) | ✅ Done | Written and diagram rendered with Python |
| **Docs** | Requirements & MoSCoW plan (`docs/requirements.md`) | ✅ Done | Written and linked in `README.md` |
| **Feature** | MovieLens dataset download & cleaning (`data_loader.py`) | ✅ Done | 9,742 movies & 100,836 ratings cleaned to `data/processed/` |
| **Feature** | Catalog API (`GET /items`, `GET /items/{id}`) | ✅ Working | Verified `200 OK` and `404` on missing IDs |
| **Feature** | Popular Items API (`GET /recommendations/popular`) | ✅ Working | Verified IMDb weighted rating ranking (`min_ratings=50`) |
| **Feature** | Rating submission (`POST /ratings`) | ✅ Working | Verified `201 Created` and `422` validation (currently stored in memory/CSV) |
| **Feature** | Next.js Catalog + Popular + Rating UI (`frontend/src/app/page.tsx`) | ✅ Working | `npm run build` passes and `http://localhost:3000` returns `200 OK` |

---

## 2. What Is Complete vs. Pending

### Complete (Verified Running)
- Local development environment (Python + Node.js + Git).
- Complete folder structure and architecture documentation.
- MovieLens `ml-latest-small` ingestion and cleaning pipeline (`movies_clean.csv`, `ratings_clean.csv`).
- FastAPI backend with `/`, `/items`, `/items/{id}`, `/recommendations/popular`, `/ratings`, and `/docs`.
- Next.js 16 frontend displaying **"Popular Right Now"**, paginated **Movie Catalog**, and **1–5 Star Rating** buttons.

### Pending (Upcoming Days)
- **Day 8:** Content-based similarity recommender (`GET /recommendations/similar/{item_id}`) using TF-IDF + cosine similarity (`scikit-learn`) and frontend "Similar Items" view.
- **Day 9:** SQLite/SQLAlchemy database schema (`users`, `items`, `ratings`, `interactions`), `db/schema.sql`, ER diagram (`docs/database.md`), and migrating catalog/popular/ratings from CSV to database.
- **Day 10:** Full CRUD API organization (`backend/app/api/`), `GET /health`, `GET/PUT/DELETE /ratings`, `POST /interactions`, `pytest` suite, and `docs/api.md`.
- **Phase 2 (Future):** Enable BIOS virtualization for Docker, switch `DATABASE_URL` to PostgreSQL + `pgvector`, add Redis caching and `sentence-transformers` embeddings, and run evaluation notebooks (`Precision@K`, `Recall@K`).

---

## 3. Real Challenges Encountered So Far

1. **Docker Engine Unreachable (Virtualization Disabled in BIOS):**
   - *Challenge:* `docker info` returned `Docker Engine not reachable` and `psql` was not installed locally (port 5432 closed).
   - *Resolution:* Chose SQLite + SQLAlchemy for local development (Day 9), keeping `DATABASE_URL` configurable via `.env` so switching to PostgreSQL + `pgvector` later requires no code rewrite.
2. **SSL Certificate Verification Error Downloading MovieLens:**
   - *Challenge:* Python `urllib.request.urlretrieve` failed with `SSL: CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate` on Windows.
   - *Resolution:* Used a custom SSL context with `urllib.request.build_opener` to successfully download `ml-latest-small.zip` (978 KB).
3. **Git Author Identity Not Set:**
   - *Challenge:* Initial commit failed with `Author identity unknown`.
   - *Resolution:* Configured global Git `user.name` (`yashaswini m g`) and `user.email` (`yashaswiniyash593@gmail.com`).

---

## 4. Realistic Next-Week Plan

| Day | Focus | Deliverable |
|-----|-------|-------------|
| **Day 8** | Content-Based Filtering | `recommender.py` with TF-IDF + cosine similarity, `GET /recommendations/similar/{item_id}`, frontend Similar Items panel |
| **Day 9** | Database Design & Integration | `db/schema.sql`, `docs/database.md` + ER diagram PNG, SQLAlchemy models, data loader script, CRUD migration to SQLite |
| **Day 10** | API Polish & Testing | Organized routes in `backend/app/api/`, `pytest` automated tests, live curl/REST test outputs, `docs/api.md` |
| **Submission** | Final Packaging | Screenshot checklist, per-day PDF reports (`docs/submissions/`), secret scan, push all commits to GitHub |
