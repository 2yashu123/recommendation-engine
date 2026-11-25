import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_diagram(output_path):
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    
    # Background color
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')
    
    # Title
    ax.text(7, 8.1, "AI Recommendation Engine — High-Level Architecture", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#0f172a')
    ax.text(7, 7.75, "End-to-End System Design: Online Real-Time Serving & Offline Data/Evaluation Loops", 
            ha='center', va='center', fontsize=11, color='#475569')

    # Group 1: Online Serving Box
    online_box = patches.FancyBboxPatch((0.5, 3.2), 13, 4.2, boxstyle="round,pad=0.2", 
                                        ec="#3b82f6", fc="#eff6ff", lw=1.5, ls="--")
    ax.add_patch(online_box)
    ax.text(0.8, 7.15, "ONLINE SERVING PIPELINE (Sub-50ms Latency)", fontsize=11, fontweight='bold', color='#1d4ed8')

    # Group 2: Offline Data Pipeline Box
    data_box = patches.FancyBboxPatch((0.5, 0.4), 6.5, 2.5, boxstyle="round,pad=0.2", 
                                      ec="#10b981", fc="#ecfdf5", lw=1.5, ls="--")
    ax.add_patch(data_box)
    ax.text(0.8, 2.65, "OFFLINE DATA PIPELINE", fontsize=11, fontweight='bold', color='#047857')

    # Group 3: Offline Model Evaluation Box
    eval_box = patches.FancyBboxPatch((7.5, 0.4), 6.0, 2.5, boxstyle="round,pad=0.2", 
                                      ec="#8b5cf6", fc="#f5f3ff", lw=1.5, ls="--")
    ax.add_patch(eval_box)
    ax.text(7.8, 2.65, "OFFLINE MODEL EVALUATION", fontsize=11, fontweight='bold', color='#6d28d9')

    # Nodes helper
    def draw_node(x, y, w, h, text, subtext, bg_color, border_color):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", 
                                      ec=border_color, fc=bg_color, lw=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.62, text, ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0f172a')
        ax.text(x + w/2, y + h*0.28, subtext, ha='center', va='center', fontsize=8.5, color='#475569')

    # Online Components
    draw_node(0.8, 5.0, 2.0, 1.3, "User / Browser", "Client Devices", "#ffffff", "#94a3b8")
    draw_node(3.3, 5.0, 2.2, 1.3, "Next.js Frontend", "React 19 / TypeScript", "#ffffff", "#3b82f6")
    draw_node(6.0, 5.0, 2.2, 1.3, "FastAPI Backend", "API Gateway / Routes", "#ffffff", "#3b82f6")
    draw_node(8.7, 5.7, 2.0, 1.1, "Redis Cache", "In-Memory (Hit/Miss)", "#fef3c7", "#f59e0b")
    draw_node(8.7, 3.8, 2.0, 1.2, "Reco Engine", "Candidate Ranking", "#ede9fe", "#8b5cf6")
    draw_node(11.2, 4.3, 2.0, 1.5, "PostgreSQL 16", "+ pgvector (HNSW)", "#e0e7ff", "#4338ca")

    # Arrows - Online
    # 1. User -> Frontend
    ax.annotate("", xy=(3.3, 5.65), xytext=(2.8, 5.65),
                arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.5))
    ax.text(3.05, 5.85, "Browse", ha='center', fontsize=8, color="#2563eb", fontweight='bold')

    # 2. Frontend -> FastAPI
    ax.annotate("", xy=(6.0, 5.65), xytext=(5.5, 5.65),
                arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.5))
    ax.text(5.75, 5.85, "REST", ha='center', fontsize=8, color="#2563eb", fontweight='bold')

    # 3. FastAPI -> Redis
    ax.annotate("", xy=(8.7, 6.25), xytext=(8.2, 5.9),
                arrowprops=dict(arrowstyle="->", color="#d97706", lw=1.5))
    ax.text(8.3, 6.35, "1. Cache Check", ha='center', fontsize=7.5, color="#d97706", fontweight='bold')

    # 4. Redis -> FastAPI (Cache Hit)
    ax.annotate("", xy=(8.2, 5.5), xytext=(8.7, 5.9),
                arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.2, ls="--"))
    ax.text(8.35, 5.3, "Hit: Return", ha='center', fontsize=7.5, color="#16a34a", fontweight='bold')

    # 5. Redis -> Reco Engine (Cache Miss)
    ax.annotate("", xy=(9.7, 5.0), xytext=(9.7, 5.7),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.2, ls="--"))
    ax.text(10.15, 5.35, "Miss", ha='center', fontsize=7.5, color="#dc2626", fontweight='bold')

    # 6. Reco Engine <-> PostgreSQL
    ax.annotate("", xy=(11.2, 4.9), xytext=(10.7, 4.5),
                arrowprops=dict(arrowstyle="->", color="#4338ca", lw=1.5))
    ax.text(10.85, 4.95, "Vector Query", ha='center', fontsize=7.5, color="#4338ca", fontweight='bold')

    ax.annotate("", xy=(10.7, 4.2), xytext=(11.2, 4.5),
                arrowprops=dict(arrowstyle="->", color="#4338ca", lw=1.2, ls=":"))
    ax.text(10.95, 3.95, "Candidates", ha='center', fontsize=7.5, color="#4338ca")

    # 7. Reco Engine -> FastAPI
    ax.annotate("", xy=(7.1, 5.0), xytext=(8.7, 4.4),
                arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=1.5))
    ax.text(7.6, 4.45, "Ranked List", ha='center', fontsize=7.5, color="#7c3aed", fontweight='bold')

    # Offline Data Components
    draw_node(0.8, 0.9, 1.7, 1.2, "Raw Datasets", "CSV / JSON (data/raw)", "#ffffff", "#10b981")
    draw_node(2.9, 0.9, 2.0, 1.2, "pandas ETL", "Clean & Deduplicate", "#ffffff", "#10b981")
    draw_node(5.2, 0.9, 1.6, 1.2, "Embeddings", "sentence-transformers", "#ffffff", "#10b981")

    # Offline Data Arrows
    ax.annotate("", xy=(2.9, 1.5), xytext=(2.5, 1.5),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5))
    ax.annotate("", xy=(5.2, 1.5), xytext=(4.9, 1.5),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5))
    
    # Ingest into PostgreSQL
    ax.annotate("", xy=(12.0, 4.3), xytext=(6.8, 1.5),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5, 
                                connectionstyle="angle,angleA=0,angleB=90,rad=10"))
    ax.text(8.8, 1.7, "Batch Vector & Metadata Ingestion", ha='center', fontsize=8, color="#059669", fontweight='bold')

    # Offline Eval Components
    draw_node(7.8, 0.9, 2.3, 1.2, "Evaluation Suite", "Jupyter Notebooks", "#ffffff", "#8b5cf6")
    draw_node(10.7, 0.9, 2.5, 1.2, "Ranking Metrics", "Precision@K, Recall@K", "#ffffff", "#8b5cf6")

    # Offline Eval Arrows
    ax.annotate("", xy=(10.7, 1.5), xytext=(10.1, 1.5),
                arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=1.5))
    
    # Query from PostgreSQL to Eval
    ax.annotate("", xy=(8.95, 2.1), xytext=(12.2, 4.3),
                arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=1.2, ls=":",
                                connectionstyle="angle,angleA=-90,angleB=0,rad=10"))
    ax.text(11.2, 2.8, "Test Interactions & Vectors", ha='center', fontsize=7.5, color="#7c3aed")

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated diagram at {output_path}")

