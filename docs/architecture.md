# System Architecture: AI Recommendation Engine

This document outlines the high-level architecture of the AI Recommendation Engine, detailing the online serving flow, the offline data pipeline, and the model evaluation loop.

---

## Architecture Diagram

```mermaid
flowchart TD
    subgraph OnlineServing["Online Inference Flow"]
        User["User / Client Browser"]
        Frontend["Next.js Frontend (React 19)"]
        API["FastAPI Backend Gateway"]
        Cache{"Redis Cache (Port 6379)"}
        Engine["Recommendation Engine Service"]
        DB[(PostgreSQL 16 + pgvector)]

        User -->|1. Browses / Requests Items| Frontend
        Frontend -->|2. HTTP REST Request| API
        API -->|3. Check Cache (user:id:recs)| Cache
        Cache -->|3a. Cache HIT: Return cached JSON| API
        Cache -->|3b. Cache MISS| Engine
        Engine -->|4. Query Vector Similarity (<->)| DB
        DB -->|5. Return Nearest Neighbor Items| Engine
        Engine -->|6. Rank Top-K & Write to Cache| Cache
        Engine -->|7. Return Ranked Recommendations| API
        API -->|8. JSON Response Payload| Frontend
        Frontend -->|9. Render Recommended UI Cards| User
    end

    subgraph OfflineData["Offline Data Pipeline"]
        RawData["Raw Datasets (CSV / JSON)"]
        PandasCleaning["pandas Data Cleaning & Preprocessing"]
        EmbeddingGen["Embedding Generation (sentence-transformers)"]
        
        RawData -->|Ingest| PandasCleaning
        PandasCleaning -->|Clean Features| EmbeddingGen
        EmbeddingGen -->|Store Vectors & Metadata| DB
    end

    subgraph OfflineEval["Offline Model Evaluation"]
        EvalNotebook["Evaluation Notebooks (Jupyter)"]
        Metrics["Performance Metrics (Precision@K, Recall@K, NDCG@K)"]

        DB -.->|Query Ground Truth & Predictions| EvalNotebook
        EvalNotebook -->|Compute Ranking Efficacy| Metrics
    end
```

---

## Data Flow Explanation

### 1. Online Inference Path (Sub-50ms Response)
1. **User Interaction**: The user interacts with the Next.js web application (viewing home feed or product details).
2. **API Request**: Next.js issues an authenticated asynchronous fetch call to the FastAPI `/api/v1/recommendations` endpoint.
3. **Cache Lookup**: FastAPI immediately inspects Redis using the key pattern `recs:user:{id}`:
   - **Cache Hit**: Redis returns the precomputed serialized recommendation list directly. The API returns this to the frontend, achieving sub-millisecond retrieval.
   - **Cache Miss**: When cache expires or no key exists, execution falls back to the **Recommendation Engine**.
4. **Vector Search & Ranking**: The Recommendation Engine queries PostgreSQL with the `pgvector` extension to perform an approximate nearest neighbor (ANN) cosine distance calculation against candidate item embeddings.
5. **Cache Warm-up & Delivery**: The engine computes the final ranked top-$K$ items, writes the result to Redis with a configurable TTL, and returns the response payload through FastAPI to Next.js.

### 2. Offline Data Preparation Pipeline
1. **Raw Ingestion**: New catalog metadata and historical user-item interactions land in `data/raw/`.
2. **Cleaning**: Python scripts utilizing `pandas` handle deduplication, impute missing values, and normalize features into `data/processed/`.
3. **Embedding Vectorization**: Pretrained `sentence-transformers` models compute dense dimensional semantic embeddings for each item.
4. **Storage**: The relational records and vector embeddings are bulk loaded into PostgreSQL tables indexed with `HNSW` or `IVFFlat` indexes.

### 3. Model Evaluation Loop
1. **Offline Benchmark**: Data scientists run Jupyter notebooks in `notebooks/` to load holdout evaluation test sets.
2. **Metric Assessment**: The system benchmarks model quality against standard ranking metrics, specifically **Precision@K** (fraction of recommended items that are relevant) and **Recall@K** (fraction of relevant items successfully recommended).
