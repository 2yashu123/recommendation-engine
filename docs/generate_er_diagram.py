"""Generate a clean ER diagram PNG at docs/er-diagram.png using matplotlib."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def draw_table(ax, x, y, w, title, fields, header_color="#1e40af"):
    row_h = 0.34
    h = (len(fields) + 1) * row_h + 0.15
    # Outer box
    box = patches.FancyBboxPatch(
        (x, y - h), w, h,
        boxstyle="round,pad=0.05",
        ec=header_color, fc="#ffffff", lw=1.6
    )
    ax.add_patch(box)

    # Header bar
    header = patches.FancyBboxPatch(
        (x, y - row_h - 0.05), w, row_h + 0.05,
        boxstyle="round,pad=0.05",
        ec=header_color, fc=header_color, lw=1.0
    )
    ax.add_patch(header)
    ax.text(x + w / 2, y - row_h / 2 - 0.02, title,
            ha="center", va="center", fontsize=11, fontweight="bold", color="#ffffff")

    # Fields
    for idx, (col, col_type, badge) in enumerate(fields):
        fy = y - (idx + 1.5) * row_h - 0.08
        label = f"{badge} {col}" if badge else f"   {col}"
        ax.text(x + 0.12, fy, label, ha="left", va="center",
                fontsize=8.8, fontweight="bold" if badge else "normal", color="#0f172a")
        ax.text(x + w - 0.12, fy, col_type, ha="right", va="center",
                fontsize=8.3, color="#475569")
    return (x, y, w, h)


def main():
    fig, ax = plt.subplots(figsize=(12, 7.2), dpi=200)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")

    ax.text(6, 6.85, "AI Recommendation Engine — Entity-Relationship (ER) Diagram",
            ha="center", va="center", fontsize=15, fontweight="bold", color="#0f172a")
    ax.text(6, 6.5, "SQLAlchemy ORM Schema (SQLite Dev / PostgreSQL Prod)",
            ha="center", va="center", fontsize=10, color="#475569")

    # USERS (top-left)
    draw_table(ax, 0.7, 5.9, 3.0, "USERS", [
        ("id", "INTEGER", "PK"),
        ("username", "VARCHAR(100)", ""),
        ("created_at", "TIMESTAMP", ""),
    ], header_color="#0f766e")

    # ITEMS (top-right)
    draw_table(ax, 8.1, 6.0, 3.3, "ITEMS (Movies)", [
        ("id", "INTEGER", "PK"),
        ("title", "VARCHAR(255)", ""),
        ("clean_title", "VARCHAR(255)", ""),
        ("genres", "VARCHAR(255)", ""),
        ("year", "INTEGER", ""),
        ("avg_rating", "REAL", ""),
        ("rating_count", "INTEGER", ""),
        ("created_at", "TIMESTAMP", ""),
    ], header_color="#1d4ed8")

    # RATINGS (bottom-left)
    draw_table(ax, 0.7, 2.9, 3.3, "RATINGS", [
        ("id", "INTEGER", "PK"),
        ("user_id", "INTEGER", "FK"),
        ("item_id", "INTEGER", "FK"),
        ("rating", "REAL (0.5-5.0)", ""),
        ("created_at", "TIMESTAMP", ""),
        ("updated_at", "TIMESTAMP", ""),
    ], header_color="#7c3aed")

    # INTERACTIONS (bottom-right)
    draw_table(ax, 7.9, 2.3, 3.5, "INTERACTIONS", [
        ("id", "INTEGER", "PK"),
        ("user_id", "INTEGER", "FK"),
        ("item_id", "INTEGER", "FK"),
        ("interaction_type", "VARCHAR(50)", ""),
        ("created_at", "TIMESTAMP", ""),
    ], header_color="#b45309")

    # Relationships
    # USERS -> RATINGS (1:N)
    ax.annotate("", xy=(2.2, 2.95), xytext=(2.2, 4.35),
                arrowprops=dict(arrowstyle="->", color="#0f766e", lw=1.8))
    ax.text(2.35, 3.65, "1 : N\nsubmits", fontsize=8.5, color="#0f766e", fontweight="bold")

    # ITEMS -> RATINGS (1:N)
    ax.annotate("", xy=(4.05, 2.0), xytext=(8.05, 4.3),
                arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=1.6,
                                connectionstyle="arc3,rad=0.15"))
    ax.text(5.8, 3.4, "1 : N receives", fontsize=8.5, color="#1d4ed8", fontweight="bold")

    # USERS -> INTERACTIONS (1:N)
    ax.annotate("", xy=(7.85, 1.5), xytext=(3.75, 4.8),
                arrowprops=dict(arrowstyle="->", color="#0f766e", lw=1.5, ls="--",
                                connectionstyle="arc3,rad=-0.12"))
    ax.text(5.5, 4.45, "1 : N performs", fontsize=8.5, color="#0f766e", fontweight="bold")

    # ITEMS -> INTERACTIONS (1:N)
    ax.annotate("", xy=(9.7, 2.35), xytext=(9.7, 2.75),
                arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=1.8))
    ax.text(9.85, 2.55, "1 : N", fontsize=8.5, color="#1d4ed8", fontweight="bold")

    out_path = os.path.join(os.path.dirname(__file__), "er-diagram.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Generated ER diagram at {out_path}")


if __name__ == "__main__":
    main()
