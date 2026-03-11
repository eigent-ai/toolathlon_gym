"""
Preprocess for arxiv-method-benchmark-tracker task.
- Clears and injects papers into arxiv.papers, arxiv_latex.papers, notion.
- Starts mock HTTP server on port 30229 for benchmark leaderboard.
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

MOCK_PORT = 30229

TARGET_PAPERS = [
    {
        "arxiv_id": "2402.10001",
        "title": "Vision Transformer at Scale",
        "authors": [{"name": "Alexei Dosovitskiy"}, {"name": "Lucas Beyer"}],
        "categories": ["cs.CV", "cs.LG"],
        "primary_category": "cs.CV",
        "abstract": (
            "We explore scaling Vision Transformers (ViT) to unprecedented sizes. Our ViT-Large "
            "model achieves 91.2% top-1 accuracy on ImageNet by pre-training on a curated dataset "
            "of 3 billion images. We demonstrate that careful scaling of patch size, model depth, "
            "and attention heads yields consistent improvements. The key contribution is a new "
            "progressive resolution training strategy that enables efficient large-scale training."
        ),
        "published": "2024-02-10",
        "pub_year": 2024,
        "venue": "CVPR",
        "citation_count": 680,
        "latex_sections": [
            {"title": "Introduction", "content": "Vision Transformers have shown remarkable performance on image recognition tasks. We scale ViT to a new level with careful architecture and training choices."},
            {"title": "Methodology", "content": "We introduce progressive resolution training, starting from 64x64 patches and increasing to 224x224. The ViT-Large model uses 24 layers, 16 heads, and 1024 hidden dimensions. Training uses the ImageNet-21K dataset augmented with web-scraped images."},
            {"title": "Experiments", "content": "ViT-Large achieves 91.2% top-1 accuracy on ImageNet. Ablation studies show that progressive resolution contributes 1.5% accuracy improvement. The primary dataset used is ImageNet with additional JFT-3B data."},
            {"title": "Conclusion", "content": "Scaling Vision Transformers with progressive resolution training is an effective strategy for achieving state-of-the-art image classification."},
        ],
    },
    {
        "arxiv_id": "2402.10002",
        "title": "ConvNeXt: A Modern ConvNet",
        "authors": [{"name": "Zhuang Liu"}, {"name": "Hanzi Mao"}],
        "categories": ["cs.CV", "cs.LG"],
        "primary_category": "cs.CV",
        "abstract": (
            "We revisit the design of convolutional neural networks and propose ConvNeXt, a pure "
            "convolutional architecture that competes with Vision Transformers. By modernizing "
            "ResNet with transformer-inspired design choices such as larger kernel sizes, layer "
            "normalization, and inverted bottlenecks, ConvNeXt-XL achieves 89.5% top-1 accuracy "
            "on ImageNet. Our key contribution is demonstrating that ConvNets can match transformer "
            "performance when equipped with modern training and architecture choices."
        ),
        "published": "2024-02-12",
        "pub_year": 2024,
        "venue": "CVPR",
        "citation_count": 450,
        "latex_sections": [
            {"title": "Introduction", "content": "Can convolutional networks compete with Vision Transformers? We answer yes by modernizing the classic ResNet design."},
            {"title": "Methodology", "content": "ConvNeXt adopts larger 7x7 kernel sizes, layer normalization instead of batch normalization, GELU activation, and inverted bottleneck blocks. The ConvNeXt-XL variant has 350M parameters."},
            {"title": "Experiments", "content": "ConvNeXt-XL achieves 89.5% on ImageNet. Evaluated on ImageNet-1K and COCO detection benchmarks. Comparable to Swin Transformer performance."},
            {"title": "Conclusion", "content": "Modern ConvNets remain competitive with transformers when properly designed."},
        ],
    },
    {
        "arxiv_id": "2402.10003",
        "title": "Large Language Model Training",
        "authors": [{"name": "Hugo Touvron"}, {"name": "Louis Martin"}],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We present techniques for training large language models at scale, applied to create "
            "LLaMA-3, a family of open-source language models. Our approach uses a combination of "
            "data curation, efficient tokenization, and novel training infrastructure optimizations. "
            "LLaMA-3 achieves 92.3% on MMLU, demonstrating competitive performance with proprietary "
            "models. Key contributions include a new data mixing strategy and grouped query attention."
        ),
        "published": "2024-02-15",
        "pub_year": 2024,
        "venue": "arXiv",
        "citation_count": 890,
        "latex_sections": [
            {"title": "Introduction", "content": "Open-source language models have lagged behind proprietary ones. LLaMA-3 closes this gap through careful training at scale."},
            {"title": "Methodology", "content": "We train on 15 trillion tokens with a novel data mixing strategy. The architecture uses grouped query attention (GQA) for efficient inference. Model sizes range from 8B to 70B parameters."},
            {"title": "Experiments", "content": "LLaMA-3 70B achieves 92.3% on MMLU. Evaluated on MMLU, HumanEval, GSM8K, and MATH benchmarks. Outperforms all open-source models."},
            {"title": "Conclusion", "content": "Open-source models can achieve competitive performance through careful data curation and training."},
        ],
    },
    {
        "arxiv_id": "2402.10004",
        "title": "Diffusion Models for Generation",
        "authors": [{"name": "Robin Rombach"}, {"name": "Andreas Blattmann"}],
        "categories": ["cs.CV", "cs.LG"],
        "primary_category": "cs.CV",
        "abstract": (
            "We introduce DiffusionXL, a latent diffusion model that achieves state-of-the-art "
            "image generation quality with an FID score of 2.1 on ImageNet 256x256. Our key "
            "contribution is a multi-scale latent space architecture that enables both high-fidelity "
            "and high-resolution generation. The model uses a cascade of diffusion stages operating "
            "at different spatial resolutions in the latent space."
        ),
        "published": "2024-02-18",
        "pub_year": 2024,
        "venue": "NeurIPS",
        "citation_count": 560,
        "latex_sections": [
            {"title": "Introduction", "content": "Diffusion models have emerged as the dominant generative modeling paradigm. We push their quality further with multi-scale latent diffusion."},
            {"title": "Methodology", "content": "DiffusionXL operates in a multi-scale latent space with 3 cascade stages. Each stage uses a UNet denoiser with cross-attention conditioning. Training uses the ImageNet dataset and a learned VAE encoder."},
            {"title": "Experiments", "content": "Achieves FID 2.1 on ImageNet 256x256. Evaluated on ImageNet, LSUN, and FFHQ datasets. Outperforms all prior diffusion and GAN models."},
            {"title": "Conclusion", "content": "Multi-scale latent diffusion enables new levels of image generation quality."},
        ],
    },
]

NOISE_PAPERS = [
    {
        "arxiv_id": "2402.10005",
        "title": "Protein Folding Advances",
        "authors": [{"name": "Sarah Lee"}],
        "categories": ["q-bio.BM", "cs.AI"],
        "primary_category": "q-bio.BM",
        "abstract": (
            "Advances in protein structure prediction using graph neural networks and attention "
            "mechanisms. Our method achieves competitive performance with AlphaFold2 on CASP15."
        ),
        "published": "2024-02-20",
        "pub_year": 2024,
        "venue": "Nature Methods",
        "citation_count": 120,
    },
    {
        "arxiv_id": "2402.10006",
        "title": "Climate Modeling with ML",
        "authors": [{"name": "David Wang"}],
        "categories": ["cs.LG", "physics.ao-ph"],
        "primary_category": "physics.ao-ph",
        "abstract": (
            "Machine learning approaches for climate modeling and weather prediction. We develop "
            "a neural operator for global weather forecasting that outperforms numerical methods."
        ),
        "published": "2024-02-22",
        "pub_year": 2024,
        "venue": "Nature",
        "citation_count": 95,
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM arxiv.papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
    conn.commit()
    print("[preprocess] Cleared arxiv.papers, arxiv_latex.papers")


def clear_notion(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        cur.execute("DELETE FROM notion.users")
    conn.commit()
    print("[preprocess] Cleared Notion data")


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
    print(f"[preprocess] Injected {len(papers)} papers into arxiv.papers")


def inject_arxiv_latex(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            if "latex_sections" not in p:
                continue
            sections = p["latex_sections"]
            latex_parts = []
            for s in sections:
                latex_parts.append(f"\\section{{{s['title']}}}\n{s['content']}")
            full_prompt = f"\\title{{{p['title']}}}\n\\begin{{abstract}}\n{p['abstract']}\n\\end{{abstract}}\n\n" + "\n\n".join(latex_parts)

            cur.execute("""
                INSERT INTO arxiv_latex.papers (id, title, abstract, full_prompt, sections)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title, abstract = EXCLUDED.abstract,
                    full_prompt = EXCLUDED.full_prompt, sections = EXCLUDED.sections
            """, (
                p["arxiv_id"], p["title"], p["abstract"],
                full_prompt, json.dumps(sections),
            ))
    conn.commit()
    print(f"[preprocess] Injected latex papers into arxiv_latex.papers")


def inject_notion_parent(conn):
    """Insert a parent page for the tracker."""
    import uuid
    page_id = f"parent-bench-{uuid.uuid4().hex[:8]}"
    props = json.dumps({
        "title": [{"text": {"content": "Research Knowledge Base"}}],
    })
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO notion.pages (id, object, properties, created_time, last_edited_time) "
            "VALUES (%s, %s, %s::jsonb, NOW(), NOW())",
            (page_id, "page", props))
    conn.commit()
    print(f"[preprocess] Injected Notion parent page: {page_id}")


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
        clear_notion(conn)
        all_papers = TARGET_PAPERS + NOISE_PAPERS
        inject_arxiv_papers(conn, all_papers)
        inject_arxiv_latex(conn, TARGET_PAPERS)
        inject_notion_parent(conn)
    finally:
        conn.close()

    await setup_mock_server()
    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
