"""
Preprocess for arxiv-research-tracker-notion task.
- Clears and injects 5 target papers + 2 noise papers into
  arxiv.papers, scholarly.arxiv_papers, scholarly.scholar_papers.
- Clears Notion data so the agent starts with a clean slate.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
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

# ── Target papers (efficient transformers theme) ─────────────────────────────

TARGET_PAPERS = [
    {
        "arxiv_id": "2402.10001",
        "title": "FlashAttention-3: Fast and Memory-Efficient Attention with IO-Awareness",
        "authors": [{"name": "Tri Dao"}, {"name": "Daniel Fu"}],
        "categories": ["cs.LG", "cs.AI"],
        "primary_category": "cs.LG",
        "abstract": (
            "We present FlashAttention-3, an algorithm for fast and memory-efficient exact "
            "attention computation that is IO-aware, accounting for reads and writes between "
            "levels of GPU memory. FlashAttention-3 extends prior work on IO-aware attention "
            "by introducing asynchronous block-wise computation and improved memory tiling "
            "strategies that reduce HBM accesses by 3-5x compared to standard attention "
            "implementations. Our approach achieves 2.1x speedup over FlashAttention-2 on "
            "A100 GPUs while maintaining numerical equivalence. We demonstrate that "
            "FlashAttention-3 enables training of transformers with sequence lengths up to "
            "128K tokens with linear memory scaling, making long-context modeling practical "
            "for large-scale language models."
        ),
        "published": "2024-02-15",
        "pub_year": 2024,
        "venue": "NeurIPS",
        "citation_count": 520,
        "markdown_content": (
            "# FlashAttention-3: Fast and Memory-Efficient Attention with IO-Awareness\n\n"
            "## Abstract\n\n"
            "We present FlashAttention-3, an IO-aware algorithm for fast and memory-efficient "
            "exact attention computation on modern GPUs.\n\n"
            "## Introduction\n\n"
            "The self-attention mechanism is a core component of transformer architectures but "
            "suffers from quadratic time and memory complexity. Prior work on FlashAttention "
            "demonstrated that IO-aware algorithms can significantly reduce memory usage. We "
            "extend this line of work with improved tiling and asynchronous computation.\n\n"
            "## Methodology\n\n"
            "FlashAttention-3 introduces asynchronous block-wise computation and improved "
            "memory tiling strategies. By carefully scheduling reads and writes between SRAM "
            "and HBM, we reduce memory accesses by 3-5x. Our tiling strategy adapts to the "
            "specific memory hierarchy of modern GPUs like the A100 and H100.\n\n"
            "## Experiments\n\n"
            "We achieve 2.1x speedup over FlashAttention-2 on A100 GPUs. Training with "
            "sequences up to 128K tokens is feasible with linear memory scaling.\n\n"
            "## Conclusion\n\n"
            "FlashAttention-3 makes long-context transformer training practical through "
            "IO-aware attention computation."
        ),
    },
    {
        "arxiv_id": "2402.10002",
        "title": "Efficient Transformers via Token Merging and Pruning",
        "authors": [{"name": "Daniel Bolya"}, {"name": "Cheng-Yang Fu"}],
        "categories": ["cs.CV", "cs.LG"],
        "primary_category": "cs.CV",
        "abstract": (
            "We propose a unified framework for accelerating vision transformer inference "
            "through combined token merging and pruning strategies. Our method identifies "
            "redundant tokens in intermediate transformer layers using a bipartite matching "
            "algorithm and either merges similar tokens or prunes uninformative ones. This "
            "approach reduces the number of tokens processed by subsequent layers by up to "
            "60% while preserving model accuracy within 0.3% on ImageNet classification. "
            "We show that our method is complementary to existing acceleration techniques "
            "such as knowledge distillation and quantization, and can be applied to any "
            "vision transformer architecture without retraining."
        ),
        "published": "2024-02-18",
        "pub_year": 2024,
        "venue": "ICLR",
        "citation_count": 180,
        "markdown_content": (
            "# Efficient Transformers via Token Merging and Pruning\n\n"
            "## Abstract\n\n"
            "We propose a unified framework for accelerating vision transformer inference "
            "through combined token merging and pruning strategies.\n\n"
            "## Introduction\n\n"
            "Vision transformers process a large number of tokens, many of which are "
            "redundant. Reducing the token count in intermediate layers can significantly "
            "speed up inference without degrading accuracy.\n\n"
            "## Methodology\n\n"
            "Our method uses bipartite matching to identify similar tokens for merging and "
            "uninformative tokens for pruning. The approach is applied at intermediate layers "
            "and can reduce token count by up to 60%.\n\n"
            "## Experiments\n\n"
            "On ImageNet, our approach maintains accuracy within 0.3% while achieving "
            "significant speedups across multiple ViT architectures.\n\n"
            "## Conclusion\n\n"
            "Token merging and pruning provide an efficient, training-free approach to "
            "accelerating vision transformers."
        ),
    },
    {
        "arxiv_id": "2402.10003",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "authors": [{"name": "Edward Hu"}, {"name": "Yelong Shen"}],
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "abstract": (
            "We propose Low-Rank Adaptation (LoRA), a parameter-efficient fine-tuning method "
            "for large language models. LoRA freezes the pre-trained model weights and injects "
            "trainable low-rank decomposition matrices into each layer of the transformer "
            "architecture, drastically reducing the number of trainable parameters for "
            "downstream tasks. For GPT-3 175B, LoRA reduces trainable parameters by 10,000x "
            "and GPU memory requirement by 3x compared to full fine-tuning, while maintaining "
            "or improving model quality on benchmark tasks including RTE, MRPC, and SST-2. "
            "LoRA adds no inference latency and can be efficiently switched between tasks by "
            "swapping the low-rank matrices."
        ),
        "published": "2024-02-20",
        "pub_year": 2024,
        "venue": "ICLR",
        "citation_count": 1200,
        "markdown_content": (
            "# LoRA: Low-Rank Adaptation of Large Language Models\n\n"
            "## Abstract\n\n"
            "We propose LoRA, a parameter-efficient fine-tuning method that injects trainable "
            "low-rank matrices into transformer layers.\n\n"
            "## Introduction\n\n"
            "Full fine-tuning of large language models is prohibitively expensive. LoRA "
            "provides an efficient alternative by training only low-rank decomposition "
            "matrices while freezing the original model weights.\n\n"
            "## Methodology\n\n"
            "LoRA decomposes weight updates into low-rank matrices. For a weight matrix W, "
            "the update is represented as W + BA where B and A are low-rank matrices. This "
            "reduces trainable parameters by 10,000x for GPT-3 175B.\n\n"
            "## Experiments\n\n"
            "LoRA matches or exceeds full fine-tuning performance on RTE, MRPC, and SST-2 "
            "while using 3x less GPU memory.\n\n"
            "## Conclusion\n\n"
            "LoRA enables efficient adaptation of large language models with minimal "
            "parameter overhead and no inference latency."
        ),
    },
    {
        "arxiv_id": "2402.10004",
        "title": "Quantization-Aware Training for Efficient Transformer Inference",
        "authors": [{"name": "Jianlin Su"}, {"name": "Minjia Zhang"}],
        "categories": ["cs.LG", "cs.AI"],
        "primary_category": "cs.LG",
        "abstract": (
            "We introduce a quantization-aware training (QAT) framework specifically designed "
            "for transformer architectures that enables efficient low-precision inference "
            "without significant accuracy degradation. Our approach incorporates learnable "
            "quantization step sizes and applies mixed-precision quantization across different "
            "transformer components, using 4-bit weights for feed-forward layers and 8-bit "
            "activations for attention layers. The framework includes a novel gradient "
            "estimation technique that reduces the straight-through estimator bias common in "
            "quantization training. On language modeling benchmarks, our QAT approach achieves "
            "within 0.5 perplexity of the full-precision baseline while reducing model size "
            "by 4x and inference latency by 2.8x on commodity hardware."
        ),
        "published": "2024-02-22",
        "pub_year": 2024,
        "venue": "ICML",
        "citation_count": 95,
        "markdown_content": (
            "# Quantization-Aware Training for Efficient Transformer Inference\n\n"
            "## Abstract\n\n"
            "We introduce a QAT framework for transformers enabling low-precision inference "
            "with minimal accuracy loss.\n\n"
            "## Introduction\n\n"
            "Deploying large transformer models on edge devices requires reducing model size "
            "and inference cost. Quantization is a key technique but naive post-training "
            "quantization often degrades accuracy significantly.\n\n"
            "## Methodology\n\n"
            "Our framework uses learnable quantization step sizes and mixed-precision "
            "quantization: 4-bit weights for FFN layers and 8-bit activations for attention "
            "layers. A novel gradient estimation technique reduces STE bias.\n\n"
            "## Experiments\n\n"
            "We achieve within 0.5 perplexity of full-precision baselines while reducing "
            "model size by 4x and inference latency by 2.8x.\n\n"
            "## Conclusion\n\n"
            "Our QAT framework enables practical deployment of transformer models on "
            "resource-constrained devices."
        ),
    },
    {
        "arxiv_id": "2402.10005",
        "title": "Sparse Mixture of Experts for Scalable Transformer Models",
        "authors": [{"name": "William Fedus"}, {"name": "Jeff Dean"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "We present a comprehensive study on sparse mixture of experts (MoE) architectures "
            "for scaling transformer models efficiently. Our approach replaces dense feed-forward "
            "layers with sparsely-activated expert layers, where each token is routed to a "
            "subset of specialized expert networks using a learned gating mechanism. This "
            "enables scaling model capacity by 8-64x while keeping computational cost constant "
            "per token. We introduce an improved load-balancing loss and expert capacity factor "
            "that stabilize training and prevent expert collapse. On language modeling tasks, "
            "our sparse MoE transformer achieves the same perplexity as a dense model 4x its "
            "computational cost, demonstrating that conditional computation is a viable path "
            "to efficiently scaling transformers."
        ),
        "published": "2024-02-25",
        "pub_year": 2024,
        "venue": "JMLR",
        "citation_count": 340,
        "markdown_content": (
            "# Sparse Mixture of Experts for Scalable Transformer Models\n\n"
            "## Abstract\n\n"
            "We study sparse MoE architectures for efficiently scaling transformers through "
            "conditional computation.\n\n"
            "## Introduction\n\n"
            "Scaling transformer models typically requires proportional increases in "
            "computation. Sparse mixture of experts offers a way to increase model capacity "
            "without proportional compute increase.\n\n"
            "## Methodology\n\n"
            "We replace dense FFN layers with sparsely-activated expert layers. A learned "
            "gating mechanism routes each token to a subset of experts. We introduce improved "
            "load-balancing loss and expert capacity factors.\n\n"
            "## Experiments\n\n"
            "Our sparse MoE transformer matches a dense model 4x its compute cost on "
            "language modeling tasks. The approach scales model capacity by 8-64x.\n\n"
            "## Conclusion\n\n"
            "Sparse MoE provides an efficient path to scaling transformers through "
            "conditional computation."
        ),
    },
]

# ── Noise papers (should NOT be included in the tracker) ─────────────────────

NOISE_PAPERS = [
    {
        "arxiv_id": "2402.10010",
        "title": "Reinforcement Learning for Autonomous Drone Navigation",
        "authors": [{"name": "Tom Chen"}],
        "categories": ["cs.RO", "cs.AI"],
        "primary_category": "cs.RO",
        "abstract": (
            "We develop a reinforcement learning framework for autonomous drone navigation "
            "in complex indoor environments. Our approach combines deep Q-networks with "
            "spatial reasoning modules to enable real-time obstacle avoidance and path "
            "planning. The system achieves a 94% success rate in navigating previously "
            "unseen environments, outperforming traditional SLAM-based approaches by 15%."
        ),
        "published": "2024-02-28",
        "pub_year": 2024,
        "venue": "IROS",
        "citation_count": 35,
    },
    {
        "arxiv_id": "2402.10011",
        "title": "Graph Neural Networks for Molecular Property Prediction",
        "authors": [{"name": "Lisa Wang"}],
        "categories": ["cs.LG", "q-bio.QM"],
        "primary_category": "cs.LG",
        "abstract": (
            "We propose a novel graph neural network architecture for predicting molecular "
            "properties from 2D and 3D molecular graphs. Our model incorporates edge features "
            "representing bond types and angular information to capture molecular geometry. "
            "On the MoleculeNet benchmark suite, our approach achieves state-of-the-art "
            "results on 8 out of 12 tasks, with particular improvements on solubility and "
            "toxicity prediction datasets."
        ),
        "published": "2024-03-01",
        "pub_year": 2024,
        "venue": "KDD",
        "citation_count": 60,
    },
]


def clear_tables(conn):
    """Clear existing data from all relevant tables."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("[preprocess] Cleared scholarly.arxiv_papers, scholarly.scholar_papers, arxiv.papers")


def clear_notion(conn):
    """Clear all Notion data."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        cur.execute("DELETE FROM notion.users")
    conn.commit()
    print("[preprocess] Cleared Notion data")


def inject_arxiv_papers(conn, papers):
    """Inject papers into arxiv.papers."""
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
                p.get("markdown_content", ""),
                bool(p.get("markdown_content")),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(papers)} papers into arxiv.papers")


def inject_scholarly_arxiv(conn, papers):
    """Inject papers into scholarly.arxiv_papers."""
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
    print(f"[preprocess] Injected {len(papers)} papers into scholarly.arxiv_papers")


def inject_scholarly_scholar(conn, papers):
    """Inject papers into scholarly.scholar_papers."""
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
    print(f"[preprocess] Injected {len(papers)} papers into scholarly.scholar_papers")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_tables(conn)
        clear_notion(conn)

        # Inject all papers (target + noise) into arxiv.papers and scholarly
        all_papers = TARGET_PAPERS + NOISE_PAPERS
        inject_arxiv_papers(conn, all_papers)
        inject_scholarly_arxiv(conn, all_papers)
        inject_scholarly_scholar(conn, all_papers)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
