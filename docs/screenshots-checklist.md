# Screenshots Checklist — Phase 1 (Days 4–10)

Take these screenshots on your computer and insert them into the matching `[INSERT SCREENSHOT: ...]` placeholders in each day's PDF under `docs/submissions/`.

**How to start both servers before taking UI/API screenshots:**
- **Backend (Terminal 1):**
  ```powershell
  cd C:\Users\Dell\Documents\recommendation-engine\backend
  .\venv\Scripts\uvicorn.exe main:app --reload --host 127.0.0.1 --port 8000
  ```
- **Frontend (Terminal 2):**
  ```powershell
  cd C:\Users\Dell\Documents\recommendation-engine\frontend
  npm run dev
  ```

---

## Day 4 — Requirements & Planning
1. **Requirements Document**: Open `docs/requirements.md` in VS Code / Antigravity showing the Functional/Non-Functional Requirements and MoSCoW table.
2. **GitHub Commit**: Open `https://github.com/2yashu123/recommendation-engine` showing commit `Add requirements analysis and development plan`.

## Day 5 — Data Cleaning & Item Catalog
1. **Data Pipeline Terminal Output**: Run in `backend/`:
   ```powershell
   .\venv\Scripts\python.exe -m app.services.data_loader
   ```
   *Must be visible:* `Total movies: 9742`, `Total clean ratings: 100836`, and `Saved enriched movies to ...movies_clean.csv`.
2. **Catalog API in Swagger UI**: Open `http://127.0.0.1:8000/docs`, expand `GET /items`, click **Try it out** &rarr; **Execute**, showing the `200` JSON response.
3. **Frontend Catalog Page**: Open `http://localhost:3000` in your browser showing movie cards with titles, genre badges, star ratings, and pagination controls.

## Day 6 — Popular Recommendations & Rating Action
1. **Popular Endpoint in Swagger UI**: Open `http://127.0.0.1:8000/docs`, execute `GET /recommendations/popular`, showing *Shawshank Redemption* / *Fight Club* with `weighted_score`.
2. **Frontend "Popular Right Now" + Rating Action**: Open `http://localhost:3000` showing the **🔥 Popular Right Now** section at the top and click a `5★` button on a card so `Saved your rating: 5/5` is visible.

## Day 7 — Progress Review & Demo Prep
1. **Progress Review Document**: Open `docs/progress-review.md` showing the completed checklist and next-week plan.
2. **Demo Script Document**: Open `docs/demo-script.md` showing the 2–5 minute walkthrough script.

## Day 8 — Content-Based Recommendations (TF-IDF)
1. **Similar Items API**: Open `http://127.0.0.1:8000/docs`, execute `GET /recommendations/similar/1?k=5` showing *Toy Story 2*, *Toy Story 3*, etc., with `similarity_score`.
2. **Frontend "Similar to ..." Panel**: On `http://localhost:3000`, click **✨ Find Similar Movies** on *Toy Story (1995)* (or any popular movie) and capture the **✨ Similar to ...** panel with `% match` badges.

## Day 9 — Database Design & SQLAlchemy Integration
1. **ER Diagram**: Open `docs/er-diagram.png` showing the 4 tables (`users`, `items`, `ratings`, `interactions`) and their relationships.
2. **Database Connectivity & Sample Rows**: Run in `backend/`:
   ```powershell
   .\venv\Scripts\python.exe -m app.services.db_loader
   ```
   *Must be visible:* `Connectivity check: OK (SELECT 1 succeeded)`, row counts (`610`, `9,742`, `100,836`), and the 5 sample rows from `items` and `ratings`.

## Day 10 — API Routes, Pytest & Documentation
1. **Pytest Results**: Run in `backend/`:
   ```powershell
   .\venv\Scripts\pytest.exe -v
   ```
   *Must be visible:* `12 passed` in green.
2. **Swagger UI All Endpoints**: Open `http://127.0.0.1:8000/docs` showing all organized endpoint groups (`Health`, `Catalog`, `Recommendations`, `Ratings`, `Interactions`).
