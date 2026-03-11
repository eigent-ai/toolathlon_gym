"""Preprocess for canvas-scholarly-curriculum-review.
Clears scholarly and notion data, injects papers and parent page.
Starts mock HTTP server for accreditation requirements on port 30238.
Canvas is read-only.
"""
import argparse
import asyncio
import json
import os
import shutil
import uuid

import psycopg2

DB = dict(
    host=os.environ.get("PGHOST", "localhost"),
    port=5432,
    dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
    user="postgres",
    password="postgres",
)


def clear_and_inject_scholarly(cur):
    """Clear scholarly data and inject pedagogy papers."""
    print("[preprocess] Clearing scholarly data...")
    cur.execute("DELETE FROM scholarly.scholar_papers")
    cur.execute("DELETE FROM scholarly.arxiv_papers")

    papers = [
        {
            "title": "Active Learning Increases Student Performance in Science, Engineering, and Mathematics",
            "authors": ["Freeman S", "Eddy SL", "McDonough M", "Smith MK", "Okoroafor N", "Jordt H", "Wenderoth MP"],
            "abstract": "This meta-analysis of 225 studies demonstrates that active learning increases examination performance by about half a standard deviation and that lecturing increases failure rates by 55% compared to active learning. Results hold across all STEM disciplines and class sizes.",
            "pub_year": 2014,
            "venue": "Proceedings of the National Academy of Sciences",
            "citation_count": 5800,
            "url": "https://doi.org/10.1073/pnas.1319030111",
        },
        {
            "title": "Classroom Assessment Techniques: A Handbook for College Teachers",
            "authors": ["Angelo TA", "Cross KP"],
            "abstract": "A comprehensive guide to formative and summative assessment in higher education. Presents 50 classroom assessment techniques that help teachers understand what students are learning and how well.",
            "pub_year": 1993,
            "venue": "Jossey-Bass Publishers",
            "citation_count": 4200,
            "url": "https://doi.org/10.5555/assessment-techniques",
        },
        {
            "title": "Evaluation of Evidence-Based Practices in Online Learning: A Meta-Analysis and Review of Online Learning Studies",
            "authors": ["Means B", "Toyama Y", "Murphy R", "Bakia M", "Jones K"],
            "abstract": "A systematic review finding that students in online learning conditions performed modestly better than those receiving face-to-face instruction. Blended learning approaches showed even larger advantages.",
            "pub_year": 2009,
            "venue": "US Department of Education",
            "citation_count": 3500,
            "url": "https://doi.org/10.5555/online-learning-meta",
        },
        {
            "title": "Understanding by Design: A Framework for Curriculum Development",
            "authors": ["Wiggins G", "McTighe J"],
            "abstract": "Introduces the backward design framework for curriculum development. Argues that curriculum should start with desired outcomes, then determine acceptable evidence, and finally plan learning experiences.",
            "pub_year": 2005,
            "venue": "Association for Supervision and Curriculum Development",
            "citation_count": 2900,
            "url": "https://doi.org/10.5555/understanding-by-design",
        },
        {
            "title": "Student Engagement and Student Learning: Testing the Linkages",
            "authors": ["Carini RM", "Kuh GD", "Klein SP"],
            "abstract": "Examines the relationship between student engagement and desirable learning outcomes. Finds that engagement is positively linked to critical thinking, grades, and persistence.",
            "pub_year": 2006,
            "venue": "Research in Higher Education",
            "citation_count": 2100,
            "url": "https://doi.org/10.1007/s11162-006-9002-4",
        },
        # Noise papers
        {
            "title": "Machine Learning Approaches for Natural Language Processing",
            "authors": ["Zhang Y", "Liu M"],
            "abstract": "Survey of machine learning methods applied to NLP tasks including sentiment analysis and text classification.",
            "pub_year": 2020,
            "venue": "ACM Computing Surveys",
            "citation_count": 450,
            "url": "https://doi.org/10.5555/ml-nlp-survey",
        },
        {
            "title": "Blockchain Technology in Supply Chain Management",
            "authors": ["Kumar A", "Singh R"],
            "abstract": "Explores applications of blockchain technology in supply chain transparency and traceability.",
            "pub_year": 2021,
            "venue": "International Journal of Production Economics",
            "citation_count": 200,
            "url": "https://doi.org/10.5555/blockchain-supply",
        },
        {
            "title": "Climate Change Impact on Agricultural Productivity",
            "authors": ["Wang L", "Chen H", "Zhao K"],
            "abstract": "Analyzes the effects of climate change on crop yields across different regions and proposes adaptation strategies.",
            "pub_year": 2022,
            "venue": "Nature Climate Change",
            "citation_count": 350,
            "url": "https://doi.org/10.5555/climate-agriculture",
        },
    ]

    for i, p in enumerate(papers, 1):
        cur.execute(
            """INSERT INTO scholarly.scholar_papers
            (id, title, authors, abstract, pub_year, venue, citation_count, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                i,
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                p["pub_year"],
                p["venue"],
                p["citation_count"],
                p["url"],
            ),
        )
    print(f"[preprocess] Injected {len(papers)} scholarly papers.")


def clear_and_inject_notion(cur):
    """Clear notion data and inject a parent page for the report."""
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")

    # Create a parent page
    parent_page_id = str(uuid.uuid4())
    cur.execute(
        """INSERT INTO notion.pages (id, object, parent, properties, archived, in_trash)
        VALUES (%s, 'page', %s, %s, false, false)""",
        (
            parent_page_id,
            json.dumps({"type": "workspace", "workspace": True}),
            json.dumps(
                {
                    "title": {
                        "title": [
                            {
                                "text": {"content": "Accreditation Documents"},
                                "plain_text": "Accreditation Documents",
                            }
                        ]
                    }
                }
            ),
        ),
    )
    print(f"[preprocess] Notion parent page created: {parent_page_id}")


async def setup_mock_server():
    """Start HTTP server on port 30238."""
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files", "mock_pages")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    shutil.copytree(files_dir, tmp_dir)

    port = 30238
    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{port}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {port} --directory {tmp_dir} "
        f"> {tmp_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        clear_and_inject_scholarly(cur)
        clear_and_inject_notion(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()

    if args.agent_workspace:
        initial_ws = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "initial_workspace"
        )
        for f in os.listdir(initial_ws):
            src = os.path.join(initial_ws, f)
            if os.path.isfile(src) and not f.startswith("."):
                shutil.copy2(src, os.path.join(args.agent_workspace, f))
        print(f"[preprocess] Copied initial_workspace files to {args.agent_workspace}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
