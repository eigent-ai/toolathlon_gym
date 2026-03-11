"""
Preprocess for arxiv-latex-reasoning-gsheet task.
- Clears gsheet data so the agent starts fresh.
- Clears and injects reasoning papers into arxiv_latex.papers.
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

REASONING_PAPERS = [
    {
        "id": "2201.11903",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "abstract": "We explore how generating a chain of thought — a series of intermediate reasoning steps — significantly improves the ability of large language models to perform complex reasoning. We show that chain-of-thought prompting improves performance on arithmetic, commonsense, and symbolic reasoning benchmarks.",
    },
    {
        "id": "2203.11171",
        "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
        "abstract": "We introduce a new decoding strategy, self-consistency, to replace the naive greedy decoding used in chain-of-thought prompting. We first sample a diverse set of reasoning paths instead of only taking the greedy one, and then select the most consistent answer by marginalizing out the sampled reasoning paths.",
    },
    {
        "id": "2205.11916",
        "title": "Large Language Models are Zero-Shot Reasoners",
        "abstract": "Pretrained large language models are widely used in many sub-fields of natural language processing. We show that simply adding 'Let's think step by step' before each answer significantly enables zero-shot chain-of-thought reasoning in large language models.",
    },
    {
        "id": "2210.03493",
        "title": "Automatic Chain of Thought Prompting in Large Language Models",
        "abstract": "Large language models can perform chain-of-thought reasoning if provided with demonstrations of the reasoning process. We propose Auto-CoT that automatically constructs demonstrations with questions and reasoning chains using clustering and zero-shot CoT generation.",
    },
    {
        "id": "2305.10601",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "abstract": "Language models are increasingly deployed for general problem solving across a wide range of tasks, but are still confined to token-level, left-to-right decision-making. We introduce a new framework for language model inference, Tree of Thoughts, which generalizes over chain-of-thought prompting and enables exploration over coherent units of text.",
    },
]


def clear_gsheet(conn):
    """Clear all Google Sheets data."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
    conn.commit()
    print("[preprocess] Cleared gsheet data")


def inject_arxiv_latex_papers(conn):
    """Clear and inject reasoning papers into arxiv_latex.papers."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM arxiv_latex.papers")
        for p in REASONING_PAPERS:
            cur.execute("""
                INSERT INTO arxiv_latex.papers (id, title, abstract)
                VALUES (%s, %s, %s)
            """, (p["id"], p["title"], p["abstract"]))
    conn.commit()
    print(f"[preprocess] Injected {len(REASONING_PAPERS)} reasoning papers into arxiv_latex.papers")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_gsheet(conn)
        inject_arxiv_latex_papers(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
