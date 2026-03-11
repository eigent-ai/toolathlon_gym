"""
Preprocess for scholarly-grant-proposal-prep task.
- Clears scholarly, email, gcal schemas.
- Injects 5 target + 3 noise papers into scholarly.
- Sets up email account config.
- Starts mock HTTP server on port 30230.
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

MOCK_PORT = 30230

TARGET_PAPERS = [
    {
        "arxiv_id": "2403.00001",
        "title": "Safe Reinforcement Learning for Language Model Alignment",
        "authors": [{"name": "John Smith"}, {"name": "Anna Lee"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": "We propose a safe reinforcement learning framework for aligning large language models with human values. Our approach uses constrained policy optimization with safety critics to prevent harmful outputs while maintaining helpfulness.",
        "published": "2024-03-01",
        "pub_year": 2024,
        "venue": "NeurIPS",
        "citation_count": 310,
    },
    {
        "arxiv_id": "2403.00002",
        "title": "Interpretable Neural Networks via Concept Bottleneck Layers",
        "authors": [{"name": "Maria Garcia"}, {"name": "Tom Wilson"}],
        "categories": ["cs.LG", "cs.AI"],
        "primary_category": "cs.LG",
        "abstract": "We introduce concept bottleneck layers that force neural networks to make predictions through interpretable intermediate concepts. Applied to medical imaging and natural language tasks, our method achieves comparable accuracy to black-box models while providing concept-level explanations.",
        "published": "2024-03-05",
        "pub_year": 2024,
        "venue": "ICML",
        "citation_count": 180,
    },
    {
        "arxiv_id": "2403.00003",
        "title": "Adversarially Robust Vision Transformers",
        "authors": [{"name": "David Kim"}, {"name": "Rachel Chen"}],
        "categories": ["cs.CV", "cs.LG"],
        "primary_category": "cs.CV",
        "abstract": "We study the adversarial robustness of Vision Transformers and propose a robust training framework that combines adversarial training with attention regularization. Our method improves robust accuracy by 12% over standard adversarial training on ImageNet.",
        "published": "2024-03-10",
        "pub_year": 2024,
        "venue": "ICLR",
        "citation_count": 145,
    },
    {
        "arxiv_id": "2403.00004",
        "title": "Deep Learning for Medical Image Segmentation: A Comprehensive Review",
        "authors": [{"name": "Emily Zhang"}, {"name": "Kevin Liu"}],
        "categories": ["cs.CV", "cs.AI"],
        "primary_category": "cs.CV",
        "abstract": "A comprehensive review of deep learning methods for medical image segmentation covering CT, MRI, and X-ray modalities. We analyze 200 papers and identify key trends including the shift to transformer-based architectures and self-supervised pre-training strategies for limited medical data.",
        "published": "2024-03-15",
        "pub_year": 2024,
        "venue": "Medical Image Analysis",
        "citation_count": 420,
    },
    {
        "arxiv_id": "2403.00005",
        "title": "Graph Neural Networks for Drug-Target Interaction Prediction",
        "authors": [{"name": "Sophie Brown"}, {"name": "Alex Taylor"}],
        "categories": ["cs.LG", "q-bio.QM"],
        "primary_category": "cs.LG",
        "abstract": "We present a graph neural network framework for predicting drug-target interactions using molecular graphs and protein structure information. Our model achieves state-of-the-art performance on the DUD-E and BindingDB benchmarks with 15% improvement in AUC.",
        "published": "2024-03-20",
        "pub_year": 2024,
        "venue": "Nature Machine Intelligence",
        "citation_count": 250,
    },
]

NOISE_PAPERS = [
    {
        "arxiv_id": "2403.00006",
        "title": "Federated Learning for IoT Devices",
        "authors": [{"name": "Robert Hill"}],
        "categories": ["cs.DC", "cs.LG"],
        "primary_category": "cs.DC",
        "abstract": "A federated learning framework optimized for resource-constrained IoT devices.",
        "published": "2024-03-25",
        "pub_year": 2024,
        "venue": "IoTDI",
        "citation_count": 30,
    },
    {
        "arxiv_id": "2403.00007",
        "title": "Neural Architecture Search for Edge Computing",
        "authors": [{"name": "Diana Patel"}],
        "categories": ["cs.LG"],
        "primary_category": "cs.LG",
        "abstract": "Efficient NAS methods for deploying neural networks on edge devices with limited compute.",
        "published": "2024-03-28",
        "pub_year": 2024,
        "venue": "MLSys",
        "citation_count": 45,
    },
    {
        "arxiv_id": "2403.00008",
        "title": "Autonomous Vehicle Path Planning with Deep Learning",
        "authors": [{"name": "George White"}],
        "categories": ["cs.RO", "cs.AI"],
        "primary_category": "cs.RO",
        "abstract": "Deep learning approaches for real-time path planning in autonomous vehicles.",
        "published": "2024-04-01",
        "pub_year": 2024,
        "venue": "ICRA",
        "citation_count": 55,
    },
]


def clear_schemas(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        # Clear email
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM email.drafts")
        cur.execute("DELETE FROM email.folders")
        cur.execute("DELETE FROM email.account_config")
        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
    conn.commit()
    print("[preprocess] Cleared scholarly, email, gcal schemas")


def setup_email(conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO email.account_config (email, name) VALUES (%s, %s)",
            ("pi@university.edu", "Dr. Elena Rodriguez"))
        cur.execute(
            "INSERT INTO email.folders (name, delimiter, flags) VALUES (%s, %s, %s)",
            ("INBOX", "/", '["\\\\Inbox"]'))
        cur.execute(
            "INSERT INTO email.folders (name, delimiter, flags) VALUES (%s, %s, %s)",
            ("Sent", "/", '["\\\\Sent"]'))
    conn.commit()
    print("[preprocess] Email account configured")


def inject_scholarly(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                (id, title, authors, abstract, categories, primary_category,
                 published, updated, doi, journal_ref, pdf_url, html_url, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title, authors = EXCLUDED.authors,
                    abstract = EXCLUDED.abstract
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]),
                p["primary_category"], p["published"], p["published"],
                None, p.get("venue"),
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}", None,
            ))
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
    print(f"[preprocess] Injected {len(papers)} papers into scholarly")


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
        clear_schemas(conn)
        setup_email(conn)
        all_papers = TARGET_PAPERS + NOISE_PAPERS
        inject_scholarly(conn, all_papers)
    finally:
        conn.close()

    await setup_mock_server()
    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
