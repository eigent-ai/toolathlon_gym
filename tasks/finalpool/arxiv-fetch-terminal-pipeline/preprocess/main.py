"""
Preprocess for arxiv-fetch-terminal-pipeline task.

Clears and injects papers about code generation into scholarly and arxiv tables.
Starts mock HTTP server on port 30151 for supplementary data fetch.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
import asyncio
import json
import os
import shutil
import tarfile

import psycopg2

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

TARGET_PAPERS = [
    {
        "arxiv_id": "2107.03374",
        "title": "Evaluating Large Language Models Trained on Code",
        "authors": [{"name": "Mark Chen"}, {"name": "Jerry Tworek"}, {"name": "Heewoo Jun"}],
        "categories": ["cs.LG", "cs.PL"],
        "primary_category": "cs.LG",
        "abstract": (
            "We introduce Codex, a GPT language model fine-tuned on publicly available code from "
            "GitHub, and study its Python code-writing capabilities. A distinct production version "
            "of Codex powers GitHub Copilot. On HumanEval, a new evaluation set we release to "
            "measure functional correctness for synthesizing programs from docstrings, our model "
            "solves 28.8% of the problems, while GPT-3 solves 0% and GPT-J solves 11.4%. "
            "Furthermore, we find that repeated sampling from the model is a surprisingly effective "
            "strategy for producing working solutions to difficult prompts."
        ),
        "published": "2021-07-07",
        "pub_year": 2021,
        "venue": "arXiv",
        "citation_count": 3500,
    },
    {
        "arxiv_id": "2002.08155",
        "title": "CodeBERT: A Pre-Trained Model for Programming and Natural Languages",
        "authors": [{"name": "Zhangyin Feng"}, {"name": "Daya Guo"}, {"name": "Duyu Tang"}],
        "categories": ["cs.CL", "cs.PL"],
        "primary_category": "cs.CL",
        "abstract": (
            "We present CodeBERT, a bimodal pre-trained model for programming language and natural "
            "language. CodeBERT learns general-purpose representations that support downstream NL-PL "
            "applications such as natural language code search, code documentation generation, and "
            "other tasks. We develop CodeBERT with Transformer-based neural architecture, and train "
            "it with a hybrid objective function that incorporates the pre-training task of replaced "
            "token detection, which is to detect plausible alternatives sampled from generators."
        ),
        "published": "2020-02-19",
        "pub_year": 2020,
        "venue": "EMNLP Findings",
        "citation_count": 2200,
    },
    {
        "arxiv_id": "2203.07814",
        "title": "Competition-Level Code Generation with AlphaCode",
        "authors": [{"name": "Yujia Li"}, {"name": "David Choi"}, {"name": "Junyoung Chung"}],
        "categories": ["cs.PL", "cs.AI"],
        "primary_category": "cs.PL",
        "abstract": (
            "Programming is a powerful and ubiquitous problem-solving tool. Developing systems that "
            "can assist programmers or even generate programs independently could make programming "
            "more productive and accessible. We introduce AlphaCode, a system for code generation "
            "that can create novel solutions to competitive programming problems that require deeper "
            "reasoning. In simulated evaluations on recent programming competitions on the Codeforces "
            "platform, AlphaCode achieved on average a ranking within the top 54.3% of participants."
        ),
        "published": "2022-03-08",
        "pub_year": 2022,
        "venue": "Science",
        "citation_count": 1800,
    },
    {
        "arxiv_id": "2305.06161",
        "title": "StarCoder: May the Source Be with You!",
        "authors": [{"name": "Raymond Li"}, {"name": "Loubna Ben Allal"}, {"name": "Yangtian Zi"}],
        "categories": ["cs.CL", "cs.PL"],
        "primary_category": "cs.CL",
        "abstract": (
            "The BigCode community, an open-scientific collaboration working on the responsible "
            "development of large language models for code, introduces StarCoder and StarCoderBase. "
            "StarCoderBase is a 15.5B parameter model trained on 1 trillion tokens sourced from The "
            "Stack, a large collection of permissively licensed GitHub repositories. StarCoder is a "
            "fine-tuned version of StarCoderBase on 35B Python tokens. We evaluate StarCoder on a "
            "comprehensive set of code generation benchmarks and find that it outperforms every open "
            "code LLM that supports multiple programming languages."
        ),
        "published": "2023-05-09",
        "pub_year": 2023,
        "venue": "TMLR",
        "citation_count": 1500,
    },
]

NOISE_PAPERS = [
    {
        "arxiv_id": "1906.10611",
        "title": "A Survey of Machine Learning for Big Code and Naturalness",
        "authors": [{"name": "Miltiadis Allamanis"}, {"name": "Earl T. Barr"}],
        "categories": ["cs.SE", "cs.LG"],
        "primary_category": "cs.SE",
        "abstract": (
            "Research at the intersection of machine learning and software engineering has recently "
            "seen a surge in interest. This survey is a comprehensive review of the state of the art "
            "in this area, covering probabilistic models of code, neural models for code analysis, "
            "code completion, bug detection, and program repair. We discuss the naturalness hypothesis "
            "which posits that software is a form of human communication and has statistical properties "
            "similar to natural language corpora."
        ),
        "published": "2019-06-25",
        "pub_year": 2019,
        "venue": "ACM Computing Surveys",
        "citation_count": 900,
    },
]

MOCK_PORT = 30151


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("Cleared scholarly, arxiv tables")


def inject_arxiv_papers(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO arxiv.papers
                (id, title, authors, summary, categories, primary_category,
                 published, updated, doi, journal_ref, comment, pdf_url,
                 links, markdown_content, is_downloaded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary,
                    categories = EXCLUDED.categories,
                    primary_category = EXCLUDED.primary_category,
                    published = EXCLUDED.published,
                    markdown_content = EXCLUDED.markdown_content,
                    is_downloaded = EXCLUDED.is_downloaded
            """, (
                p["arxiv_id"],
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                json.dumps(p["categories"]),
                p["primary_category"],
                p["published"],
                p["published"],
                None,
                p.get("venue"),
                None,
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                json.dumps([]),
                "",
                False,
            ))
    conn.commit()
    print(f"Injected {len(papers)} papers into arxiv.papers")


