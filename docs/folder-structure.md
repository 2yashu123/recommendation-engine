# Project Folder Structure: AI Recommendation Engine

This document provides a clean overview of the repository's directory layout, highlighting the role and purpose of each folder.

```text
recommendation-engine/
├── .env.example                     # Template environment variables
├── .gitignore                       # Ignored files (node_modules, venv, secrets, logs)
├── docker-compose.yml               # Multi-container orchestration (pgvector + Redis)
├── README.md                        # Project landing page & documentation
│
├── backend/                         # FastAPI backend service
│   ├── app/
│   │   ├── api/                     # REST API endpoints, routers, and request handlers
│   │   ├── core/                    # App configuration, environment settings, security
│   │   ├── models/                  # Database models and Pydantic validation schemas
│   │   └── services/                # Recommendation algorithms & vector search logic
│   ├── tests/                       # Unit, integration, and API test suites
│   ├── main.py                      # Application bootstrap and ASGI entry point
│   └── requirements.txt             # Python dependencies
│
├── frontend/                        # Next.js 16 frontend application
│   ├── public/                      # Static assets (SVGs, favicons, branding)
│   ├── src/
│   │   ├── app/                     # Next.js App Router (layout, pages, globals.css)
│   │   ├── components/              # Modular, reusable UI components (cards, filters)
│   │   └── lib/                     # API client utilities, constants, helper functions
│   ├── package.json                 # Node.js dependencies and npm run scripts
│   └── tsconfig.json                # TypeScript compiler configuration
│
├── data/                            # Dataset storage
│   ├── raw/                         # Raw, unmodified source datasets
│   └── processed/                   # Cleaned, normalized datasets and embeddings
│
├── db/                              # Database schemas, migrations, and seed scripts
├── docs/                            # Project specifications, diagrams, and reports
└── notebooks/                       # Jupyter notebooks for data analysis & model evaluation
```

---

### Folder Roles and Justifications

- **`backend/app/api/`**: Keeps API route handlers modular, organized by domain (e.g., `/recommendations`, `/items`, `/health`).
- **`backend/app/services/`**: Isolates recommendation logic, embedding generation, and Redis caching from the transport/API layer.
- **`backend/app/models/`**: Defines Pydantic request/response schemas and SQLAlchemy database entities.
- **`backend/app/core/`**: Houses centralized application settings (`pydantic-settings`), logging configuration, and CORS rules.
- **`backend/tests/`**: Contains pytest test cases ensuring reliability of endpoints and recommendation ranking logic.
- **`frontend/src/components/`**: Houses reusable React components (e.g., `RecommendationCard`, `Navbar`, `SearchBar`).
- **`frontend/src/lib/`**: Contains API fetch wrappers and utility functions shared across Next.js pages.
- **`data/raw/` vs `data/processed/`**: Preserves original source data in `raw/` while storing cleaned arrays and vector caches in `processed/`.
- **`db/`**: Holds SQL initialization scripts (such as `CREATE EXTENSION vector;`) and table definitions.
- **`notebooks/`**: Dedicated space for exploratory data analysis, prototype experiments, and offline model evaluation.
- **`docs/`**: Central repository for architecture diagrams, module documentation, and project milestone submissions.
