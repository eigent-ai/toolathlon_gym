"""
Preprocess script for fetch-arxiv-conference-schedule-gcal-notion task.

This script:
1. Clears arxiv, scholarly, notion, gcal schemas
2. Injects papers into arxiv and scholarly schemas
3. Injects noise data
4. Extracts mock_pages.tar.gz and starts HTTP server on port 30207
"""

import argparse
import asyncio
import json
import os
import shutil
import tarfile
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_schemas(cur):
    """Clear writable schemas."""
    print("[preprocess] Clearing schemas...")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM notion.users")
    cur.execute("DELETE FROM gcal.events")
    cur.execute("DELETE FROM arxiv.papers")
    cur.execute("DELETE FROM scholarly.arxiv_papers")
    cur.execute("DELETE FROM scholarly.scholar_papers")
    print("[preprocess] Schemas cleared.")


def inject_arxiv_papers(cur):
    """Inject relevant arxiv papers."""
    print("[preprocess] Injecting arxiv papers...")
    papers = [
        {
            "id": "2601.00001",
            "title": "Sparse Attention Transformers for Efficient Long-Range Sequence Modeling",
            "authors": json.dumps(["Alice Chen", "Bob Li", "Carlos Ruiz"]),
            "summary": "We propose a sparse attention mechanism that reduces the computational complexity of transformers from quadratic to near-linear, enabling efficient processing of long sequences up to 16K tokens. Our approach uses a learned routing strategy to identify the most relevant attention heads for each input position.",
            "categories": json.dumps(["cs.CL", "cs.LG"]),
            "primary_category": "cs.CL",
            "published": "2026-01-15T00:00:00Z",
        },
        {
            "id": "2601.00002",
            "title": "Multi-Scale Hierarchical Transformers for Document Understanding",
            "authors": json.dumps(["David Kim", "Elena Volkov"]),
            "summary": "This paper presents a hierarchical transformer architecture that processes documents at multiple scales simultaneously. We introduce cross-scale attention layers that allow information flow between word-level, sentence-level, and paragraph-level representations.",
            "categories": json.dumps(["cs.CL", "cs.AI"]),
            "primary_category": "cs.CL",
            "published": "2026-01-20T00:00:00Z",
        },
        {
            "id": "2602.00003",
            "title": "Adaptive Learning Rate Methods for Training Deep Neural Networks",
            "authors": json.dumps(["Frank Wu", "Grace Patel"]),
            "summary": "We introduce AdaptiveScheduler, a novel learning rate scheduling algorithm that dynamically adjusts the learning rate based on gradient statistics and loss landscape curvature. Experiments on ImageNet and GLUE benchmarks show consistent improvements over existing methods.",
            "categories": json.dumps(["cs.LG", "cs.AI"]),
            "primary_category": "cs.LG",
            "published": "2026-02-05T00:00:00Z",
        },
        {
            "id": "2602.00004",
            "title": "Memory-Enhanced Attention Networks for Few-Shot Classification",
            "authors": json.dumps(["Hiroshi Tanaka", "Isabel Santos"]),
            "summary": "We propose a memory-augmented attention mechanism that maintains an external memory bank of prototypical representations. The attention module learns to retrieve and integrate relevant memories during forward passes, achieving state-of-the-art results on Mini-ImageNet and tiered-ImageNet benchmarks.",
            "categories": json.dumps(["cs.CV", "cs.LG"]),
            "primary_category": "cs.CV",
            "published": "2026-02-10T00:00:00Z",
        },
        {
            "id": "2603.00005",
            "title": "Gradient-Free Optimization Techniques for Large Language Model Fine-Tuning",
            "authors": json.dumps(["Jack Morris", "Karen Zhang"]),
            "summary": "This work explores gradient-free optimization methods including evolution strategies and Bayesian optimization for fine-tuning large language models. We show that these methods can achieve comparable performance to gradient-based approaches while requiring significantly less memory.",
            "categories": json.dumps(["cs.LG", "cs.CL"]),
            "primary_category": "cs.LG",
            "published": "2026-03-01T00:00:00Z",
        },
    ]

    for p in papers:
        cur.execute(
            "INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, published) "
            "VALUES (%(id)s, %(title)s, %(authors)s, %(summary)s, %(categories)s, %(primary_category)s, %(published)s)",
            p,
        )

    # Noise papers (unrelated topics)
    noise_papers = [
        {
            "id": "2601.99001",
            "title": "Molecular Dynamics Simulations of Protein Folding Under Extreme Pressure",
            "authors": json.dumps(["Zara Ahmed", "Paul Chen"]),
            "summary": "This study investigates the folding dynamics of globular proteins under high hydrostatic pressure using all-atom molecular dynamics simulations.",
            "categories": json.dumps(["q-bio.BM"]),
            "primary_category": "q-bio.BM",
            "published": "2026-01-12T00:00:00Z",
        },
        {
            "id": "2602.99002",
            "title": "Topological Invariants of Four-Dimensional Manifolds",
            "authors": json.dumps(["Robert Green"]),
            "summary": "We compute new topological invariants for a class of smooth four-dimensional manifolds using gauge-theoretic methods.",
            "categories": json.dumps(["math.GT"]),
            "primary_category": "math.GT",
            "published": "2026-02-01T00:00:00Z",
        },
    ]
    for p in noise_papers:
        cur.execute(
            "INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, published) "
            "VALUES (%(id)s, %(title)s, %(authors)s, %(summary)s, %(categories)s, %(primary_category)s, %(published)s)",
            p,
        )
    print("[preprocess] Arxiv papers injected.")


