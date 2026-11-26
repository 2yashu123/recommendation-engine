# Day 5 Notes — Data Cleaning & Item Catalog Module

## 1. Dataset Acquisition
- **Dataset:** MovieLens `ml-latest-small` (`https://files.grouplens.org/datasets/movielens/ml-latest-small.zip`).
- **Challenge Encountered:** The initial Python `urllib.request.urlretrieve` call failed with `[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`.
- **Fix Applied:** Used a custom SSL context with `urllib.request.build_opener` to download the public dataset archive (`978,202` bytes) and extracted `movies.csv`, `ratings.csv`, `links.csv`, `tags.csv`, and `README.txt` into `data/raw/ml-latest-small/`.

## 2. Data Cleaning Pipeline (`backend/app/services/data_loader.py`)
- Loaded `movies.csv` (`9,742` rows) and `ratings.csv` (`100,836` rows) using `pandas`.
- Handled missing values, removed duplicate `movieId` / `(userId, movieId)` pairs (keeping the latest rating by timestamp), and validated ratings in the `0.5–5.0` range.
- Extracted release `year` and `clean_title`, parsed pipe-separated genres, and computed `avg_rating` and `rating_count` per movie (`9,724` movies had ratings).
- Saved cleaned outputs to `data/processed/movies_clean.csv` and `data/processed/ratings_clean.csv`.

## 3. Backend API (`backend/main.py`)
- Added CORS middleware allowing `http://localhost:3000`.
- Loaded `data/processed/movies_clean.csv` on server startup.
- Implemented `GET /items?limit=20&offset=0` for paginated catalog retrieval.
- Implemented `GET /items/{item_id}` for single movie details with `404` error handling for missing IDs.

### Backend Test Results
- `GET /` &rarr; `200 OK` (`{"status": "ok"}`)
- `GET /items?limit=3&offset=0` &rarr; `200 OK` (`total: 9742`, returned 3 movies including *Toy Story (1995)* with Avg `3.92`, Count `215`)
- `GET /items/1` &rarr; `200 OK` (returned *Toy Story (1995)* details)
- `GET /items/999999` &rarr; `404 Not Found` (`Item with id 999999 not found.`)
- `GET /docs` &rarr; `200 OK`

## 4. Frontend Catalog Page (`frontend/src/app/page.tsx`)
- Built a client-side catalog page fetching `/items` from `http://localhost:8000`.
- Displays movie titles, genre badges, star ratings, rating counts, pagination controls (`Previous` / `Next`), loading spinner, and error/retry state.
- Verified with `npm run build` (TypeScript and production build passed) and `npm run dev` (`GET /` returned `200 OK`).
