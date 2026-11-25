# System Modules Specification: AI Recommendation Engine

This document defines the core functional modules of the AI Recommendation Engine, detailing their responsibilities, inputs, processing logic, and outputs.

---

### 1. Frontend UI
- **Responsibility**: Provides an interactive, responsive web user interface for browsing catalog items, viewing personalized recommendation feeds, and capturing user interactions.
- **Inputs**: User interaction events (clicks, likes, searches), user session IDs, and recommendation payloads from the Backend API.
- **Process**: Renders React 19 / Next.js client and server components, handles client-side state, dispatches asynchronous HTTP fetch requests to the API, and visualizes recommended items.
- **Outputs**: Rendered web views, user interaction events, and API request calls.

---

### 2. Backend API
- **Responsibility**: Serves as the primary secure gateway, routing client requests, validating schemas, coordinating cache queries, and delivering standardized JSON responses.
- **Inputs**: HTTP REST requests (user IDs, catalog filters, paging parameters).
- **Process**: Validates incoming request payloads using Pydantic, queries the Redis cache, delegates cache misses to the Recommendation Engine service, and formats API responses.
- **Outputs**: Formatted JSON responses (status codes, recommended item lists, latency metrics).

---

### 3. Recommendation Engine
- **Responsibility**: Generates personalized candidate rankings by calculating vector similarity between user preferences and item feature vectors.
- **Inputs**: User history, preference vectors, candidate item embeddings from PostgreSQL, and ranking parameters ($K$).
- **Process**: Performs cosine/inner-product similarity scoring via pgvector and scikit-learn models, applies post-filtering (deduplication, business rules), and ranks the top-$K$ candidates.
- **Outputs**: Ranked list of recommended item IDs paired with similarity/confidence scores.

---

### 4. Data Pipeline
- **Responsibility**: Ingests raw catalog and user behavior data, cleans and normalizes features, generates dense semantic embeddings, and loads structured records into PostgreSQL.
- **Inputs**: Raw datasets (CSV/JSON product catalogs, ratings, interaction logs).
- **Process**: Data preprocessing using pandas (handling nulls, deduplication, type casting), vectorization using scikit-learn / sentence-transformers, and bulk database ingestion.
- **Outputs**: Clean relational database tables and high-dimensional vector embeddings stored in PostgreSQL.

---

### 5. Database (PostgreSQL + pgvector)
- **Responsibility**: Acts as the single source of truth for persistent relational data, user metadata, and vector embeddings supporting high-performance similarity search.
- **Inputs**: Structured records, user profiles, catalog entities, and dense vector embeddings.
- **Process**: Executes transactional queries, manages relational constraints, and performs approximate nearest neighbor (ANN) vector indexing (HNSW/IVFFlat).
- **Outputs**: Persisted entity records, query result sets, and vector distance search results.

---

### 6. Cache (Redis)
- **Responsibility**: Provides high-speed in-memory caching for frequent recommendation queries to minimize database overhead and achieve sub-millisecond response times.
- **Inputs**: Query cache keys (e.g., `user:{id}:recommendations`), TTL parameters, and computed recommendation payloads.
- **Process**: Performs key-value lookups; returns stored results immediately on a cache hit, or stores newly calculated recommendation results on a cache miss.
- **Outputs**: Cached recommendation JSON payloads or cache-miss indicators.

---

### 7. Evaluation Module
- **Responsibility**: Evaluates the recommendation models offline to validate quality, relevance, and ranking efficacy before production deployment.
- **Inputs**: Historical test split interactions, ground-truth labels, and generated top-$K$ recommendation lists.
- **Process**: Computes standard recommendation metrics including Precision@$K$, Recall@$K$, Mean Average Precision (MAP), and NDCG in interactive Jupyter notebooks.
- **Outputs**: Metric summary tables, performance visualization plots, and benchmark reports.