def inject_scholarly_arxiv(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                (id, title, authors, abstract, categories, primary_category,
                 published, updated, doi, journal_ref, pdf_url, html_url, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    abstract = EXCLUDED.abstract,
                    categories = EXCLUDED.categories,
                    primary_category = EXCLUDED.primary_category,
                    published = EXCLUDED.published
            """, (
                p["arxiv_id"],
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                json.dumps(p["categories"]),
                p["primary_category"],
                p["published"],
                p["published"],
                None,
                p.get("venue"),
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                None,
            ))
    conn.commit()
    print(f"Injected {len(papers)} papers into scholarly.arxiv_papers")


def inject_scholarly_scholar(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.scholar_papers
                (title, authors, abstract, pub_year, venue, citation_count,
                 url, eprint_url, pub_url, bib)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                p["pub_year"],
                p.get("venue"),
                p.get("citation_count", 0),
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                json.dumps({"title": p["title"], "year": p["pub_year"]}),
            ))
    conn.commit()
    print(f"Injected {len(papers)} papers into scholarly.scholar_papers")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30151."""
    print("[preprocess] Setting up mock server...")

    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)
    print(f"[preprocess] Extracted {tar_path} to {tmp_dir}")

    mock_dir = os.path.join(tmp_dir, "mock_pages")

    # Kill any existing process on the port
    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{MOCK_PORT}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    # Start HTTP server
    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {MOCK_PORT} --directory {mock_dir} "
        f"> {mock_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server running at http://localhost:{MOCK_PORT}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_tables(conn)
        all_papers = TARGET_PAPERS + NOISE_PAPERS
        inject_arxiv_papers(conn, all_papers)
        inject_scholarly_arxiv(conn, all_papers)
        inject_scholarly_scholar(conn, all_papers)
    finally:
        conn.close()

    await setup_mock_server()
    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
