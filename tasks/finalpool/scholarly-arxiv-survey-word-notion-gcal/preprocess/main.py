"""
Preprocess for scholarly-arxiv-survey-word-notion-gcal task.

Injects 8 papers (5 relevant LLM reasoning + 3 noise) into:
  - scholarly.arxiv_papers
  - arxiv.papers
  - arxiv_latex.papers

Also injects noise Notion pages, noise GCal events, and clears email tables.

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

# ── Relevant LLM Reasoning Papers ──────────────────────────────────────────

RELEVANT_PAPERS = [
    {
        "arxiv_id": "2201.11903",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": [{"name": "Jason Wei"}, {"name": "Xuezhi Wang"}, {"name": "Dale Schuurmans"}],
        "abstract": (
            "We explore how generating a chain of thought -- a series of intermediate reasoning "
            "steps -- significantly improves the ability of large language models to perform complex "
            "reasoning. We show that chain-of-thought prompting improves performance on arithmetic, "
            "commonsense, and symbolic reasoning benchmarks when applied to sufficiently large models."
        ),
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "published": "2022-01-28",
        "citation_count": 4200,
        "method": "Chain-of-Thought",
        "markdown_content": (
            "# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models\n\n"
            "## Abstract\n\n"
            "We explore how generating a chain of thought -- a series of intermediate reasoning "
            "steps -- significantly improves the ability of large language models to perform complex "
            "reasoning.\n\n"
            "## Introduction\n\n"
            "Scaling up language models has been shown to improve performance on many NLP tasks. "
            "However, scaling alone has not proven sufficient for achieving strong performance on "
            "challenging tasks that require multi-step reasoning, such as math word problems and "
            "commonsense reasoning. We propose chain-of-thought prompting, where a few chain of "
            "thought demonstrations are provided as exemplars in prompting.\n\n"
            "## Method\n\n"
            "Chain-of-thought prompting augments each exemplar in few-shot prompting with a chain "
            "of thought -- a coherent series of intermediate reasoning steps leading to the final "
            "answer. This allows the model to decompose complex problems into intermediate steps "
            "that are each individually simpler. The key insight is that by providing a few examples "
            "of step-by-step reasoning, the model learns to generate similar reasoning traces.\n\n"
            "## Experiments\n\n"
            "We evaluate chain-of-thought prompting on arithmetic reasoning (GSM8K, SVAMP, ASDiv, "
            "AQuA, MAWPS), commonsense reasoning (CSQA, StrategyQA), and symbolic reasoning tasks. "
            "On GSM8K, chain-of-thought prompting with PaLM 540B achieves 56.9% accuracy compared "
            "to standard prompting at 17.9%. The method is an emergent ability that arises at "
            "sufficient model scale (approximately 100B parameters).\n\n"
            "## Conclusion\n\n"
            "Chain-of-thought prompting is a simple yet effective method for eliciting multi-step "
            "reasoning in large language models. It requires no fine-tuning and can be applied to "
            "any sufficiently large language model through few-shot prompting."
        ),
        "latex_sections": ["Abstract", "Introduction", "Method", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2305.10601",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "authors": [{"name": "Shunyu Yao"}, {"name": "Dian Yu"}, {"name": "Jeffrey Zhao"}],
        "abstract": (
            "We introduce Tree of Thoughts (ToT), a framework that generalizes over chain-of-thought "
            "prompting and enables exploration over coherent units of text (thoughts) that serve as "
            "intermediate steps toward problem solving. ToT allows language models to perform deliberate "
            "decision making by considering multiple reasoning paths and self-evaluating choices."
        ),
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "published": "2023-05-17",
        "citation_count": 1850,
        "method": "Tree-of-Thought",
        "markdown_content": (
            "# Tree of Thoughts: Deliberate Problem Solving with Large Language Models\n\n"
            "## Abstract\n\n"
            "We introduce Tree of Thoughts (ToT), a framework that generalizes chain-of-thought "
            "prompting by exploring multiple reasoning paths in a tree structure.\n\n"
            "## Introduction\n\n"
            "While chain-of-thought prompting enables step-by-step reasoning, it follows a single "
            "linear path without the ability to explore alternatives or backtrack. Inspired by the "
            "dual-process theory of human cognition, we propose Tree of Thoughts which allows "
            "deliberate planning and search over the space of possible reasoning paths.\n\n"
            "## Framework\n\n"
            "ToT defines a thought as a coherent language sequence that serves as an intermediate "
            "reasoning step. The framework has four key components: (1) thought decomposition, "
            "(2) thought generation using either sampling or proposal prompting, (3) state "
            "evaluation using value or vote prompting, and (4) search algorithms (BFS or DFS). "
            "The LM serves as both the generator and evaluator of thoughts.\n\n"
            "## Experiments\n\n"
            "We evaluate ToT on three novel tasks: Game of 24, Creative Writing, and Mini "
            "Crosswords. On Game of 24, ToT with GPT-4 achieves 74% success rate compared to "
            "4% for chain-of-thought prompting. On Creative Writing, ToT produces more coherent "
            "passages as judged by GPT-4 evaluation. On Mini Crosswords, ToT solves 60% of games "
            "compared to 16% for best-of-100 CoT sampling.\n\n"
            "## Conclusion\n\n"
            "Tree of Thoughts provides a principled framework for deliberate problem solving with "
            "language models through structured exploration of reasoning paths."
        ),
        "latex_sections": ["Abstract", "Introduction", "Framework", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2203.11171",
        "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
        "authors": [{"name": "Xuezhi Wang"}, {"name": "Jason Wei"}, {"name": "Dale Schuurmans"}],
        "abstract": (
            "We introduce self-consistency, a simple decoding strategy that replaces the naive greedy "
            "decoding used in chain-of-thought prompting. The key idea is to sample a diverse set of "
            "reasoning paths instead of only taking the greedy one, and then select the most consistent "
            "answer by marginalizing out the sampled reasoning paths."
        ),
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "published": "2022-03-21",
        "citation_count": 2100,
        "method": "Self-Consistency",
        "markdown_content": (
            "# Self-Consistency Improves Chain of Thought Reasoning in Language Models\n\n"
            "## Abstract\n\n"
            "We introduce self-consistency, a decoding strategy that samples diverse reasoning "
            "paths and selects the most consistent answer through majority voting.\n\n"
            "## Introduction\n\n"
            "Chain-of-thought prompting has shown promise for complex reasoning tasks, but "
            "typically uses greedy decoding which commits to a single reasoning path. We observe "
            "that complex reasoning tasks often admit multiple valid reasoning paths leading to "
            "the correct answer. Self-consistency exploits this intuition by sampling multiple "
            "reasoning paths and aggregating the answers.\n\n"
            "## Method\n\n"
            "Self-consistency works in three steps: (1) prompt the language model with chain-of-thought "
            "exemplars, (2) sample multiple diverse reasoning paths from the decoder by using a "
            "non-zero temperature, (3) marginalize over the reasoning paths by selecting the most "
            "frequent answer (majority voting). The method is unsupervised and requires no additional "
            "training or fine-tuning.\n\n"
            "## Experiments\n\n"
            "Self-consistency substantially improves over chain-of-thought prompting on arithmetic "
            "(GSM8K: +17.9%), commonsense (ARC: +3.9%), and symbolic reasoning benchmarks. "
            "With PaLM 540B, self-consistency achieves 74.4% on GSM8K, surpassing the previous "
            "best of 56.9% from standard chain-of-thought. Performance improves with more samples "
            "up to approximately 40 paths.\n\n"
            "## Conclusion\n\n"
            "Self-consistency is a simple, universally applicable method that significantly boosts "
            "chain-of-thought reasoning through diverse sampling and majority voting."
        ),
        "latex_sections": ["Abstract", "Introduction", "Method", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2305.20050",
        "title": "Let's Verify Step by Step",
        "authors": [{"name": "Hunter Lightman"}, {"name": "Vineet Kosaraju"}, {"name": "Yura Burda"}],
        "abstract": (
            "We investigate process supervision as a method for training reliable reward models for "
            "large language model reasoning. Process supervision provides feedback on each individual "
            "step of a chain-of-thought, rather than just the final answer. We show that process "
            "supervision significantly outperforms outcome supervision for training reward models."
        ),
        "categories": ["cs.CL", "cs.AI", "cs.LG"],
        "primary_category": "cs.CL",
        "published": "2023-05-31",
        "citation_count": 980,
        "method": "Process Supervision",
        "markdown_content": (
            "# Let's Verify Step by Step\n\n"
            "## Abstract\n\n"
            "We investigate process supervision as a method for training reliable reward models "
            "for large language model reasoning, providing feedback on each step.\n\n"
            "## Introduction\n\n"
            "As language models are increasingly used for complex reasoning, ensuring the reliability "
            "of each reasoning step becomes crucial. Outcome-based reward models (ORMs) only provide "
            "feedback on the final answer, while process-based reward models (PRMs) evaluate each "
            "intermediate step. We hypothesize that process supervision leads to more reliable "
            "reasoning by catching errors early in the chain of thought.\n\n"
            "## Method\n\n"
            "We train process reward models (PRMs) by collecting human labels on each step of "
            "model-generated solutions. For each step, annotators label whether it is correct, "
            "incorrect, or neutral. We compare PRMs against ORMs trained only on final answer "
            "correctness. Both models are used as verifiers to select among multiple candidate "
            "solutions generated by a base model.\n\n"
            "## Experiments\n\n"
            "On the MATH benchmark, the PRM-based approach achieves 78.2% accuracy compared to "
            "72.4% for ORM-based verification and 53.2% for majority voting. Process supervision "
            "produces more interpretable reward signals, as each step receives an individual score. "
            "We also release PRM800K, a dataset of 800K step-level human feedback labels.\n\n"
            "## Conclusion\n\n"
            "Process supervision is a more effective paradigm for training reward models that "
            "verify multi-step reasoning. Step-by-step verification catches errors earlier and "
            "produces more reliable outputs."
        ),
        "latex_sections": ["Abstract", "Introduction", "Method", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2210.03629",
        "title": "Automatic Chain of Thought Prompting in Large Language Models",
        "authors": [{"name": "Zhuosheng Zhang"}, {"name": "Aston Zhang"}, {"name": "Mu Li"}],
        "abstract": (
            "We propose Auto-CoT, a method that automatically constructs demonstrations with chains "
            "of thought for prompting. Auto-CoT samples questions with diversity and generates "
            "reasoning chains using zero-shot chain-of-thought prompting, eliminating the need for "
            "manual effort in crafting chain-of-thought exemplars."
        ),
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "published": "2022-10-07",
        "citation_count": 720,
        "method": "Automatic CoT",
        "markdown_content": (
            "# Automatic Chain of Thought Prompting in Large Language Models\n\n"
            "## Abstract\n\n"
            "We propose Auto-CoT, a method that automatically constructs chain-of-thought "
            "demonstrations without manual effort.\n\n"
            "## Introduction\n\n"
            "Chain-of-thought prompting requires carefully crafted exemplars with step-by-step "
            "reasoning traces. This manual process is labor-intensive and requires task-specific "
            "expertise. We address this limitation by proposing Auto-CoT, which automatically "
            "generates effective chain-of-thought demonstrations.\n\n"
            "## Method\n\n"
            "Auto-CoT consists of two main steps: (1) question clustering -- partition questions "
            "of a given dataset into clusters using sentence embeddings and k-means clustering, "
            "then select a representative question from each cluster; (2) demonstration generation "
            "-- for each selected question, generate a reasoning chain using zero-shot CoT "
            "(appending 'Let's think step by step'). The diversity-based sampling ensures that "
            "demonstrations cover different types of reasoning patterns.\n\n"
            "## Experiments\n\n"
            "Auto-CoT matches or exceeds the performance of manually crafted chain-of-thought "
            "prompts on 10 benchmark reasoning tasks including arithmetic (MultiArith, GSM8K), "
            "commonsense (CSQA), and symbolic reasoning. On MultiArith, Auto-CoT achieves 92.0% "
            "accuracy compared to 91.7% for manual CoT. The method eliminates the need for "
            "human annotation while maintaining competitive performance.\n\n"
            "## Conclusion\n\n"
            "Auto-CoT demonstrates that effective chain-of-thought demonstrations can be "
            "automatically constructed through diversity-based question sampling and zero-shot "
            "reasoning chain generation."
        ),
        "latex_sections": ["Abstract", "Introduction", "Method", "Experiments", "Conclusion"],
    },
]

# ── Noise Papers (different topics) ────────────────────────────────────────

NOISE_PAPERS = [
    {
        "arxiv_id": "2302.00001",
        "title": "Efficient Training of Vision Transformers with Progressive Resizing",
        "authors": [{"name": "Kai Chen"}, {"name": "Jie Zhou"}],
        "abstract": (
            "We propose progressive resizing strategies for efficient training of Vision Transformers. "
            "By starting training at lower resolutions and gradually increasing image size, we achieve "
            "3x training speedup while maintaining accuracy on ImageNet classification."
        ),
        "categories": ["cs.CV", "cs.LG"],
        "primary_category": "cs.CV",
        "published": "2023-02-01",
        "citation_count": 180,
        "method": None,
        "markdown_content": (
            "# Efficient Training of Vision Transformers with Progressive Resizing\n\n"
            "## Abstract\n\nProgressive resizing for efficient ViT training.\n\n"
            "## Method\n\nStart at 64x64, increase to 224x224 over training.\n\n"
            "## Results\n\n3x speedup on ImageNet with <0.5% accuracy drop."
        ),
        "latex_sections": ["Abstract", "Method", "Results"],
    },
    {
        "arxiv_id": "2303.00002",
        "title": "Graph Neural Networks for Molecular Property Prediction",
        "authors": [{"name": "Liang Zhang"}, {"name": "Yiwen Liu"}],
        "abstract": (
            "We develop graph neural network architectures for predicting molecular properties from "
            "chemical structures. Our approach uses message passing on molecular graphs with attention "
            "mechanisms to achieve state-of-the-art on QM9 and ZINC benchmarks."
        ),
        "categories": ["cs.LG", "q-bio.BM"],
        "primary_category": "cs.LG",
        "published": "2023-03-01",
        "citation_count": 95,
        "method": None,
        "markdown_content": (
            "# Graph Neural Networks for Molecular Property Prediction\n\n"
            "## Abstract\n\nGNN architectures for molecular property prediction.\n\n"
            "## Method\n\nMessage passing neural network with attention on molecular graphs.\n\n"
            "## Results\n\nState-of-the-art on QM9 and ZINC benchmarks."
        ),
        "latex_sections": ["Abstract", "Method", "Results"],
    },
    {
        "arxiv_id": "2304.00003",
        "title": "Federated Learning with Differential Privacy Guarantees",
        "authors": [{"name": "Maria Santos"}, {"name": "David Brown"}],
        "abstract": (
            "We propose a federated learning framework with formal differential privacy guarantees. "
            "Our method uses adaptive clipping and noise calibration to achieve strong privacy "
            "protection while minimizing accuracy degradation across heterogeneous client datasets."
        ),
        "categories": ["cs.LG", "cs.CR"],
        "primary_category": "cs.LG",
        "published": "2023-04-01",
        "citation_count": 140,
        "method": None,
        "markdown_content": (
            "# Federated Learning with Differential Privacy Guarantees\n\n"
            "## Abstract\n\nFL framework with formal differential privacy.\n\n"
            "## Method\n\nAdaptive clipping and noise calibration for privacy-utility tradeoff.\n\n"
            "## Results\n\nStrong privacy (epsilon=1) with <2% accuracy drop."
        ),
        "latex_sections": ["Abstract", "Method", "Results"],
    },
]

ALL_PAPERS = RELEVANT_PAPERS + NOISE_PAPERS

# ── Noise Notion pages ─────────────────────────────────────────────────────

NOISE_NOTION_PAGES = [
    {
        "title": "Weekly Team Standup Notes - Feb 2026",
        "content": "Discussion of project milestones. No major blockers reported.",
    },
    {
        "title": "Conference Travel Policy",
        "content": "Updated travel reimbursement policy for conference attendance. Submit receipts within 30 days.",
    },
]

# ── Noise GCal events ──────────────────────────────────────────────────────

NOISE_GCAL_EVENTS = [
    {
        "summary": "Department Meeting",
        "description": "Monthly department all-hands meeting.",
        "start": "2026-03-10 09:00:00",
        "end": "2026-03-10 10:00:00",
    },
    {
        "summary": "Grant Proposal Deadline",
        "description": "NSF grant proposal submission deadline.",
        "start": "2026-03-12 17:00:00",
        "end": "2026-03-12 18:00:00",
    },
]


def clear_tables(conn):
    tables = [
        "scholarly.arxiv_papers",
        "scholarly.scholar_papers",
        "arxiv.papers",
        "arxiv_latex.papers",
        "notion.blocks",
        "notion.comments",
        "notion.pages",
        "notion.databases",
        "gcal.events",
        "email.attachments",
        "email.sent_log",
        "email.messages",
        "email.drafts",
    ]
    for t in tables:
        try:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {t}")
            conn.commit()
        except Exception:
            conn.rollback()
    print("[preprocess] Cleared all target tables.")


def inject_scholarly_arxiv_papers(conn):
    with conn.cursor() as cur:
        for p in ALL_PAPERS:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                (id, title, authors, abstract, categories, primary_category,
                 published, updated, pdf_url, html_url)
                VALUES (%s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    abstract = EXCLUDED.abstract
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]), p["primary_category"],
                p["published"], p["published"],
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(ALL_PAPERS)} papers into scholarly.arxiv_papers")


def inject_arxiv_papers(conn):
    with conn.cursor() as cur:
        for p in ALL_PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers
                (id, title, authors, summary, categories, primary_category,
                 pdf_url, published, is_downloaded, markdown_content)
                VALUES (%s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary,
                    markdown_content = EXCLUDED.markdown_content
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]), p["primary_category"],
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                p["published"], True, p["markdown_content"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(ALL_PAPERS)} papers into arxiv.papers")


def inject_arxiv_latex_papers(conn):
    with conn.cursor() as cur:
        for p in ALL_PAPERS:
            # Build a simple LaTeX document from the markdown content
            author_str = " and ".join(a["name"] for a in p["authors"])
            latex_content = (
                f"\\documentclass{{article}}\n"
                f"\\title{{{p['title']}}}\n"
                f"\\author{{{author_str}}}\n"
                f"\\begin{{document}}\n\\maketitle\n\n"
                f"\\begin{{abstract}}\n{p['abstract']}\n\\end{{abstract}}\n\n"
            )
            for section in p["latex_sections"]:
                if section == "Abstract":
                    continue
                latex_content += f"\\section{{{section}}}\n"
                latex_content += f"Content of {section} section for {p['title']}.\n\n"
            latex_content += "\\end{document}"

            cur.execute("""
                INSERT INTO arxiv_latex.papers
                (id, title, abstract, full_prompt, sections, raw_latex, processed_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    abstract = EXCLUDED.abstract,
                    full_prompt = EXCLUDED.full_prompt,
                    sections = EXCLUDED.sections,
                    raw_latex = EXCLUDED.raw_latex,
                    processed_at = NOW()
            """, (
                p["arxiv_id"], p["title"], p["abstract"],
                p["markdown_content"],
                json.dumps(p["latex_sections"]),
                latex_content,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(ALL_PAPERS)} papers into arxiv_latex.papers")


def inject_scholarly_scholar_papers(conn):
    """Inject into scholarly.scholar_papers for completeness."""
    with conn.cursor() as cur:
        for p in ALL_PAPERS:
            first_author = p["authors"][0]["name"]
            pub_year = int(p["published"][:4])
            cur.execute("""
                INSERT INTO scholarly.scholar_papers
                (title, authors, abstract, pub_year, venue, citation_count, url)
                VALUES (%s, %s::jsonb, %s, %s, %s, %s, %s)
            """, (
                p["title"], json.dumps(p["authors"]),
                p["abstract"], pub_year,
                "arXiv preprint",
                p.get("citation_count", 0),
                f"http://arxiv.org/abs/{p['arxiv_id']}",
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(ALL_PAPERS)} papers into scholarly.scholar_papers")


def inject_notion_noise(conn):
    import uuid
    with conn.cursor() as cur:
        for page in NOISE_NOTION_PAGES:
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, properties, url)
                VALUES (%s, %s::jsonb, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                page_id,
                json.dumps({
                    "title": {
                        "title": [{"type": "text", "text": {"content": page["title"]}}]
                    },
                    "content": page["content"],
                }),
                f"https://notion.so/{page['title'].replace(' ', '-').lower()}",
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(NOISE_NOTION_PAGES)} noise Notion pages")


def inject_gcal_noise(conn):
    with conn.cursor() as cur:
        for ev in NOISE_GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime)
                VALUES (%s, %s, %s, %s)
            """, (ev["summary"], ev["description"], ev["start"], ev["end"]))
    conn.commit()
    print(f"[preprocess] Injected {len(NOISE_GCAL_EVENTS)} noise GCal events")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_scholarly_arxiv_papers(conn)
        inject_arxiv_papers(conn)
        inject_arxiv_latex_papers(conn)
        inject_scholarly_scholar_papers(conn)
        inject_notion_noise(conn)
        inject_gcal_noise(conn)
        ensure_email_folder(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
