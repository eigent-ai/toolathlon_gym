"""Preprocess script for terminal-canvas-arxiv-word-excel-notion task.
Canvas is read-only. Clear arxiv, notion schemas. Inject arxiv papers.
"""
import argparse
import glob
import json
import os
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_arxiv(cur):
    print("[preprocess] Clearing arxiv data...")
    cur.execute("DELETE FROM arxiv.papers")
    print("[preprocess] arxiv data cleared.")


def clear_notion(cur):
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    print("[preprocess] Notion data cleared.")


def inject_arxiv_papers(cur):
    print("[preprocess] Injecting arxiv papers...")
    papers = [
        {"id": "2025.01001", "title": "Deep Learning for Time Series Analytics: A Survey",
         "authors": json.dumps([{"name": "Alice Zhang"}, {"name": "Bob Chen"}]),
         "summary": "A comprehensive survey of deep learning methods for time series data analytics and algorithm design including forecasting and classification.",
         "categories": json.dumps(["cs.LG", "cs.AI"]), "primary_category": "cs.LG",
         "published": "2025-01-15T00:00:00Z", "updated": "2025-01-15T00:00:00Z"},
        {"id": "2025.01002", "title": "Reinforcement Learning in Financial Markets",
         "authors": json.dumps([{"name": "Carol Davis"}, {"name": "David Lee"}]),
         "summary": "This paper explores reinforcement learning approaches for financial analysis, portfolio optimization, and algorithmic trading strategies.",
         "categories": json.dumps(["cs.AI", "q-fin.TR"]), "primary_category": "cs.AI",
         "published": "2025-02-10T00:00:00Z", "updated": "2025-02-10T00:00:00Z"},
        {"id": "2025.01003", "title": "Data-Driven Design Optimization Using Neural Networks",
         "authors": json.dumps([{"name": "Eve Wilson"}, {"name": "Frank Brown"}]),
         "summary": "Novel data-driven approaches to engineering design optimization using neural network surrogate models and computational methods.",
         "categories": json.dumps(["cs.LG", "cs.CE"]), "primary_category": "cs.LG",
         "published": "2025-01-20T00:00:00Z", "updated": "2025-01-20T00:00:00Z"},
        {"id": "2025.01004", "title": "Computational Methods for Environmental Economics Modeling",
         "authors": json.dumps([{"name": "Grace Kim"}, {"name": "Henry Park"}]),
         "summary": "Advanced computational methods for environmental economics modeling including climate risk assessment and sustainability metrics.",
         "categories": json.dumps(["econ.GN", "cs.CE"]), "primary_category": "econ.GN",
         "published": "2025-03-01T00:00:00Z", "updated": "2025-03-01T00:00:00Z"},
        {"id": "2025.01005", "title": "Machine Learning Algorithms for Geopolitical Risk Assessment",
         "authors": json.dumps([{"name": "Irene Johnson"}, {"name": "Jack Smith"}]),
         "summary": "Application of machine learning algorithms and data analytics to geopolitical risk scoring and global governance analysis.",
         "categories": json.dumps(["cs.AI", "cs.CY"]), "primary_category": "cs.AI",
         "published": "2025-02-28T00:00:00Z", "updated": "2025-02-28T00:00:00Z"},
        # Noise papers
        {"id": "2025.02001", "title": "Quantum Error Correction in Superconducting Qubits",
         "authors": json.dumps([{"name": "Karen White"}]),
         "summary": "Progress in quantum error correction codes for superconducting qubit architectures.",
         "categories": json.dumps(["quant-ph"]), "primary_category": "quant-ph",
         "published": "2025-01-05T00:00:00Z", "updated": "2025-01-05T00:00:00Z"},
        {"id": "2025.02002", "title": "Dark Matter Detection via Gravitational Lensing",
         "authors": json.dumps([{"name": "Leo Martinez"}]),
         "summary": "New methods for dark matter detection using weak gravitational lensing surveys.",
         "categories": json.dumps(["astro-ph.CO"]), "primary_category": "astro-ph.CO",
         "published": "2025-02-01T00:00:00Z", "updated": "2025-02-01T00:00:00Z"},
        {"id": "2025.02003", "title": "Protein Folding with Transformer Architectures",
         "authors": json.dumps([{"name": "Mia Anderson"}]),
         "summary": "Using transformer models for protein structure prediction and biochemical analysis in bioinformatics.",
         "categories": json.dumps(["q-bio.BM", "cs.LG"]), "primary_category": "q-bio.BM",
         "published": "2025-01-25T00:00:00Z", "updated": "2025-01-25T00:00:00Z"},
    ]

    for p in papers:
        cur.execute("""
            INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, published, updated, is_downloaded)
            VALUES (%(id)s, %(title)s, %(authors)s, %(summary)s, %(categories)s, %(primary_category)s, %(published)s, %(updated)s, false)
        """, p)

    print(f"[preprocess] Injected {len(papers)} arxiv papers.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_arxiv(cur)
        clear_notion(cur)
        inject_arxiv_papers(cur)
        conn.commit()
        print("[preprocess] DB operations done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Curriculum_Gap_Analysis.xlsx", "Curriculum_Enhancement_Proposal.docx", "curriculum_gap_output.txt"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