def inject_scholarly_papers(cur):
    """Inject scholarly papers."""
    print("[preprocess] Injecting scholarly papers...")

    # arxiv_papers in scholarly schema
    scholarly_arxiv = [
        {
            "id": "2603.00010",
            "title": "Self-Attention Distillation for Compact Transformer Models",
            "authors": json.dumps(["Lina Petrov", "Max Jensen"]),
            "abstract": "We present a knowledge distillation framework specifically designed for transformer attention layers. Our method transfers attention patterns from large teacher models to compact student models, achieving 90% of teacher performance with 4x fewer parameters.",
            "categories": json.dumps(["cs.LG", "cs.CL"]),
            "primary_category": "cs.LG",
            "published": "2026-03-02T00:00:00Z",
        },
    ]
    for p in scholarly_arxiv:
        cur.execute(
            "INSERT INTO scholarly.arxiv_papers (id, title, authors, abstract, categories, primary_category, published) "
            "VALUES (%(id)s, %(title)s, %(authors)s, %(abstract)s, %(categories)s, %(primary_category)s, %(published)s)",
            p,
        )

    # scholar_papers
    scholar_papers = [
        {
            "title": "A Survey on Attention Mechanisms in Deep Learning",
            "authors": json.dumps(["Wei Lin", "Sarah Johnson", "Tao Wang"]),
            "abstract": "This comprehensive survey reviews attention mechanisms in deep learning, covering self-attention, cross-attention, multi-head attention, and their applications across NLP, computer vision, and speech processing. We categorize 150+ papers and identify future research directions.",
            "pub_year": 2025,
            "venue": "ACM Computing Surveys",
            "citation_count": 245,
        },
        {
            "title": "Mixed Precision Training of Deep Neural Networks: Methods and Best Practices",
            "authors": json.dumps(["Yuki Sato", "Andreas Muller"]),
            "abstract": "This paper provides a systematic study of mixed precision training techniques for deep neural networks. We analyze loss scaling strategies, gradient accumulation methods, and numerically stable implementations across various model architectures.",
            "pub_year": 2025,
            "venue": "NeurIPS 2025",
            "citation_count": 89,
        },
        {
            "title": "Vision-Language Pretraining with Cross-Modal Transformers",
            "authors": json.dumps(["Jennifer Lee", "Raj Patel", "Chris Anderson"]),
            "abstract": "We introduce a cross-modal transformer pretraining framework that jointly learns visual and textual representations. Our approach uses cross-attention layers to align multimodal features, achieving state-of-the-art results on VQA, image captioning, and visual reasoning tasks.",
            "pub_year": 2025,
            "venue": "CVPR 2025",
            "citation_count": 156,
        },
    ]

    # Noise scholar papers
    noise_scholar = [
        {
            "title": "Climate Change Impact on Coastal Erosion Patterns",
            "authors": json.dumps(["Maria Costa"]),
            "abstract": "Analysis of coastal erosion rates over 50 years across Mediterranean coastlines.",
            "pub_year": 2024,
            "venue": "Nature Geoscience",
            "citation_count": 67,
        },
    ]

    for p in scholar_papers + noise_scholar:
        cur.execute(
            "INSERT INTO scholarly.scholar_papers (title, authors, abstract, pub_year, venue, citation_count) "
            "VALUES (%(title)s, %(authors)s, %(abstract)s, %(pub_year)s, %(venue)s, %(citation_count)s)",
            p,
        )
    print("[preprocess] Scholarly papers injected.")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30207."""
    print("[preprocess] Setting up mock conference API server...")

    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)

    mock_dir = os.path.join(tmp_dir, "mock_pages")
    port = 30207

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{port}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {port} --directory {mock_dir} "
        f"> {mock_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock API server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_schemas(cur)
        inject_arxiv_papers(cur)
        inject_scholarly_papers(cur)
        conn.commit()
        print("[preprocess] Database operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Database error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
