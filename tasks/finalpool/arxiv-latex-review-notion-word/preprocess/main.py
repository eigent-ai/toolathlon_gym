"""
Preprocess for arxiv-latex-review-notion-word task.
- Clears and injects papers into arxiv.papers and arxiv_latex.papers.
- Clears notion, gsheet schemas so agent starts fresh.
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

# 3 relevant LLM fine-tuning/alignment papers
RELEVANT_PAPERS = [
    {
        "id": "2305.20050",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "authors": [{"name": "Rafael Rafailov"}, {"name": "Archit Sharma"}],
        "abstract": "While large language models show impressive capabilities, fine-tuning them to follow human preferences is challenging. We present DPO, a stable, performant, and computationally lightweight alternative to RLHF that directly optimizes the language model policy.",
        "sections": [
            {"title": "Abstract", "content": "We present DPO, a stable, performant, and computationally lightweight alternative to RLHF for aligning language models to human preferences."},
            {"title": "1 Introduction", "content": "Training LLMs to act in accordance with human preferences using reinforcement learning from human feedback (RLHF) is complex and unstable. DPO avoids fitting an explicit reward model."},
            {"title": "2 Related Work", "content": "RLHF has been applied successfully to fine-tune language models, but requires training a separate reward model and running PPO, which is computationally expensive."},
            {"title": "3 Method", "content": "Direct Preference Optimization (DPO) formulates the alignment problem as a classification task on preference data, deriving a simple closed-form update that avoids reinforcement learning."}
        ],
        "full_prompt": "\\documentclass{article}\\begin{document}We present DPO, a method for aligning language models to human preferences without explicit reward modeling.\\end{document}",
        "pdf_url": "https://arxiv.org/pdf/2305.20050",
        "published": "2023-05-30",
    },
    {
        "id": "2307.09288",
        "title": "Llama 2: Open Foundation and Fine-Tuned Chat Models",
        "authors": [{"name": "Hugo Touvron"}, {"name": "Louis Martin"}],
        "abstract": "We develop and release Llama 2, a collection of pretrained and fine-tuned large language models ranging in scale from 7 billion to 70 billion parameters. Our fine-tuned models, called Llama 2-Chat, are optimized for dialogue use cases.",
        "sections": [
            {"title": "Abstract", "content": "We develop and release Llama 2, pretrained and fine-tuned large language models optimized for dialogue."},
            {"title": "1 Introduction", "content": "Large language models (LLMs) have shown great promise as highly capable AI assistants. We present Llama 2, a family of open pretrained and fine-tuned chat models."},
            {"title": "2 Pretraining", "content": "Our training corpus includes publicly available data sources. We train models ranging from 7B to 70B parameters using standard transformer architectures."},
            {"title": "3 Fine-Tuning", "content": "We use supervised fine-tuning (SFT) followed by reinforcement learning from human feedback (RLHF) to align Llama 2-Chat with human preferences for helpfulness and safety."}
        ],
        "full_prompt": "\\documentclass{article}\\begin{document}We develop Llama 2, open foundation and fine-tuned chat models for dialogue.\\end{document}",
        "pdf_url": "https://arxiv.org/pdf/2307.09288",
        "published": "2023-07-18",
    },
    {
        "id": "2310.06825",
        "title": "Mistral 7B",
        "authors": [{"name": "Albert Jiang"}, {"name": "Alexandre Sablayrolles"}],
        "abstract": "We introduce Mistral 7B, a 7-billion-parameter language model engineered for superior performance and efficiency. Mistral 7B outperforms the best open models of all sizes on all evaluated benchmarks.",
        "sections": [
            {"title": "Abstract", "content": "We introduce Mistral 7B, a 7B parameter language model that outperforms larger models on multiple benchmarks."},
            {"title": "1 Introduction", "content": "NLP has been revolutionized by large language models. We present Mistral 7B, which uses grouped-query attention and sliding window attention for efficiency."},
            {"title": "2 Architecture", "content": "Mistral 7B uses grouped-query attention (GQA) for faster inference and sliding window attention (SWA) to handle sequences of arbitrary length efficiently."},
            {"title": "3 Results", "content": "Mistral 7B outperforms Llama 2 13B on all benchmarks and approaches the performance of much larger models on many tasks."}
        ],
        "full_prompt": "\\documentclass{article}\\begin{document}Mistral 7B is a language model with superior performance through architectural improvements.\\end{document}",
        "pdf_url": "https://arxiv.org/pdf/2310.06825",
        "published": "2023-10-10",
    },
]

# 1 noise paper about robotics
NOISE_PAPERS = [
    {
        "id": "2309.16349",
        "title": "Robot Learning with Affordances",
        "authors": [{"name": "Sherry Chen"}],
        "abstract": "We present a framework for robot learning using affordance representations. Affordances describe what actions an agent can perform on objects in the environment.",
        "sections": [
            {"title": "Abstract", "content": "Robot learning is challenging due to the complexity of physical interaction."},
            {"title": "1 Introduction", "content": "Affordances describe what actions an agent can perform on objects in the physical world."}
        ],
        "full_prompt": "\\documentclass{article}\\begin{document}Robot affordances for learning.\\end{document}",
        "pdf_url": "https://arxiv.org/pdf/2309.16349",
        "published": "2023-09-28",
    },
]

ALL_PAPERS = RELEVANT_PAPERS + NOISE_PAPERS


def clear_schemas(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM arxiv_latex.papers")
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("[preprocess] Cleared gsheet, notion, arxiv_latex, arxiv schemas")


def inject_papers(conn):
    with conn.cursor() as cur:
        for p in ALL_PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers
                    (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p["id"], p["title"], json.dumps(p["authors"]), p["abstract"],
                json.dumps(["cs.CL"]), "cs.CL",
                p["pdf_url"], p["published"], True
            ))
            cur.execute("""
                INSERT INTO arxiv_latex.papers
                    (id, title, abstract, full_prompt, sections)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                p["id"], p["title"], p["abstract"],
                p["full_prompt"], json.dumps(p["sections"])
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(ALL_PAPERS)} papers into arxiv and arxiv_latex schemas")


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