def generate_pdf(pdf_path, img_path):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Phase 1 Day 3 — Project Structure & System Architecture", title_style))
    story.append(Paragraph("<b>Student:</b> Yashaswini M G &nbsp;|&nbsp; <b>Track:</b> Full Stack with AI &nbsp;|&nbsp; <b>Project:</b> AI Recommendation Engine<br/><b>Repository:</b> <font color='#2563eb'>https://github.com/2yashu123/recommendation-engine</font>", subtitle_style))
    story.append(Spacer(1, 4))

    # Section 1: Project Organization
    story.append(Paragraph("1. Project Organization and Rationale", h2_style))
    org_text = (
        "The project follows an industry-standard monorepo-style structure that cleanly decouples the client application, "
        "API gateway, machine learning services, and database persistence. The <b>frontend/</b> directory isolates Next.js 16 (App Router) "
        "user interface components, client libraries, and routing. The <b>backend/</b> directory encloses a high-throughput FastAPI application, "
        "logically partitioned into API routers (<b>api/</b>), business and recommendation algorithms (<b>services/</b>), Pydantic schemas (<b>models/</b>), "
        "central configurations (<b>core/</b>), and test suites (<b>tests/</b>). The <b>data/</b> folder enforces strict data governance by segregating immutable "
        "source datasets (<b>raw/</b>) from cleaned feature vectors (<b>processed/</b>). The <b>db/</b> folder centralizes SQL migrations and initialization scripts for PostgreSQL pgvector, "
        "the <b>notebooks/</b> directory preserves exploratory workflows and model evaluation scripts, and <b>docs/</b> hosts engineering specifications and architecture artifacts."
    )
    story.append(Paragraph(org_text, body_style))
    story.append(Spacer(1, 4))

    # Section 2: Folder Structure Tree
    story.append(Paragraph("2. Repository Folder Structure", h2_style))
    tree_text = (
        "recommendation-engine/\n"
        "├── backend/                  # FastAPI Application Service\n"
        "│   ├── app/                  # Modular backend packages\n"
        "│   │   ├── api/              # Route controllers & endpoints\n"
        "│   │   ├── core/             # App configs, CORS, logging\n"
        "│   │   ├── models/           # Pydantic & SQLAlchemy models\n"
        "│   │   └── services/         # Reco algorithms & vector scoring\n"
        "│   ├── tests/                # Pytest unit & integration tests\n"
        "│   ├── main.py               # FastAPI entry point\n"
        "│   └── requirements.txt      # Python dependencies\n"
        "├── frontend/                 # Next.js 16 Web Application\n"
        "│   ├── src/app/              # Next.js App Router (pages/layouts)\n"
        "│   ├── src/components/       # Reusable React UI components\n"
        "│   └── src/lib/              # Utility functions & API clients\n"
        "├── data/                     # Data Lake\n"
        "│   ├── raw/                  # Original raw datasets (gitignored)\n"
        "│   └── processed/            # Cleaned data & vector caches\n"
        "├── db/                       # PostgreSQL migrations & schemas\n"
        "├── docs/                     # Specifications, architecture, reports\n"
        "├── notebooks/                # Jupyter EDA & offline evaluation\n"
        "├── docker-compose.yml        # PostgreSQL (pgvector) + Redis setup\n"
        "└── README.md                 # Project landing page & documentation"
    )
    story.append(Preformatted(tree_text, code_style))
    story.append(Spacer(1, 6))

    # Section 3: Module List with Descriptions
    story.append(Paragraph("3. System Modules Specification", h2_style))
    modules_data = [
        [Paragraph("<b>Module</b>", body_style), Paragraph("<b>Responsibility</b>", body_style), Paragraph("<b>Key Technologies</b>", body_style)],
        [Paragraph("<b>Frontend UI</b>", body_style), Paragraph("Renders item feeds, captures user clicks, displays personalized recommendations.", body_style), Paragraph("Next.js 16, React 19, Tailwind", body_style)],
        [Paragraph("<b>Backend API</b>", body_style), Paragraph("Serves REST endpoints, validates request payloads, orchestrates cache queries.", body_style), Paragraph("FastAPI, Pydantic, Uvicorn", body_style)],
        [Paragraph("<b>Reco Engine</b>", body_style), Paragraph("Executes vector similarity scoring, top-K ranking, and business filtering.", body_style), Paragraph("scikit-learn, pgvector", body_style)],
        [Paragraph("<b>Data Pipeline</b>", body_style), Paragraph("Cleans raw datasets, handles missing values, generates dense embeddings.", body_style), Paragraph("pandas, sentence-transformers", body_style)],
        [Paragraph("<b>Database</b>", body_style), Paragraph("Stores relational records and executes ANN vector distance queries.", body_style), Paragraph("PostgreSQL 16, pgvector (HNSW)", body_style)],
        [Paragraph("<b>Cache Layer</b>", body_style), Paragraph("In-memory caching of frequent recommendations for sub-5ms retrieval.", body_style), Paragraph("Redis 7", body_style)],
        [Paragraph("<b>Evaluation</b>", body_style), Paragraph("Measures offline model quality using Precision@K, Recall@K, and NDCG.", body_style), Paragraph("Jupyter, scikit-learn", body_style)],
    ]
    t = Table(modules_data, colWidths=[90, 310, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Section 4: Architecture Diagram Image & Explanation
    story.append(Paragraph("4. System Architecture & Data Flow", h2_style))
    if os.path.exists(img_path):
        story.append(Image(img_path, width=520, height=315))
        story.append(Spacer(1, 4))
    
    arch_desc = (
        "<b>Architecture Flow:</b> The architecture is segmented into an online serving loop and two offline loops. "
        "In the online flow, a user interaction triggers a REST call from Next.js to FastAPI. The API first checks Redis for cached recommendations. "
        "On a <i>cache hit</i>, precomputed results are returned immediately with sub-millisecond latency. On a <i>cache miss</i>, the query routes "
        "to the Recommendation Engine, which executes approximate nearest neighbor (ANN) vector queries on PostgreSQL with pgvector, ranks the top candidates, "
        "updates Redis, and returns the response. In the offline data pipeline, raw CSV/JSON data is ingested, cleaned with pandas, vectorized using "
        "sentence-transformers, and stored in PostgreSQL. In the offline evaluation loop, Jupyter notebooks benchmark predictions against ground truth using Precision@K and Recall@K."
    )
    story.append(Paragraph(arch_desc, body_style))
    story.append(Spacer(1, 8))

    # Section 5: README Update Note
    story.append(Paragraph("5. README.md Documentation Update", h2_style))
    readme_note = (
        "The project's root <b>README.md</b> was comprehensively updated to reflect the expanded modular architecture and development milestones. "
        "Without removing any prior setup instructions or configuration guides, new sections were introduced: <i>Project Overview</i>, <i>System Modules</i>, "
        "<i>Updated Folder Structure</i>, <i>Architecture & Data Flow</i> (embedding the architecture diagram), and a multi-phase <i>Development Plan</i> "
        "guiding future implementation phases."
    )
    story.append(Paragraph(readme_note, body_style))

    doc.build(story)
    print(f"Successfully generated PDF report at {pdf_path}")

if __name__ == '__main__':
    base_dir = r"C:\Users\Dell\Documents\recommendation-engine\docs"
    img_file = os.path.join(base_dir, "architecture.png")
    pdf_file = os.path.join(base_dir, "YashaswiniMG_Phase1_Day3.pdf")
    
    generate_diagram(img_file)
    generate_pdf(pdf_file, img_file)
