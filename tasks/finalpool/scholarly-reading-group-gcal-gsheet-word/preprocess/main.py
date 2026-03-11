"""
Preprocess for scholarly-reading-group-gcal-gsheet-word task.
- Clears and injects transformer papers into scholarly.arxiv_papers and arxiv.papers.
- Clears gcal and gsheet schemas so agent starts fresh.
"""
import os
import argparse
import json
import psycopg2

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

# 3 foundational transformer papers
RELEVANT_PAPERS = [
    {
        "id": "1706.03762",
        "title": "Attention Is All You Need",
        "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}, {"name": "Niki Parmar"}],
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose the Transformer, a model architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. The Transformer achieves superior results on machine translation tasks.",
        "categories": ["cs.CL", "cs.LG"],
        "pdf_url": "https://arxiv.org/pdf/1706.03762",
        "published": "2017-06-12",
    },
    {
        "id": "1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": [{"name": "Jacob Devlin"}, {"name": "Ming-Wei Chang"}],
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional representations from unlabeled text and achieves state-of-the-art results on eleven NLP tasks.",
        "categories": ["cs.CL"],
        "pdf_url": "https://arxiv.org/pdf/1810.04805",
        "published": "2018-10-11",
    },
    {
        "id": "2005.14165",
        "title": "Language Models are Few-Shot Learners",
        "authors": [{"name": "Tom Brown"}, {"name": "Benjamin Mann"}],
        "abstract": "We demonstrate that scaling language models greatly improves task-agnostic, few-shot performance. GPT-3, our 175 billion parameter autoregressive language model, achieves strong performance on many NLP benchmarks with few or no task-specific examples, showing that transformers can be powerful few-shot learners.",
        "categories": ["cs.CL", "cs.AI"],
        "pdf_url": "https://arxiv.org/pdf/2005.14165",
        "published": "2020-05-28",
    },
]

# 1 noise paper - about RLHF, not core transformer architecture
NOISE_PAPERS = [
    {
        "id": "2203.02155",
        "title": "Training language models to follow instructions with human feedback",
        "authors": [{"name": "Long Ouyang"}],
        "abstract": "Making language models bigger does not inherently make them better at following a user's intent. We train language models to follow instructions using reinforcement learning from human feedback, producing models that are more helpful and less harmful.",
        "categories": ["cs.CL"],
        "pdf_url": "https://arxiv.org/pdf/2203.02155",
        "published": "2022-03-04",
    },
]

ALL_PAPERS = RELEVANT_PAPERS + NOISE_PAPERS


def clear_schemas(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("[preprocess] Cleared gsheet, gcal, scholarly, arxiv schemas")


def inject_papers(conn):
    with conn.cursor() as cur:
        for p in ALL_PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers
                    (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p["id"], p["title"], json.dumps(p["authors"]), p["abstract"],
                json.dumps(p["categories"]), p["categories"][0],
                p["pdf_url"], p["published"], True
            ))
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                    (id, title, authors, abstract, categories, primary_category, pdf_url, published)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p["id"], p["title"], json.dumps(p["authors"]), p["abstract"],
                json.dumps(p["categories"]), p["categories"][0],
                p["pdf_url"], p["published"]
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(ALL_PAPERS)} papers ({len(RELEVANT_PAPERS)} relevant, {len(NOISE_PAPERS)} noise)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_schemas(conn)
        inject_papers(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
