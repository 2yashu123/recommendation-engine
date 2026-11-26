"""
generate_submissions.py - Generates per-day submission PDFs (Days 4-10)
in docs/submissions/ using ReportLab.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, Preformatted, SimpleDocTemplate, Spacer

OUT_DIR = os.path.join(os.path.dirname(__file__), "submissions")
REPO_URL = "https://github.com/2yashu123/recommendation-engine"
STUDENT_NAME = "Yashaswini M G"


def get_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "SubTitle", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=22, textColor=colors.HexColor("#0f172a"), spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "SubMeta", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=13, textColor=colors.HexColor("#475569"), spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "SubH2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12.5, leading=16, textColor=colors.HexColor("#1e40af"),
            spaceBefore=10, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "SubBody", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=13.5, textColor=colors.HexColor("#1e293b"), spaceAfter=5,
        ),
        "placeholder": ParagraphStyle(
            "SubPlaceholder", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9.5, leading=14, textColor=colors.HexColor("#b45309"),
            backColor=colors.HexColor("#fef3c7"), borderPadding=6, spaceBefore=6, spaceAfter=8,
        ),
        "code": ParagraphStyle(
            "SubCode", parent=base["Code"], fontName="Courier",
            fontSize=8, leading=10.5, textColor=colors.HexColor("#0f172a"),
        ),
    }


def build_pdf(filename: str, day_title: str, sections: list[tuple[str, str, list[str]]], image_path: str | None = None):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    s = get_styles()
    doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=40, bottomMargin=40)

    story = [
        Paragraph(day_title, s["title"]),
        Paragraph(
            f"<b>Student:</b> {STUDENT_NAME} &nbsp;|&nbsp; <b>Track:</b> Full Stack with AI &nbsp;|&nbsp; "
            f"<b>Project:</b> AI Recommendation Engine<br/><b>Repository:</b> "
            f"<font color='#2563eb'>{REPO_URL}</font>",
            s["meta"],
        ),
    ]

    for heading, kind, content in sections:
        story.append(Paragraph(heading, s["h2"]))
        if kind == "body":
            for para in content:
                story.append(Paragraph(para, s["body"]))
        elif kind == "code":
            story.append(Preformatted("\n".join(content), s["code"]))
        elif kind == "placeholder":
            for p in content:
                story.append(Paragraph(p, s["placeholder"]))
        elif kind == "image" and image_path and os.path.exists(image_path):
            story.append(Image(image_path, width=480, height=288))
            for para in content:
                story.append(Paragraph(para, s["body"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    print(f"Created {path}")


def main():
    docs_dir = os.path.dirname(__file__)

    # Day 4
    build_pdf(
        "YashaswiniMG_Phase1_Day4.pdf",
        "Phase 1 Day 4 — Requirements Analysis & Development Plan",
        [
            ("1. What Was Implemented", "body", [
                "• Created <b>docs/requirements.md</b> covering Functional Requirements (FR-01 to FR-07), Non-Functional Requirements (NFR-01 to NFR-07, including <1s latency and zero secrets in Git), and User Requirements.",
                "• Built a Feature Breakdown Table (name, purpose, input, processing, output) and Module Breakdown with dependencies.",
                "• Applied MoSCoW prioritization (Must/Should/Could/Won't) mapped to the 8-stage project plan and created a per-module task checklist.",
                "• Updated <b>README.md</b> with a Requirements & Planning section linking to <i>docs/requirements.md</i> without deleting any existing content.",
            ]),
            ("2. Environment Check & Decisions", "body", [
                "• Verified Python 3.12.10, Node.js v20.18.0, npm 10.8.2, and Git 2.55.0 are working.",
                "• Docker Engine and local PostgreSQL (port 5432) were unreachable due to BIOS virtualization settings. Decided to use SQLite with SQLAlchemy for local development, keeping DATABASE_URL configurable for PostgreSQL later.",
            ]),
            ("3. Verification & Commit", "body", [
                "• Ran <i>git status</i> and a project-wide secret scan confirming .env was not staged.",
                "• Committed as <b>840fa13</b>: <i>\"Add requirements analysis and development plan\"</i>.",
            ]),
            ("4. Screenshot Placeholders", "placeholder", [
                "[INSERT SCREENSHOT: docs/requirements.md open showing MoSCoW prioritization & requirements]",
                "[INSERT SCREENSHOT: GitHub commit history showing Day 4 commit]",
            ]),
        ],
    )

    # Day 5
    build_pdf(
        "YashaswiniMG_Phase1_Day5.pdf",
        "Phase 1 Day 5 — Data Cleaning & Item Catalog Module",
        [
            ("1. What Was Implemented", "body", [
                "• Downloaded the MovieLens <b>ml-latest-small</b> dataset (9,742 movies, 100,836 ratings) into <i>data/raw/</i>.",
                "• Built <b>backend/app/services/data_loader.py</b> using pandas to drop missing values, remove duplicates, parse pipe-separated genres, extract release years, and compute average ratings and rating counts.",
                "• Saved cleaned outputs to <i>data/processed/movies_clean.csv</i> and <i>ratings_clean.csv</i>.",
                "• Added FastAPI endpoints <b>GET /items</b> (paginated with limit/offset) and <b>GET /items/{item_id}</b> (with 404 handling) in <b>backend/main.py</b>.",
                "• Built the Next.js catalog page in <b>frontend/src/app/page.tsx</b> displaying titles, genre badges, star ratings, pagination, loading spinner, and error/retry states.",
            ]),
            ("2. Real Testing Results", "code", [
                "Pipeline: 9,742 movies | 9,724 with ratings | 100,836 clean ratings | 610 users",
                "GET /items?limit=3&offset=0 -> 200 OK (total: 9742, first: Toy Story (1995))",
                "GET /items/1                -> 200 OK (Avg: 3.92, Count: 215)",
                "GET /items/999999           -> 404 Not Found",
                "Frontend npm run build      -> Compiled & TypeScript passed; GET / -> 200 OK",
            ]),
            ("3. Challenges & How They Were Addressed", "body", [
                "• <b>SSL Certificate Error:</b> Downloading MovieLens failed with <i>SSL: CERTIFICATE_VERIFY_FAILED</i>. Fixed using a custom SSL opener in Python to download the archive cleanly.",
                "• <b>Raw Data Ignore Rule:</b> Re-added <i>data/raw/</i> to <i>.gitignore</i> so raw zip/CSV files are never committed. Committed as <b>7abbdf5</b>.",
            ]),
            ("4. Screenshot Placeholders", "placeholder", [
                "[INSERT SCREENSHOT: Terminal output of data_loader.py showing 9,742 movies & 100,836 ratings]",
                "[INSERT SCREENSHOT: Swagger UI http://127.0.0.1:8000/docs testing GET /items]",
                "[INSERT SCREENSHOT: Next.js catalog page at http://localhost:3000]",
            ]),
        ],
    )

    # Day 6
    build_pdf(
        "YashaswiniMG_Phase1_Day6.pdf",
        "Phase 1 Day 6 — Popular Recommendations & Rating Action",
        [
            ("1. What Was Implemented", "body", [
                "• Reviewed Day 5 code and extracted catalog logic into <b>backend/app/services/catalog_service.py</b>, replacing deprecated startup events with FastAPI <i>lifespan</i>.",
                "• Added <b>GET /recommendations/popular</b> ranked by IMDb Weighted Rating: WR = (v/(v+m))*R + (m/(v+m))*C with minimum rating threshold (default 50).",
                "• Added <b>POST /ratings</b> with Pydantic validation (1.0–5.0), storing ratings in memory and temporary CSV (ready for Day 9 database migration).",
                "• Updated <b>frontend/src/app/page.tsx</b> with a <b>Popular Right Now</b> section and interactive <b>1★–5★ rating buttons</b> on every card.",
            ]),
            ("2. Real Testing Results", "code", [
                "GET /recommendations/popular?limit=5&min_ratings=50 -> 200 OK",
                "  #1 Shawshank Redemption, The (1994) | Avg: 4.43 | Count: 317 | WR: 4.271",
                "  #2 Fight Club (1999)               | Avg: 4.27 | Count: 218 | WR: 4.082",
                "POST /ratings (valid rating=5 for movieId=1) -> 201 Created (count: 215 -> 216)",
                "POST /ratings (invalid rating=6)             -> 422 Unprocessable Entity",
                "GET /items?limit=2                           -> 200 OK (catalog still works)",
                "Frontend npm run build & GET /               -> 200 OK",
            ]),
            ("3. Challenges & Commit", "body", [
                "• Ensured live UI state updates across both the Popular section and Catalog grid immediately after a user submits a star rating. Committed as <b>35554f7</b>.",
            ]),
            ("4. Screenshot Placeholders", "placeholder", [
                "[INSERT SCREENSHOT: Swagger UI testing GET /recommendations/popular]",
                "[INSERT SCREENSHOT: Next.js http://localhost:3000 showing Popular Right Now & Saved rating confirmation]",
            ]),
        ],
    )

    # Day 7
    build_pdf(
        "YashaswiniMG_Phase1_Day7.pdf",
        "Phase 1 Day 7 — Progress Review & Demo Preparation",
        [
            ("1. Demo Video Link", "placeholder", [
                "[INSERT DEMO VIDEO LINK HERE — 2 to 5 minute walkthrough recording]",
            ]),
            ("2. Honest Progress Summary", "body", [
                "• <b>Completed & Verified:</b> Python 3.12 + Node.js v20.18 + Git setup; modular folder structure; architecture & requirements docs; MovieLens cleaning pipeline (9,742 movies, 100,836 ratings); FastAPI endpoints (/, /items, /items/{id}, /recommendations/popular, /ratings); Next.js frontend with Popular Right Now, Catalog pagination, and 1–5 star ratings.",
                "• <b>Pending (Days 8–10 & Phase 2):</b> TF-IDF content-based similarity (Day 8), SQLite/SQLAlchemy schema & CRUD migration (Day 9), organized API router + pytest + API docs (Day 10), and Redis/PostgreSQL Docker deployment once BIOS virtualization is enabled.",
            ]),
            ("3. Next-Week Plan", "code", [
                "Day 8: Build TF-IDF + cosine similarity recommender & Similar Items UI panel",
                "Day 9: Design SQL schema & ER diagram, configure SQLAlchemy + SQLite, migrate CRUD",
                "Day 10: Refactor routes to backend/app/api/, write pytest suite, write docs/api.md",
                "Phase 2: Enable Docker virtualization -> PostgreSQL pgvector + Redis + Evaluation",
            ]),
            ("4. Challenges Addressed & Commit", "body", [
                "• Documented real challenges in <b>docs/progress-review.md</b> (Docker BIOS limitation, MovieLens SSL error, Git author config) and created a 3–4 minute demo script in <b>docs/demo-script.md</b>.",
                "• Updated <b>README.md</b> with a Current Status section. Committed as <b>3e97f07</b>.",
            ]),
            ("5. Screenshot Placeholders", "placeholder", [
                "[INSERT SCREENSHOT: docs/progress-review.md checklist]",
                "[INSERT SCREENSHOT: docs/demo-script.md walkthrough script]",
            ]),
        ],
    )

    # Day 8
    build_pdf(
        "YashaswiniMG_Phase1_Day8.pdf",
        "Phase 1 Day 8 — Content-Based Recommendations (TF-IDF)",
        [
            ("1. What Was Implemented", "body", [
                "• Built <b>ContentRecommender</b> in <b>backend/app/services/recommender.py</b> using scikit-learn <i>TfidfVectorizer</i> and <i>cosine_similarity</i> over movie titles and genres.",
                "• Added <b>GET /recommendations/similar/{item_id}?k=10</b> in <b>backend/main.py</b> with validation (404 when item_id is missing; 422 when k is outside 1–50).",
                "• Updated <b>frontend/src/app/page.tsx</b> with a <b>Find Similar Movies</b> button on every card that opens a <b>Similar to ...</b> panel showing top-6 matches with % match badges.",
            ]),
            ("2. Real Testing Results", "code", [
                "GET /recommendations/similar/1?k=5 (Toy Story (1995)) -> 200 OK:",
                "  #1 Toy Story 2 (1999)                    | Sim: 1.0",
                "  #2 Toy Story 3 (2010)                    | Sim: 0.8666",
                "  #3 Wild, The (2006)                      | Sim: 0.7442",
                "  #4 We're Back! A Dinosaur's Story (1993) | Sim: 0.7384",
                "  #5 Monsters, Inc. (2001)                 | Sim: 0.724",
                "GET /recommendations/similar/999999      -> 404 Not Found",
                "GET /recommendations/similar/1?k=100     -> 422 Validation Error",
                "Regression: GET /items & /recommendations/popular -> 200 OK; Frontend -> 200 OK",
            ]),
            ("3. Challenges & Commit", "body", [
                "• <b>Startup Timing:</b> Importing scikit-learn and fitting TF-IDF took ~3.5s, causing an initial 3s sleep test to fail with ConnectionRefusedError. Updated test verification to poll until ready. Committed as <b>e60c58a</b>.",
            ]),
            ("4. Screenshot Placeholders", "placeholder", [
                "[INSERT SCREENSHOT: Swagger UI testing GET /recommendations/similar/1?k=5]",
                "[INSERT SCREENSHOT: Next.js UI showing 'Similar to Toy Story (1995)' panel with % match badges]",
            ]),
        ],
    )

    # Day 9
    er_img = os.path.join(docs_dir, "er-diagram.png")
    build_pdf(
        "YashaswiniMG_Phase1_Day9.pdf",
        "Phase 1 Day 9 — Database Design & SQLAlchemy Integration",
        [
            ("1. What Was Implemented", "body", [
                "• Designed relational schema (<b>users</b>, <b>items</b>, <b>ratings</b>, <b>interactions</b>) in <b>db/schema.sql</b> and documented it with Mermaid + PNG ER diagrams in <b>docs/database.md</b>.",
                "• Configured SQLAlchemy in <b>backend/app/core/database.py</b> reading <i>DATABASE_URL</i> from <i>.env</i> (using SQLite locally, portable to PostgreSQL) and defined ORM models in <b>backend/app/models/db_models.py</b>.",
                "• Built and ran <b>backend/app/services/db_loader.py</b> to create all tables and bulk-load 610 users, 9,742 items, and 100,836 ratings.",
                "• Switched catalog, popular items, and Ratings CRUD (POST, GET, PUT, DELETE) in <b>backend/main.py</b> to SQLAlchemy while keeping TF-IDF recommendations working.",
            ]),
            ("2. Entity-Relationship Diagram", "image", [
                "ER Diagram generated via Python (docs/er-diagram.png) showing 1-to-Many relationships between users, items, ratings, and interactions.",
            ]),
            ("3. Real Connectivity & CRUD Output", "code", [
                "Connectivity check: OK (SELECT 1 succeeded)",
                "Row counts -> users: 610 | items: 9,742 | ratings: 100,836 | interactions: 0",
                "CRUD Test  -> POST /ratings (id=100837) -> GET /ratings -> PUT (3.5) -> DELETE -> OK",
            ]),
            ("4. Challenges & Commit", "body", [
                "• Docker Engine/PostgreSQL was unavailable locally; SQLAlchemy + SQLite allowed full relational modeling and CRUD integration while keeping <i>.env</i> and <i>*.db</i> excluded from Git. Committed as <b>c508ffc</b>.",
            ]),
            ("5. Screenshot Placeholders", "placeholder", [
                "[INSERT SCREENSHOT: Terminal output of db_loader.py showing connectivity check, row counts, and 5 sample rows]",
            ]),
        ],
        image_path=er_img,
    )

    # Day 10
    build_pdf(
        "YashaswiniMG_Phase1_Day10.pdf",
        "Phase 1 Day 10 — API Endpoints, Pytest Suite & Documentation",
        [
            ("1. What Was Implemented", "body", [
                "• Organized all 10 routes cleanly under <b>backend/app/api/routes.py</b> with Pydantic schemas in <b>backend/app/api/schemas.py</b> and SQLAlchemy error handling.",
                "• Final endpoints: <b>GET /health</b>, <b>GET /items</b>, <b>GET /items/{id}</b>, <b>GET /recommendations/popular</b>, <b>GET /recommendations/similar/{item_id}</b>, <b>POST /ratings</b>, <b>GET /ratings?user_id=</b>, <b>PUT /ratings/{id}</b>, <b>DELETE /ratings/{id}</b>, and <b>POST /interactions</b>.",
                "• Wrote 12 automated tests in <b>backend/tests/test_api.py</b> with pytest + TestClient.",
                "• Documented all endpoints in <b>docs/api.md</b>, recorded real HTTP test outputs in <b>docs/api-testing.md</b>, and updated <b>README.md</b> with run & test instructions.",
            ]),
            ("2. Real Testing Results", "code", [
                "pytest -v -> 12 passed in 3.66s (health, catalog, 404, popular, similar, 422, CRUD, interactions)",
                "Live HTTP checks -> All 10 endpoints verified returning 200 / 201 with real JSON payloads.",
            ]),
            ("3. Commit & Security", "body", [
                "• Added <i>.pytest_cache/</i> to <i>.gitignore</i>. Committed as <b>6ec71c9</b>: <i>\"Add API endpoints, tests and API documentation\"</i>.",
            ]),
            ("4. Screenshot Placeholders", "placeholder", [
                "[INSERT SCREENSHOT: Terminal output of pytest -v showing 12 passed]",
                "[INSERT SCREENSHOT: Swagger UI http://127.0.0.1:8000/docs showing all organized API tags]",
            ]),
        ],
    )


if __name__ == "__main__":
    main()
