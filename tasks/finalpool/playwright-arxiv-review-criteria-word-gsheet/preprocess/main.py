"""
Preprocess for playwright-arxiv-review-criteria-word-gsheet task.

Injects 3 papers into arxiv.papers and arxiv_latex.papers.
Clears gsheet data.
Extracts mock_pages.tar.gz and starts HTTP server on port 30214.
"""
import argparse
import asyncio
import json
import os
import shutil
import tarfile

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

PAPERS = [
    {
        "arxiv_id": "2301.07041",
        "title": "Scaling Laws for Neural Language Models",
        "authors": [{"name": "Jared Kaplan"}, {"name": "Sam McCandlish"}, {"name": "Tom Henighan"}],
        "abstract": (
            "We study empirical scaling laws for language model performance on the cross-entropy loss. "
            "The loss scales as a power-law with model size, dataset size, and the amount of compute used "
            "for training, with some trends spanning more than seven orders of magnitude. Other "
            "architectural details such as network width or depth have minimal effects within a wide range. "
            "Simple equations govern the dependence of overfitting on model/dataset size and the dependence "
            "of training speed on model size. These relationships allow us to determine the optimal allocation "
            "of a fixed compute budget."
        ),
        "categories": ["cs.LG", "cs.CL"],
        "primary_category": "cs.LG",
        "published": "2020-01-22",
        "markdown_content": (
            "# Scaling Laws for Neural Language Models\n\n"
            "## Introduction\n\n"
            "We present empirical scaling laws for language model performance. Performance scales predictably "
            "with model size, dataset size, and compute budget.\n\n"
            "## Scaling Laws\n\n"
            "The cross-entropy loss L follows a power law: L(N) = (N_c/N)^alpha_N where N is model parameters "
            "and N_c is a constant. Similarly for dataset size and compute. The exponents are approximately "
            "alpha_N = 0.076, alpha_D = 0.095, alpha_C = 0.050.\n\n"
            "## Experiments\n\n"
            "We trained over 1000 models spanning 3 orders of magnitude in scale. Results confirm that larger "
            "models trained on more data with more compute consistently achieve lower loss.\n\n"
            "## Conclusion\n\n"
            "Scaling laws provide a principled framework for predicting model performance and allocating "
            "compute budgets optimally. Larger models are more sample-efficient."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Scaling Laws for Neural Language Models}\n"
            "\\author{Jared Kaplan and Sam McCandlish}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We study empirical scaling laws for language model performance on cross-entropy loss. "
            "The loss scales as a power-law with model size, dataset size, and compute.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Performance of language models scales predictably with model size N, dataset size D, and compute C.\n\n"
            "\\section{Scaling Laws}\n"
            "The cross-entropy loss L follows power laws: L(N) = (N_c/N)^{\\alpha_N}, "
            "L(D) = (D_c/D)^{\\alpha_D}, L(C) = (C_c/C)^{\\alpha_C}. "
            "Exponents: alpha_N = 0.076, alpha_D = 0.095, alpha_C = 0.050.\n\n"
            "\\section{Experiments}\n"
            "Over 1000 models trained spanning 3 orders of magnitude confirm power-law scaling.\n\n"
            "\\section{Conclusion}\n"
            "Scaling laws predict performance and guide optimal compute allocation.\n\n"
            "\\end{document}"
        ),
        "sections": ["Introduction", "Scaling Laws", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2203.11171",
        "title": "Training language models to follow instructions with human feedback",
        "authors": [{"name": "Long Ouyang"}, {"name": "Jeff Wu"}, {"name": "Xu Jiang"}],
        "abstract": (
            "Starting from GPT-3, we train language models that are much better at following user instructions. "
            "We fine-tune GPT-3 using supervised learning on demonstration data and then further fine-tune "
            "using reinforcement learning from human feedback (RLHF). The resulting InstructGPT models are "
            "preferred by human labelers to GPT-3 outputs, are more truthful, and are less toxic, despite "
            "having only 1.3B parameters compared to the 175B GPT-3."
        ),
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "published": "2022-03-04",
        "markdown_content": (
            "# Training language models to follow instructions with human feedback\n\n"
            "## Introduction\n\n"
            "Large language models can generate unhelpful, untruthful, or toxic outputs. We use RLHF "
            "to align models with human intent through three steps.\n\n"
            "## Method\n\n"
            "Step 1: Supervised fine-tuning (SFT) on human demonstration data. "
            "Step 2: Train a reward model from human preference comparisons. "
            "Step 3: Fine-tune with PPO using the reward model.\n\n"
            "## Experiments\n\n"
            "InstructGPT 1.3B is preferred to GPT-3 175B by human evaluators on 85% of prompts. "
            "It shows better truthfulness on TruthfulQA and less toxicity.\n\n"
            "## Results\n\n"
            "RLHF achieves substantial alignment improvement with minimal trade-off in general capabilities."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Training language models to follow instructions with human feedback}\n"
            "\\author{Long Ouyang and Jeff Wu}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We train InstructGPT using RLHF. The resulting model follows instructions better "
            "and is preferred by humans despite being 100x smaller than GPT-3.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "LLMs generate untruthful or toxic outputs. RLHF aligns them with human intent.\n\n"
            "\\section{Method}\n"
            "Three steps: SFT on demonstrations, reward model from comparisons, PPO fine-tuning.\n\n"
            "\\section{Experiments}\n"
            "InstructGPT 1.3B preferred to GPT-3 175B on 85\\% of prompts.\n\n"
            "\\section{Results}\n"
            "RLHF substantially improves alignment with minimal capability trade-off.\n\n"
            "\\end{document}"
        ),
        "sections": ["Introduction", "Method", "Experiments", "Results"],
    },
    {
        "arxiv_id": "2205.01068",
        "title": "OPT: Open Pre-trained Transformer Language Models",
        "authors": [{"name": "Susan Zhang"}, {"name": "Stephen Roller"}, {"name": "Naman Goyal"}],
        "abstract": (
            "We present OPT, a suite of open-source large language models with parameters ranging from "
            "125M to 175B. OPT models match or exceed GPT-3 on most NLP benchmarks while being fully "
            "open-source. We describe the training methodology, hardware infrastructure, and the "
            "lessons learned from training at scale. We also release model weights and the training code "
            "to enable the research community to study large language models."
        ),
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "published": "2022-05-02",
        "markdown_content": (
            "# OPT: Open Pre-trained Transformer Language Models\n\n"
            "## Introduction\n\n"
            "We present OPT, open-source language models from 125M to 175B parameters. "
            "The goal is to enable the research community to study large LLMs.\n\n"
            "## Architecture\n\n"
            "OPT uses standard transformer architecture with pre-norm layer normalization, "
            "ReLU activations, and learned positional embeddings. Models trained with AdamW optimizer.\n\n"
            "## Training\n\n"
            "Trained on a combination of Common Crawl, Wikipedia, and other datasets totaling 800GB. "
            "Used tensor and pipeline parallelism across up to 992 A100 GPUs.\n\n"
            "## Results\n\n"
            "OPT-175B matches GPT-3 on most zero-shot and few-shot NLP benchmarks. "
            "Full model weights and training code released publicly."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{OPT: Open Pre-trained Transformer Language Models}\n"
            "\\author{Susan Zhang and Stephen Roller}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We present OPT, open-source LLMs from 125M to 175B parameters that match GPT-3 "
            "on NLP benchmarks while being fully open-source.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "OPT enables open research on large language models.\n\n"
            "\\section{Architecture}\n"
            "Standard transformer with pre-norm, ReLU, learned positional embeddings, AdamW.\n\n"
            "\\section{Training}\n"
            "800GB training data, 992 A100 GPUs, tensor and pipeline parallelism.\n\n"
            "\\section{Results}\n"
            "OPT-175B matches GPT-3 on zero-shot and few-shot benchmarks. Weights released publicly.\n\n"
            "\\end{document}"
        ),
        "sections": ["Introduction", "Architecture", "Training", "Results"],
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM arxiv.papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
        cur.execute("DELETE FROM gsheet.cells")
        try:
            cur.execute("DELETE FROM gsheet.permissions")
        except Exception:
            pass
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
    conn.commit()
    print("[preprocess] Cleared arxiv, arxiv_latex, and gsheet tables.")


def inject_arxiv_papers(conn):
    with conn.cursor() as cur:
        for p in PAPERS:
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
    print(f"[preprocess] Injected {len(PAPERS)} papers into arxiv.papers")


def inject_arxiv_latex(conn):
    with conn.cursor() as cur:
        for p in PAPERS:
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
                p["markdown_content"], json.dumps(p["sections"]),
                p["latex_content"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into arxiv_latex.papers")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30214."""
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
    port = 30214

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
    print(f"[preprocess] Mock server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_arxiv_papers(conn)
        inject_arxiv_latex(conn)
    finally:
        conn.close()

    await setup_mock_server()
    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
