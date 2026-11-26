# Day 8 Notes — Content-Based Recommendations (TF-IDF)

## 1. Similarity Module (`backend/app/services/recommender.py`)
- Built `ContentRecommender` using `scikit-learn`'s `TfidfVectorizer(stop_words="english")` and `cosine_similarity`.
- Combined `clean_title` and parsed `genres` into a single content text feature (weighting genres so genre alignment remains strong).
- Mapped `movieId` to matrix row index for $O(1)$ lookup and computed cosine similarity on demand against all 9,742 movies.

## 2. Backend Endpoint (`GET /recommendations/similar/{item_id}`)
- Added `GET /recommendations/similar/{item_id}?k=10` in `backend/main.py`.
- Validated `k` (`1 <= k <= 50`) using FastAPI `Query` constraints (`422` on out-of-range values) and returned `404` when `item_id` does not exist.

## 3. Frontend Integration (`frontend/src/app/page.tsx`)
- Added a **"✨ Find Similar Movies"** button to every movie card in both the Popular and Catalog sections.
- Clicking it opens the **"✨ Similar to ..."** panel at the top of the page showing top-6 similar items with `% match` badges.

## 4. Test Results
- **Challenge during testing:** Initial test script waited 3s for startup and hit `ConnectionRefusedError` because importing `scikit-learn` and fitting TF-IDF took ~3.5s. Updated the test runner to poll `/`, after which all checks passed.
- **`GET /recommendations/similar/1?k=5` (*Toy Story*)** &rarr; `200 OK`:
  1. *Toy Story 2 (1999)* (`Sim: 1.0`)
  2. *Toy Story 3 (2010)* (`Sim: 0.8666`)
  3. *Wild, The (2006)* (`Sim: 0.7442`)
  4. *We're Back! A Dinosaur's Story (1993)* (`Sim: 0.7384`)
  5. *Monsters, Inc. (2001)* (`Sim: 0.724`)
- **`GET /recommendations/similar/999999` (invalid ID)** &rarr; `404 Not Found` (`Item with id 999999 not found.`).
- **`GET /recommendations/similar/1?k=100` (`k` too large)** &rarr; `422 Unprocessable Entity`.
- **Day 5 & 6 regression check:** `GET /items` (`200 OK`) and `GET /recommendations/popular` (`200 OK`) still work.
