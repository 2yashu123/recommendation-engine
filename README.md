# AI Recommendation Engine

An end-to-end AI-powered Recommendation Engine designed to deliver personalized content and product recommendations in real time. The platform integrates a modern Next.js frontend with a high-performance Python FastAPI backend, leveraging PostgreSQL with pgvector for efficient vector similarity searches, Redis for low-latency caching, and machine learning pipelines built using pandas and scikit-learn.

## Tech Stack

- **Frontend**: Next.js 16 (React 19, TypeScript, Tailwind CSS, App Router)
- **Backend**: FastAPI (Python 3.12, Uvicorn)
- **Machine Learning & Data**: pandas, scikit-learn, Jupyter
- **Vector Database**: PostgreSQL 16 with pgvector extension (`pgvector/pgvector:pg16`)
- **In-Memory Cache**: Redis (`redis:7`)
- **Containerization**: Docker & Docker Compose

## Project Structure

```text
recommendation-engine/
├── backend/
│   ├── app/                 # FastAPI application modules
│   ├── venv/                # Python virtual environment (ignored in git)
│   ├── main.py              # Application entry point & routes
│   └── requirements.txt     # Python backend dependencies
├── frontend/
│   ├── src/                 # Next.js source code (App Router)
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies and scripts
│   └── tsconfig.json        # TypeScript configuration
├── data/                    # Dataset storage (raw and processed data)
│   └── raw/                 # Raw dataset files (ignored in git)
├── notebooks/               # Jupyter notebooks for data analysis & modeling
├── db/                      # Database migration scripts & schemas
├── docs/                    # Architecture diagrams & project documentation
├── docker-compose.yml       # Multi-container setup for pgvector and Redis
├── .env.example             # Template for required environment variables
├── .gitignore               # Root git ignore specification
└── README.md                # Project documentation
```

## Getting Started

### 1. Environment Configuration
Copy the template environment file and set your credentials:
```bash
cp .env.example .env
```

### 2. Backend Setup
Navigate to the `backend/` directory, activate the virtual environment, install dependencies, and start the development server:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`

### 3. Frontend Setup
Navigate to the `frontend/` directory, install dependencies, and launch the Next.js dev server:
```powershell
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:3000`

### 4. Database & Cache Services (Docker)
Once Docker virtualization is enabled on your machine, launch PostgreSQL (with pgvector) and Redis using:
```bash
docker compose up -d
```
