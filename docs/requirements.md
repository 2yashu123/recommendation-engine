# Requirements Analysis & Development Plan

**Project:** AI Recommendation Engine  
**Author:** Yashaswini M G  
**Repository:** https://github.com/2yashu123/recommendation-engine  
**Date:** Phase 1, Day 4

---

## 1. Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-01 | Item Catalog Browsing | Users can browse a paginated catalog of movies with title, genres, and average rating. |
| FR-02 | Item Detail View | Users can view detailed information about a single item by its ID. |
| FR-03 | Popular Items Fallback | The system recommends popular items (ranked by weighted rating) when no personalized data is available. |
| FR-04 | Content-Based Recommendations | Given an item, the system returns similar items using TF-IDF on genres and titles. |
| FR-05 | User Ratings | Users can submit, view, update, and delete ratings (1–5 stars) for items. |
| FR-06 | Interaction Tracking | The system logs user interactions (clicks, views) for future model improvement. |
| FR-07 | Health Check Endpoint | A `/health` endpoint reports API status for monitoring. |

---

## 2. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Response Time | API responses under 1 second for all endpoints. |
| NFR-02 | Security — No Secrets in Git | Passwords, API keys, and tokens are never committed. `.env` is in `.gitignore`; only `.env.example` with placeholders is tracked. |
| NFR-03 | Code Readability | Clean, commented code with simple explanations a beginner can understand and explain. |
| NFR-04 | Database Portability | SQLAlchemy ORM with configurable `DATABASE_URL` so the app works with SQLite (dev) or PostgreSQL (prod) without code changes. |
| NFR-05 | CORS Support | Backend allows cross-origin requests from the Next.js frontend (localhost:3000). |
| NFR-06 | Input Validation | All endpoints validate inputs with Pydantic; return proper HTTP status codes (200, 201, 404, 422). |
| NFR-07 | Error Handling | Meaningful error messages for invalid requests, missing items, and database errors. |

---

## 3. User Requirements

| User | Need | Acceptance Criteria |
|------|------|---------------------|
| Visitor | Browse available movies | Catalog page loads with titles, genres, and ratings. Pagination works. |
| Visitor | See what's popular | "Popular Right Now" section shows top-rated movies with enough reviews. |
| Visitor | Find similar movies | Clicking an item shows a list of similar items based on content. |
| Registered User | Rate movies | Can submit a 1–5 star rating. Can update or delete their rating. |
| Developer | Run the project locally | Clear setup instructions in README. Single command to start backend and frontend. |
| Evaluator | Verify API works | Swagger docs at `/docs`. All endpoints return correct status codes. |

---

## 4. Feature Breakdown Table

| Feature | Purpose | Input | Processing | Output |
|---------|---------|-------|------------|--------|
| Data Cleaning | Prepare raw MovieLens data for use | Raw CSV files (movies.csv, ratings.csv) | pandas: handle nulls, remove duplicates, parse genres, compute avg rating & count | Cleaned CSV in `data/processed/` |
| Item Catalog API | Serve browsable item list | Query params: `limit`, `offset` | Read processed data, paginate results | JSON array of items with title, genres, avg rating |
| Item Detail API | Serve single item info | Path param: `item_id` | Lookup item by ID, return 404 if missing | JSON object with full item details |
| Popular Items | Recommend widely-liked items | Query param: `limit` | Weighted rating formula with minimum vote threshold | JSON array of top-rated items |
| Content-Based Recs | Suggest similar items | Path param: `item_id`, query: `k` | TF-IDF vectorization on genres+title, cosine similarity | JSON array of k similar items with scores |
| User Ratings CRUD | Let users rate items | POST/PUT body: `user_id`, `item_id`, `rating` (1–5) | Validate input, store in database, handle duplicates | Created/updated rating object |
| Interaction Logging | Track user behavior | POST body: `user_id`, `item_id`, `interaction_type` | Insert interaction record with timestamp | 201 Created confirmation |
| Health Check | Monitor API status | GET request | Return status and timestamp | `{"status": "ok", "timestamp": "..."}` |

---

## 5. Module Breakdown — Responsibilities & Dependencies

| Module | Responsibility | Depends On |
|--------|---------------|------------|
| **Data Pipeline** (`backend/app/services/data_loader.py`) | Download, clean, and preprocess the MovieLens dataset | pandas, raw data files |
| **Database Layer** (`backend/app/core/`, `backend/app/models/`) | SQLAlchemy engine, session management, ORM models | SQLAlchemy, database URL from `.env` |
| **Item Service** (`backend/app/services/`) | Business logic for item lookup and catalog queries | Database Layer, Data Pipeline (initial load) |
| **Recommender Service** (`backend/app/services/recommender.py`) | TF-IDF similarity computation and popular item ranking | scikit-learn, Item Service |
| **API Layer** (`backend/app/api/`) | FastAPI route handlers, Pydantic schemas, error responses | Item Service, Recommender Service, Database Layer |
| **Frontend** (`frontend/src/`) | Next.js pages and components for catalog, detail, ratings UI | Backend API (fetch calls) |
| **Evaluation** (`notebooks/`) | Offline accuracy measurement (Precision@K, Recall@K) | Processed data, recommender logic |

