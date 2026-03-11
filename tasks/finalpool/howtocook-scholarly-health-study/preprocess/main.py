"""
Preprocess script for howtocook-scholarly-health-study task.

This script:
1. Clears scholarly data and injects nutrition-related papers
2. Extracts mock_pages.tar.gz and starts HTTP server on port 30155
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
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PAPERS = [
    {
        "arxiv_id": "2001.00001",
        "title": "Dietary Patterns and Risk of Chronic Disease",
        "authors": [
            {"name": "Sarah Johnson"}, {"name": "Michael Brown"},
            {"name": "Lisa Wang"}, {"name": "David Kim"},
        ],
        "categories": ["q-bio.OT"],
        "primary_category": "q-bio.OT",
        "abstract": (
            "This comprehensive review examines the relationship between dietary patterns "
            "and the risk of chronic diseases including cardiovascular disease, diabetes, "
            "and cancer. We analyze data from 45 prospective cohort studies spanning "
            "multiple countries and dietary traditions. Our findings suggest that diets "
            "rich in whole grains, fruits, vegetables, and lean proteins are associated "
            "with significantly reduced chronic disease risk."
        ),
        "published": "2020-01-15",
        "pub_year": 2020,
        "venue": "Annual Review of Nutrition",
        "citation_count": 500,
    },
    {
        "arxiv_id": "2002.00002",
        "title": "Mediterranean Diet and Cardiovascular Health",
        "authors": [
            {"name": "Maria Garcia"}, {"name": "Antonio Romano"},
            {"name": "Elena Costa"},
        ],
        "categories": ["q-bio.OT"],
        "primary_category": "q-bio.OT",
        "abstract": (
            "The Mediterranean diet, characterized by high consumption of olive oil, "
            "fruits, vegetables, legumes, and moderate wine intake, has been extensively "
            "studied for its cardiovascular benefits. This meta-analysis of 23 randomized "
            "controlled trials demonstrates significant reductions in cardiovascular events, "
            "blood pressure, and inflammatory markers among adherents to the Mediterranean "
            "dietary pattern."
        ),
        "published": "2020-06-20",
        "pub_year": 2020,
        "venue": "The Lancet",
        "citation_count": 800,
    },
    {
        "arxiv_id": "2003.00003",
        "title": "Plant-Based Diets: A Review of Evidence",
        "authors": [
            {"name": "James Chen"}, {"name": "Rachel Green"},
            {"name": "Thomas Liu"},
        ],
        "categories": ["q-bio.OT"],
        "primary_category": "q-bio.OT",
        "abstract": (
            "Plant-based diets have gained significant popularity in recent years. "
            "This review examines the evidence for health benefits of plant-based "
            "dietary patterns, including vegan and vegetarian diets. We analyze "
            "nutritional adequacy, impact on body weight, cardiovascular risk factors, "
            "and cancer prevention. The evidence supports well-planned plant-based diets "
            "as nutritionally adequate and beneficial for disease prevention."
        ),
        "published": "2021-03-10",
        "pub_year": 2021,
        "venue": "Nutrients",
        "citation_count": 350,
    },
    {
        "arxiv_id": "2004.00004",
        "title": "Machine Learning for Drug Discovery",
        "authors": [
            {"name": "Alex Zhang"}, {"name": "Jennifer Wu"},
        ],
        "categories": ["cs.AI", "q-bio.BM"],
        "primary_category": "cs.AI",
        "abstract": (
            "Machine learning approaches have revolutionized drug discovery pipelines. "
            "This paper reviews deep learning architectures for molecular property "
            "prediction, generative models for de novo drug design, and reinforcement "
            "learning for lead optimization. We benchmark state-of-the-art methods "
            "on standard datasets and discuss future directions."
        ),
        "published": "2021-07-01",
        "pub_year": 2021,
        "venue": "Nature Machine Intelligence",
        "citation_count": 1000,
    },
]


def clear_scholarly(cur):
    """Clear scholarly data."""
    print("[preprocess] Clearing scholarly data...")
    cur.execute("DELETE FROM scholarly.arxiv_papers")
    cur.execute("DELETE FROM scholarly.scholar_papers")
    print("[preprocess] Scholarly data cleared.")


def inject_scholarly_arxiv(cur):
    """Inject papers into scholarly.arxiv_papers."""
    for p in PAPERS:
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
    print(f"[preprocess] Injected {len(PAPERS)} papers into scholarly.arxiv_papers")


def inject_scholarly_scholar(cur):
    """Inject papers into scholarly.scholar_papers."""
    for p in PAPERS:
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
    print(f"[preprocess] Injected {len(PAPERS)} papers into scholarly.scholar_papers")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30155."""
    print("[preprocess] Setting up mock nutrition data server...")

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
    port = 30155

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
    print(f"[preprocess] Mock nutrition server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_scholarly(cur)
        inject_scholarly_arxiv(cur)
        inject_scholarly_scholar(cur)
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
