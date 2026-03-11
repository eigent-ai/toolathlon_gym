"""
Preprocess for arxiv-survey-presentation task.
- Clears and injects NLP papers into arxiv.papers and arxiv_latex.papers.
- Starts mock HTTP server on port 30231.
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

MOCK_PORT = 30231

TARGET_PAPERS = [
    {
        "arxiv_id": "2404.00001",
        "title": "Chain-of-Thought Prompting for Complex Reasoning",
        "authors": [{"name": "Wei Zhang"}, {"name": "Yao Chen"}],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": "We demonstrate that chain-of-thought prompting significantly improves the reasoning capabilities of large language models. By providing step-by-step reasoning examples, models achieve 15% improvement on GSM8K and 12% on MATH benchmarks compared to standard prompting.",
        "published": "2024-04-01",
        "pub_year": 2024,
        "venue": "NeurIPS",
        "citation_count": 480,
        "latex_sections": [
            {"title": "Introduction", "content": "Reasoning remains a key challenge for LLMs. We explore prompting strategies to enhance reasoning."},
            {"title": "Methodology", "content": "Chain-of-thought prompting provides intermediate reasoning steps as demonstrations. We test few-shot CoT with 4-8 examples."},
            {"title": "Experiments", "content": "Evaluated on GSM8K and MATH benchmarks. CoT improves accuracy by 15% on GSM8K and 12% on MATH."},
            {"title": "Analysis", "content": "Longer chains produce better results for complex problems. Model scale matters for CoT effectiveness."},
        ],
    },
    {
        "arxiv_id": "2404.00002",
        "title": "Instruction Tuning for Improved Language Understanding",
        "authors": [{"name": "Sanjay Gupta"}, {"name": "Laura Kim"}],
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "abstract": "We present a systematic study of instruction tuning methods for improving language model understanding. Our approach uses 50,000 diverse instruction-response pairs and achieves state-of-the-art on MMLU with a 10B parameter model, outperforming models 5x larger.",
        "published": "2024-04-05",
        "pub_year": 2024,
        "venue": "ACL",
        "citation_count": 320,
        "latex_sections": [
            {"title": "Introduction", "content": "Instruction tuning bridges the gap between pre-training and task-specific performance."},
            {"title": "Methodology", "content": "We curate 50K instruction-response pairs spanning 200 task categories. Fine-tuning uses LoRA with rank 64."},
            {"title": "Experiments", "content": "Our 10B model achieves 72.5% on MMLU, outperforming 65B models. Evaluated on MMLU, BBH, and TriviaQA."},
            {"title": "Conclusion", "content": "Quality and diversity of instructions matter more than quantity for effective tuning."},
        ],
    },
    {
        "arxiv_id": "2404.00003",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP",
        "authors": [{"name": "Patrick Lewis"}, {"name": "Ethan Perez"}],
        "categories": ["cs.CL", "cs.IR"],
        "primary_category": "cs.CL",
        "abstract": "We present an improved retrieval-augmented generation framework that combines dense retrieval with a generator model. Our system reduces hallucination by 40% on knowledge-intensive tasks while improving factual accuracy on Natural Questions and TriviaQA benchmarks.",
        "published": "2024-04-10",
        "pub_year": 2024,
        "venue": "EMNLP",
        "citation_count": 250,
        "latex_sections": [
            {"title": "Introduction", "content": "LLMs suffer from hallucination. RAG grounds generation in retrieved evidence."},
            {"title": "Methodology", "content": "Dense retrieval with contriever model, combined with a fine-tuned LLaMA generator. Retrieves top-5 passages per query."},
            {"title": "Experiments", "content": "40% reduction in hallucination on NQ and TriviaQA. Evaluated on Natural Questions and TriviaQA datasets."},
            {"title": "Conclusion", "content": "RAG is essential for knowledge-intensive tasks requiring factual accuracy."},
        ],
    },
    {
        "arxiv_id": "2404.00004",
        "title": "Self-Consistency in Language Model Reasoning",
        "authors": [{"name": "Xuezhi Wang"}, {"name": "Jason Wei"}],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": "We introduce self-consistency decoding that samples multiple reasoning paths and selects the most consistent answer. This approach improves chain-of-thought reasoning by 8% on GSM8K without any additional training, demonstrating that diverse reasoning is key to reliable answers.",
        "published": "2024-04-15",
        "pub_year": 2024,
        "venue": "ICLR",
        "citation_count": 380,
        "latex_sections": [
            {"title": "Introduction", "content": "Greedy decoding limits reasoning quality. Self-consistency explores diverse paths."},
            {"title": "Methodology", "content": "Sample 40 reasoning paths using temperature sampling. Marginalize over paths to select the most frequent answer."},
            {"title": "Experiments", "content": "8% improvement on GSM8K over standard CoT. Evaluated on GSM8K, SVAMP, and AQuA datasets."},
            {"title": "Conclusion", "content": "Self-consistency is a simple yet effective method for improving reasoning reliability."},
        ],
    },
    {
        "arxiv_id": "2404.00005",
        "title": "Multimodal Large Language Models for Visual Reasoning",
        "authors": [{"name": "Haotian Liu"}, {"name": "Chunyuan Li"}],
        "categories": ["cs.CV", "cs.CL"],
        "primary_category": "cs.CV",
        "abstract": "We present a multimodal language model that combines vision encoders with large language models for visual reasoning tasks. Our model achieves state-of-the-art on VQA, visual dialogue, and image captioning benchmarks by using a visual instruction tuning approach.",
        "published": "2024-04-20",
        "pub_year": 2024,
        "venue": "CVPR",
        "citation_count": 550,
        "latex_sections": [
            {"title": "Introduction", "content": "Extending LLMs to multimodal understanding is crucial for general AI."},
            {"title": "Methodology", "content": "Connect CLIP vision encoder to LLaMA via a projection layer. Visual instruction tuning on 600K image-text pairs."},
            {"title": "Experiments", "content": "State-of-the-art on VQA v2, visual dialogue, and COCO captioning. Evaluated on VQA, GQA, and VizWiz datasets."},
            {"title": "Conclusion", "content": "Visual instruction tuning is effective for building multimodal LLMs."},
        ],
    },
]

NOISE_PAPERS = [
    {
        "arxiv_id": "2404.00006",
        "title": "Efficient Database Query Optimization",
        "authors": [{"name": "Mark Johnson"}],
        "categories": ["cs.DB"],
        "primary_category": "cs.DB",
        "abstract": "Novel query optimization techniques for distributed databases using learned cost models.",
        "published": "2024-04-25",
        "pub_year": 2024,
        "venue": "SIGMOD",
        "citation_count": 30,
    },
    {
        "arxiv_id": "2404.00007",
        "title": "Wireless Network Optimization via Machine Learning",
        "authors": [{"name": "Amy Wright"}],
        "categories": ["cs.NI", "cs.LG"],
        "primary_category": "cs.NI",
        "abstract": "Applying ML to optimize wireless network resource allocation and scheduling.",
        "published": "2024-04-28",
        "pub_year": 2024,
        "venue": "MobiCom",
        "citation_count": 20,
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM arxiv.papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
    conn.commit()
    print("[preprocess] Cleared arxiv, arxiv_latex")


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
                json.dumps([]), "", False,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(papers)} into arxiv.papers")


def inject_arxiv_latex(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            if "latex_sections" not in p:
                continue
            sections = p["latex_sections"]
            parts = [f"\\section{{{s['title']}}}\n{s['content']}" for s in sections]
            full_prompt = f"\\title{{{p['title']}}}\n\\begin{{abstract}}\n{p['abstract']}\n\\end{{abstract}}\n\n" + "\n\n".join(parts)
            cur.execute("""
                INSERT INTO arxiv_latex.papers (id, title, abstract, full_prompt, sections)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title, abstract = EXCLUDED.abstract,
                    full_prompt = EXCLUDED.full_prompt, sections = EXCLUDED.sections
            """, (p["arxiv_id"], p["title"], p["abstract"], full_prompt, json.dumps(sections)))
    conn.commit()
    print("[preprocess] Injected latex papers")


async def setup_mock_server():
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

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
        serve_dir = tmp_dir
        if os.path.exists(mock_src):
            shutil.copytree(mock_src, os.path.join(tmp_dir, "mock_pages"))
            serve_dir = os.path.join(tmp_dir, "mock_pages")

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{MOCK_PORT}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {MOCK_PORT} --directory {serve_dir} "
        f"> {serve_dir}/server.log 2>&1 &")
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server at http://localhost:{MOCK_PORT}")


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
        inject_arxiv_latex(conn, TARGET_PAPERS)
    finally:
        conn.close()

    await setup_mock_server()
    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
