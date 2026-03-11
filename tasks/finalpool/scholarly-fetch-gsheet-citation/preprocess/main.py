"""
Preprocess for scholarly-fetch-gsheet-citation task.

Clears gsheet and scholarly schemas, then injects known paper data
into scholarly.scholar_papers so the task is deterministic.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""

import os
import argparse
import json
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PAPERS = [
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": [{"name": "Jacob Devlin"}, {"name": "Ming-Wei Chang"}, {"name": "Kenton Lee"}, {"name": "Kristina Toutanova"}],
        "citation_count": 2800,
        "pub_year": 2019,
        "venue": "NAACL",
        "abstract": "We introduce a new language representation model called BERT.",
    },
    {
        "title": "GPT-4 Technical Report",
        "authors": [{"name": "OpenAI Team"}, {"name": "Josh Achiam"}, {"name": "Steven Adler"}],
        "citation_count": 1500,
        "pub_year": 2023,
        "venue": "arXiv",
        "abstract": "We report the development of GPT-4, a large-scale multimodal model.",
    },
    {
        "title": "Attention Is All You Need",
        "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}, {"name": "Niki Parmar"}, {"name": "Jakob Uszkoreit"}],
        "citation_count": 5200,
        "pub_year": 2017,
        "venue": "NeurIPS",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
    },
    {
        "title": "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
        "authors": [{"name": "Yinhan Liu"}, {"name": "Myle Ott"}, {"name": "Naman Goyal"}, {"name": "Jingfei Du"}],
        "citation_count": 1100,
        "pub_year": 2019,
        "venue": "arXiv",
        "abstract": "Language model pretraining has led to significant performance gains.",
    },
    {
        "title": "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer",
        "authors": [{"name": "Colin Raffel"}, {"name": "Noam Shazeer"}, {"name": "Adam Roberts"}, {"name": "Katherine Lee"}],
        "citation_count": 900,
        "pub_year": 2020,
        "venue": "JMLR",
        "abstract": "Transfer learning, where a model is first pre-trained on a data-rich task.",
    },
    {
        "title": "Training language models to follow instructions with human feedback",
        "authors": [{"name": "Long Ouyang"}, {"name": "Jeff Wu"}, {"name": "Xu Jiang"}, {"name": "Josh Achiam"}],
        "citation_count": 650,
        "pub_year": 2022,
        "venue": "NeurIPS",
        "abstract": "Making language models bigger does not inherently make them better at following instructions.",
    },
    {
        "title": "Deep Learning for 3D Point Clouds: A Survey",
        "authors": [{"name": "Yulan Guo"}, {"name": "Hanyun Wang"}],
        "citation_count": 80,
        "pub_year": 2020,
        "venue": "TPAMI",
        "abstract": "Point cloud learning has been attracting attention due to its wide applications.",
    },
    {
        "title": "Structure and Function of the Global Soil Microbiome",
        "authors": [{"name": "Manuel Delgado-Baquerizo"}, {"name": "Angela Oliverio"}],
        "citation_count": 45,
        "pub_year": 2018,
        "venue": "Nature",
        "abstract": "Soil microorganisms are critical for maintaining ecosystem function.",
    },
]


def clear_schemas(conn):
    """Clear gsheet and scholarly tables."""
    with conn.cursor() as cur:
        # Clear gsheet
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.permissions")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        # Clear scholarly
        cur.execute("DELETE FROM scholarly.scholar_papers")
    conn.commit()
    print("[preprocess] Cleared gsheet and scholarly tables.")


def inject_scholarly_data(conn):
    """Insert known papers into scholarly.scholar_papers."""
    with conn.cursor() as cur:
        for p in PAPERS:
            cur.execute(
                """INSERT INTO scholarly.scholar_papers
                   (title, authors, citation_count, pub_year, venue, abstract)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    p["title"],
                    json.dumps(p["authors"]),
                    p["citation_count"],
                    p["pub_year"],
                    p["venue"],
                    p["abstract"],
                ),
            )
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into scholarly.scholar_papers.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_schemas(conn)
        inject_scholarly_data(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
