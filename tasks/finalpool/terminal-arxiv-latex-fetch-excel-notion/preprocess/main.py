"""Preprocess script for terminal-arxiv-latex-fetch-excel-notion task."""
import os
import argparse, json, os, sys, shutil, tarfile, subprocess, time

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel"
}

TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAPERS = [
    {
        "arxiv_id": "2301.07041",
        "title": "Scaling Laws for Neural Language Models",
        "authors": [{"name": "Jared Kaplan"}, {"name": "Sam McCandlish"}],
        "abstract": "We study empirical scaling laws for language model performance on cross-entropy loss. The loss scales as a power-law with model size, dataset size, and compute.",
        "categories": ["cs.LG", "cs.CL"],
        "primary_category": "cs.LG",
        "published": "2020-01-22",
        "markdown_content": "# Scaling Laws for Neural Language Models\n\n## Introduction\nPerformance scales predictably with model size N, dataset size D, and compute C.\n\n## Scaling Laws\nL(N) = (N_c/N)^alpha_N. Exponents: alpha_N=0.076, alpha_D=0.095, alpha_C=0.050.\n\n## Experiments\nOver 1000 models spanning 3 orders of magnitude confirm power-law scaling.\n\n## Conclusion\nScaling laws predict performance and guide optimal compute allocation.",
        "latex_content": "\\documentclass{article}\n\\title{Scaling Laws for Neural Language Models}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\nPerformance scales predictably.\n\\section{Scaling Laws}\nPower-law relationships.\n\\section{Experiments}\nOver 1000 models tested.\n\\section{Conclusion}\nScaling laws guide allocation.\n\\end{document}",
        "sections": ["Introduction", "Scaling Laws", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2203.11171",
        "title": "Training language models to follow instructions with human feedback",
        "authors": [{"name": "Long Ouyang"}, {"name": "Jeff Wu"}],
        "abstract": "We train InstructGPT using RLHF. The 1.3B model is preferred to 175B GPT-3 by human evaluators.",
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "published": "2022-03-04",
        "markdown_content": "# Training language models to follow instructions with human feedback\n\n## Introduction\nLLMs generate untruthful or toxic outputs. RLHF aligns them with human intent.\n\n## Method\nThree steps: SFT on demonstrations, reward model from comparisons, PPO fine-tuning.\n\n## Experiments\nInstructGPT 1.3B preferred to GPT-3 175B on 85% of prompts.\n\n## Results\nRLHF substantially improves alignment with minimal capability trade-off.",
        "latex_content": "\\documentclass{article}\n\\title{Training language models to follow instructions}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\nLLMs need alignment.\n\\section{Method}\nSFT, reward model, PPO.\n\\section{Experiments}\n1.3B beats 175B.\n\\section{Results}\nRLHF works.\n\\end{document}",
        "sections": ["Introduction", "Method", "Experiments", "Results"],
    },
    {
        "arxiv_id": "2205.01068",
        "title": "OPT: Open Pre-trained Transformer Language Models",
        "authors": [{"name": "Susan Zhang"}, {"name": "Stephen Roller"}],
        "abstract": "We present OPT, open-source LLMs from 125M to 175B parameters that match GPT-3 on NLP benchmarks.",
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "published": "2022-05-02",
        "markdown_content": "# OPT: Open Pre-trained Transformer Language Models\n\n## Introduction\nOPT enables open research on large language models.\n\n## Architecture\nStandard transformer with pre-norm, ReLU, learned positional embeddings.\n\n## Training\n800GB training data, 992 A100 GPUs, tensor and pipeline parallelism.\n\n## Results\nOPT-175B matches GPT-3 on benchmarks. Weights released publicly.",
        "latex_content": "\\documentclass{article}\n\\title{OPT: Open Pre-trained Transformer Language Models}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\nOPT for open research.\n\\section{Architecture}\nStandard transformer.\n\\section{Training}\n992 A100 GPUs.\n\\section{Results}\nMatches GPT-3.\n\\end{document}",
        "sections": ["Introduction", "Architecture", "Training", "Results"],
    },
]

# Noise papers
NOISE_PAPERS = [
    {
        "arxiv_id": "2301.99901",
        "title": "Quantum Error Correction in Topological Systems",
        "authors": [{"name": "Alice Quantum"}],
        "abstract": "Novel approaches to quantum error correction using topological codes.",
        "categories": ["quant-ph"],
        "primary_category": "quant-ph",
        "published": "2023-01-15",
        "markdown_content": "# Quantum Error Correction\n\n## Introduction\nTopological codes.\n\n## Method\nSurface codes.",
        "latex_content": "\\documentclass{article}\n\\title{Quantum Error Correction}\n\\begin{document}\n\\section{Introduction}\nTopological codes.\n\\end{document}",
        "sections": ["Introduction", "Method"],
    },
    {
        "arxiv_id": "2302.99902",
        "title": "Climate Modeling with Deep Learning",
        "authors": [{"name": "Bob Climate"}],
        "abstract": "Deep learning for weather prediction and climate modeling.",
        "categories": ["cs.AI", "physics.ao-ph"],
        "primary_category": "physics.ao-ph",
        "published": "2023-02-20",
        "markdown_content": "# Climate Modeling\n\n## Introduction\nDeep learning for weather.",
        "latex_content": "\\documentclass{article}\n\\title{Climate Modeling}\n\\begin{document}\n\\section{Introduction}\nWeather prediction.\n\\end{document}",
        "sections": ["Introduction"],
    },
]


def get_conn():
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)


def clear_schemas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM arxiv_latex.papers")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM notion.users")
    conn.commit()
    cur.close()
    conn.close()
    print("[preprocess] Cleared arxiv_latex, notion schemas")


def inject_papers():
    conn = get_conn()
    cur = conn.cursor()
    for p in PAPERS + NOISE_PAPERS:
        cur.execute("""
            INSERT INTO arxiv_latex.papers (id, title, abstract, full_prompt, sections, raw_latex, processed_at)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, NOW())
            ON CONFLICT (id) DO UPDATE SET title=EXCLUDED.title, abstract=EXCLUDED.abstract,
            full_prompt=EXCLUDED.full_prompt, sections=EXCLUDED.sections, raw_latex=EXCLUDED.raw_latex
        """, (p["arxiv_id"], p["title"], p["abstract"], p["markdown_content"],
              json.dumps(p["sections"]), p["latex_content"]))
    conn.commit()
    cur.close()
    conn.close()
    print(f"[preprocess] Injected {len(PAPERS)} papers + {len(NOISE_PAPERS)} noise into arxiv_latex")


def setup_mock_server(port=30412):
    files_dir = os.path.join(TASK_ROOT, "files")
    tmp_dir = os.path.join(TASK_ROOT, "tmp")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        subprocess.run(f"kill -9 $(lsof -ti:{port}) 2>/dev/null", shell=True, timeout=5)
    except Exception:
        pass
    time.sleep(0.5)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)

    mock_dir = os.path.join(tmp_dir, "mock_pages")
    if os.path.exists(mock_dir):
        log_path = os.path.join(mock_dir, "server.log")
        subprocess.Popen(
            f"nohup python3 -m http.server {port} --directory {mock_dir} > {log_path} 2>&1 &",
            shell=True
        )
        time.sleep(1)
        print(f"Mock server started on port {port}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    clear_schemas()
    inject_papers()
    setup_mock_server(30412)


if __name__ == "__main__":
    main()
