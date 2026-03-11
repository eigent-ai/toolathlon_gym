"""
Preprocess for arxiv-research-landscape-report task.
- Clears and injects 5 target + 3 noise papers into arxiv.papers, scholarly.arxiv_papers, scholarly.scholar_papers.
- Starts mock HTTP server on port 30228 for conference schedule.
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
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

MOCK_PORT = 30228

TARGET_PAPERS = [
    {
        "arxiv_id": "2401.00001",
        "title": "Efficient Transformers for NLP",
        "authors": [{"name": "Alice Zhang"}, {"name": "Bob Li"}],
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "abstract": (
            "We present a novel architecture for efficient transformer models in natural language "
            "processing tasks. Our approach introduces sparse attention patterns and dynamic token "
            "selection that reduces computational cost by 40% while maintaining accuracy on standard "
            "NLP benchmarks including GLUE, SuperGLUE, and SQuAD. The method is applicable to both "
            "encoder and decoder architectures and demonstrates strong performance on text "
            "classification, question answering, and machine translation tasks."
        ),
        "published": "2024-01-05",
        "pub_year": 2024,
        "venue": "ACL",
        "citation_count": 350,
        "markdown_content": (
            "# Efficient Transformers for NLP\n\n"
            "## Abstract\nWe present efficient transformer models for NLP with sparse attention.\n\n"
            "## Methodology\nOur approach uses dynamic token selection to reduce computation.\n\n"
            "## Results\n40% computational reduction on GLUE and SuperGLUE benchmarks."
        ),
    },
    {
        "arxiv_id": "2401.00002",
        "title": "Deep RL with Human Feedback",
        "authors": [{"name": "Carlos Rivera"}, {"name": "Diana Wu"}],
        "categories": ["cs.LG", "cs.AI"],
        "primary_category": "cs.LG",
        "abstract": (
            "We introduce a deep reinforcement learning framework that incorporates human feedback "
            "for training language models. Our approach combines proximal policy optimization with "
            "a learned reward model trained on human preference data. We demonstrate that this "
            "method significantly improves the alignment of language model outputs with human values "
            "and intentions, reducing harmful outputs by 65% while maintaining task performance. "
            "The framework supports both online and offline feedback collection."
        ),
        "published": "2024-01-10",
        "pub_year": 2024,
        "venue": "NeurIPS",
        "citation_count": 520,
        "markdown_content": (
            "# Deep RL with Human Feedback\n\n"
            "## Abstract\nA deep RL framework using human feedback for language model alignment.\n\n"
            "## Methodology\nCombines PPO with learned reward models from preference data.\n\n"
            "## Results\n65% reduction in harmful outputs."
        ),
    },
    {
        "arxiv_id": "2401.00003",
        "title": "Generative Models for Code",
        "authors": [{"name": "Emily Chen"}, {"name": "Frank Park"}],
        "categories": ["cs.SE", "cs.LG"],
        "primary_category": "cs.SE",
        "abstract": (
            "We present a large-scale generative model specifically designed for code synthesis and "
            "completion. Our model is trained on a curated dataset of 500 billion tokens from "
            "open-source repositories spanning 20 programming languages. We introduce a novel "
            "code-aware tokenization scheme and a hierarchical generation strategy that produces "
            "syntactically valid code with 92% accuracy. On the HumanEval benchmark, our model "
            "achieves a pass@1 rate of 67%, outperforming existing open-source alternatives."
        ),
        "published": "2024-01-15",
        "pub_year": 2024,
        "venue": "ICML",
        "citation_count": 280,
        "markdown_content": (
            "# Generative Models for Code\n\n"
            "## Abstract\nA generative model for code synthesis trained on 500B tokens.\n\n"
            "## Methodology\nCode-aware tokenization with hierarchical generation.\n\n"
            "## Results\n67% pass@1 on HumanEval, 92% syntactic validity."
        ),
    },
    {
        "arxiv_id": "2401.00004",
        "title": "Knowledge Graph Embeddings",
        "authors": [{"name": "Grace Kim"}, {"name": "Henry Zhao"}],
        "categories": ["cs.AI", "cs.CL"],
        "primary_category": "cs.AI",
        "abstract": (
            "We propose a new approach to learning knowledge graph embeddings that captures both "
            "structural and semantic relationships between entities. Our method combines graph "
            "neural networks with pre-trained language model representations to create enriched "
            "entity embeddings. On standard knowledge graph completion benchmarks including "
            "FB15k-237 and WN18RR, our approach achieves state-of-the-art results with 8% "
            "improvement in Hits@10 over the previous best method. The embeddings also show "
            "strong transfer learning capability for downstream planning and reasoning tasks."
        ),
        "published": "2024-01-20",
        "pub_year": 2024,
        "venue": "AAAI",
        "citation_count": 190,
        "markdown_content": (
            "# Knowledge Graph Embeddings\n\n"
            "## Abstract\nKnowledge graph embeddings combining GNNs and language models.\n\n"
            "## Methodology\nGraph neural networks with pre-trained LM representations.\n\n"
            "## Results\n8% improvement in Hits@10 on FB15k-237 and WN18RR."
        ),
    },
    {
        "arxiv_id": "2401.00005",
        "title": "Optimization in Deep Learning",
        "authors": [{"name": "Ian Roberts"}, {"name": "Julia Martinez"}],
        "categories": ["cs.LG", "math.OC"],
        "primary_category": "cs.LG",
        "abstract": (
            "We present a comprehensive study of optimization methods for training deep neural "
            "networks, introducing a new adaptive learning rate algorithm that combines the "
            "benefits of Adam and natural gradient methods. Our optimizer, called AdaNatGrad, "
            "uses a lightweight approximation of the Fisher information matrix to precondition "
            "gradient updates. On image classification, language modeling, and reinforcement "
            "learning benchmarks, AdaNatGrad converges 30% faster than Adam while achieving "
            "comparable or better final performance."
        ),
        "published": "2024-01-25",
        "pub_year": 2024,
        "venue": "ICLR",
        "citation_count": 150,
        "markdown_content": (
            "# Optimization in Deep Learning\n\n"
            "## Abstract\nA new adaptive optimizer combining Adam and natural gradient.\n\n"
            "## Methodology\nLightweight Fisher information approximation for preconditioning.\n\n"
            "## Results\n30% faster convergence than Adam."
        ),
    },
]

NOISE_PAPERS = [
    {
        "arxiv_id": "2401.00006",
        "title": "Quantum Computing Survey",
        "authors": [{"name": "Kate Nelson"}],
        "categories": ["quant-ph", "cs.ET"],
        "primary_category": "quant-ph",
        "abstract": (
            "A comprehensive survey of quantum computing algorithms and their applications in "
            "cryptography, optimization, and simulation. We review recent advances in quantum "
            "error correction, quantum supremacy experiments, and near-term quantum algorithms."
        ),
        "published": "2024-02-01",
        "pub_year": 2024,
        "venue": "Physical Review Letters",
        "citation_count": 40,
    },
    {
        "arxiv_id": "2401.00007",
        "title": "Blockchain Consensus",
        "authors": [{"name": "Leo Brown"}],
        "categories": ["cs.DC", "cs.CR"],
        "primary_category": "cs.DC",
        "abstract": (
            "We analyze consensus mechanisms in blockchain systems, comparing proof-of-work, "
            "proof-of-stake, and delegated proof-of-stake approaches. We propose a new hybrid "
            "consensus protocol that achieves higher throughput while maintaining decentralization."
        ),
        "published": "2024-02-05",
        "pub_year": 2024,
        "venue": "IEEE S&P",
        "citation_count": 25,
    },
    {
        "arxiv_id": "2401.00008",
        "title": "Robotics Navigation",
        "authors": [{"name": "Mary Johnson"}],
        "categories": ["cs.RO"],
        "primary_category": "cs.RO",
        "abstract": (
            "A novel approach to autonomous robot navigation using vision-based SLAM and learned "
            "motion primitives. Our system operates in real-time on embedded hardware and achieves "
            "robust navigation in cluttered indoor environments."
        ),
        "published": "2024-02-10",
        "pub_year": 2024,
        "venue": "IROS",
        "citation_count": 15,
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("[preprocess] Cleared scholarly.arxiv_papers, scholarly.scholar_papers, arxiv.papers")


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
                    title = EXCLUDED.title, authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary, categories = EXCLUDED.categories,
                    primary_category = EXCLUDED.primary_category,
                    published = EXCLUDED.published,
                    markdown_content = EXCLUDED.markdown_content,
                    is_downloaded = EXCLUDED.is_downloaded
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]),
                p["primary_category"], p["published"], p["published"],
                None, p.get("venue"), None,
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                json.dumps([]), p.get("markdown_content", ""),
                bool(p.get("markdown_content")),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(papers)} papers into arxiv.papers")


def inject_scholarly_arxiv(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                (id, title, authors, abstract, categories, primary_category,
                 published, updated, doi, journal_ref, pdf_url, html_url, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title, authors = EXCLUDED.authors,
                    abstract = EXCLUDED.abstract, categories = EXCLUDED.categories,
                    primary_category = EXCLUDED.primary_category,
                    published = EXCLUDED.published
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]),
                p["primary_category"], p["published"], p["published"],
                None, p.get("venue"),
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}", None,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(papers)} papers into scholarly.arxiv_papers")


def inject_scholarly_scholar(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.scholar_papers
                (title, authors, abstract, pub_year, venue, citation_count,
                 url, eprint_url, pub_url, bib)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p["title"], json.dumps(p["authors"]),
                p["abstract"], p["pub_year"], p.get("venue"),
                p.get("citation_count", 0),
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                json.dumps({"title": p["title"], "year": p["pub_year"]}),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(papers)} papers into scholarly.scholar_papers")


async def setup_mock_server():
    """Extract mock_pages and start HTTP server on port 30228."""
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    # Create tar.gz if it doesn't exist
    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    mock_src = os.path.join(files_dir, "mock_pages")
    if not os.path.exists(tar_path) and os.path.exists(mock_src):
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(mock_src, arcname="mock_pages")

    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)
        serve_dir = os.path.join(tmp_dir, "mock_pages")
    else:
        # Fallback: copy directly
        serve_dir = tmp_dir
        mock_src = os.path.join(files_dir, "mock_pages")
        if os.path.exists(mock_src):
            shutil.copytree(mock_src, os.path.join(tmp_dir, "mock_pages"))
            serve_dir = os.path.join(tmp_dir, "mock_pages")

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{MOCK_PORT}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {MOCK_PORT} --directory {serve_dir} "
        f"> {serve_dir}/server.log 2>&1 &"
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
    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