---

## 6. MoSCoW Prioritization

Mapped to the 8-stage implementation plan:

### Must Have (Critical — project fails without these)
| Stage | Feature | Day |
|-------|---------|-----|
| 1 | Dataset acquisition and data cleaning pipeline | Day 5 |
| 2 | Database schema design and table creation | Day 9 |
| 3 | Item catalog API (GET /items, GET /items/{id}) | Day 5 |
| 4 | Popular items fallback (GET /recommendations/popular) | Day 6 |
| 5 | Content-based recommendations (GET /recommendations/similar/{id}) | Day 8 |
| 6 | FastAPI route organization with validation and error handling | Day 10 |

### Should Have (Important — expected in a complete submission)
| Stage | Feature | Day |
|-------|---------|-----|
| 7 | User ratings CRUD (POST/GET/PUT/DELETE /ratings) | Days 6, 9, 10 |
| 8 | Frontend catalog page with loading/error states | Day 5 |
| 8 | Frontend "Popular Right Now" section | Day 6 |
| 8 | Frontend "Similar Items" display | Day 8 |

### Could Have (Nice additions if time allows)
| Feature | Notes |
|---------|-------|
| Redis caching layer | Prepared in docker-compose.yml; implement when Docker works |
| Embedding-based collaborative filtering | Requires sentence-transformers; planned for Phase 2 |
| Interaction tracking endpoint | Simple POST /interactions for future model improvement |
| Evaluation notebook with Precision@K, Recall@K | Offline benchmarking in notebooks/ |

### Won't Have (This phase)
| Feature | Reason |
|---------|--------|
| User authentication / login | Out of scope for Phase 1 |
| Real-time model retraining | Requires MLOps infrastructure |
| Production deployment (cloud hosting) | Phase 2+ |
| Collaborative filtering with neural embeddings | Requires sentence-transformers and larger dataset |

---

## 7. Development Task List Per Module

### Data Pipeline Module (Day 5)
- [ ] Download MovieLens ml-latest-small dataset to `data/raw/`
- [ ] Write `data_loader.py`: load CSVs with pandas
- [ ] Handle missing values and remove duplicate rows
- [ ] Parse pipe-separated genres into lists
- [ ] Compute average rating and rating count per movie
- [ ] Save cleaned data to `data/processed/`

### Database Module (Day 9)
- [ ] Design schema: users, items, ratings, interactions tables
- [ ] Write `db/schema.sql` with CREATE TABLE statements
- [ ] Create `docs/database.md` with ER diagram (Mermaid + PNG)
- [ ] Implement SQLAlchemy models in `backend/app/models/`
- [ ] Configure database connection in `backend/app/core/`
- [ ] Write data loading script to populate tables from processed CSVs
- [ ] Add `DATABASE_URL` placeholder to `.env.example`

### API Module (Days 5, 6, 8, 10)
- [ ] GET /health — return status and timestamp
- [ ] GET /items — paginated item list with limit/offset
- [ ] GET /items/{id} — single item detail with 404 handling
- [ ] GET /recommendations/popular — weighted rating ranked list
- [ ] GET /recommendations/similar/{item_id} — TF-IDF content similarity
- [ ] POST /ratings — create a rating (validate 1–5 range)
- [ ] GET /ratings?user_id= — list ratings for a user
- [ ] PUT /ratings/{id} — update an existing rating
- [ ] DELETE /ratings/{id} — remove a rating
- [ ] POST /interactions — log a user interaction
- [ ] Add Pydantic request/response schemas
- [ ] Configure CORS middleware
- [ ] Write pytest tests for main endpoints

### Recommender Module (Days 6, 8)
- [ ] Implement weighted rating formula for popular items
- [ ] Build TF-IDF matrix on genres + title text
- [ ] Implement cosine similarity search for similar items
- [ ] Add input validation (item exists, k within 1–50 range)

### Frontend Module (Days 5, 6, 8)
- [ ] Catalog page: fetch GET /items, display cards with title/genres/rating
- [ ] Loading spinner and error state handling
- [ ] Item detail view: fetch GET /items/{id}
- [ ] "Popular Right Now" section: fetch GET /recommendations/popular
- [ ] Rating component: 1–5 star selector, POST to backend
- [ ] "Similar Items" section: fetch GET /recommendations/similar/{id}

### Documentation & Review (Days 4, 7)
- [ ] Requirements document (this file)
- [ ] Progress review and honest status report
- [ ] Demo script for walkthrough video
- [ ] API documentation with endpoint details
- [ ] Screenshot checklist for submission
