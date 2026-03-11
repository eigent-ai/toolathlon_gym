"""
Preprocess for scholarly-arxiv-ppt-gsheet task.
- Clears and injects papers into scholarly.arxiv_papers and arxiv.papers.
- Clears gsheet, email, and pptx-related data so agent starts fresh.
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

# 3 relevant papers about LLM reasoning
RELEVANT_PAPERS = [
    {
        "id": "2301.00234",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": [{"name": "Jason Wei"}, {"name": "Xuezhi Wang"}],
        "abstract": "We explore how chain-of-thought prompting elicits reasoning in large language models. By providing a few chain-of-thought examples as demonstrations, we show that this technique significantly improves performance on arithmetic, commonsense, and symbolic reasoning tasks across a range of large language models.",
        "categories": ["cs.CL"],
        "pdf_url": "https://arxiv.org/pdf/2301.00234",
        "published": "2023-01-15",
    },
    {
        "id": "2302.11382",
        "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
        "authors": [{"name": "Xuezhi Wang"}, {"name": "Jason Wei"}],
        "abstract": "We introduce self-consistency, a novel decoding strategy to replace greedy decoding used in chain-of-thought prompting. We sample a diverse set of reasoning paths and select the most consistent answer by marginalizing out the sampled paths, significantly improving accuracy on reasoning benchmarks.",
        "categories": ["cs.AI", "cs.CL"],
        "pdf_url": "https://arxiv.org/pdf/2302.11382",
        "published": "2023-02-22",
    },
    {
        "id": "2305.10601",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "authors": [{"name": "Shunyu Yao"}, {"name": "Dian Yu"}],
        "abstract": "Language models are increasingly being used as problem solvers. We introduce Tree of Thoughts, a framework that generalizes chain-of-thought prompting and enables exploration over coherent units of text called thoughts, allowing language models to perform deliberate decision making by considering multiple reasoning paths.",
        "categories": ["cs.AI"],
        "pdf_url": "https://arxiv.org/pdf/2305.10601",
        "published": "2023-05-17",
    },
]

# 3 noise papers about unrelated topics
NOISE_PAPERS = [
    {
        "id": "2301.11093",
        "title": "Segment Anything in Medical Images",
        "authors": [{"name": "Jun Ma"}],
        "abstract": "Medical image segmentation is a challenging task that requires identifying and delineating structures within medical images. We present a universal model for medical image segmentation using segment anything approaches.",
        "categories": ["cs.CV"],
        "pdf_url": "https://arxiv.org/pdf/2301.11093",
        "published": "2023-01-26",
    },
    {
        "id": "2302.05543",
        "title": "Scaling Laws for Neural Machine Translation",
        "authors": [{"name": "Brian Thompson"}],
        "abstract": "We study how neural machine translation performance scales with model size and data size. Our findings suggest predictable scaling relationships that can guide model development and resource allocation decisions.",
        "categories": ["cs.CL"],
        "pdf_url": "https://arxiv.org/pdf/2302.05543",
        "published": "2023-02-11",
    },
    {
        "id": "2304.09842",
        "title": "Image Captioning with Diffusion Models",
        "authors": [{"name": "Sarah Chen"}],
        "abstract": "We propose a new approach to image captioning using diffusion models. Our method generates descriptive captions by iteratively refining text outputs conditioned on image features extracted from a vision encoder.",
        "categories": ["cs.CV"],
        "pdf_url": "https://arxiv.org/pdf/2304.09842",
        "published": "2023-04-19",
    },
]

ALL_PAPERS = RELEVANT_PAPERS + NOISE_PAPERS


def clear_schemas(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("[preprocess] Cleared gsheet, email, scholarly, arxiv schemas")


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
