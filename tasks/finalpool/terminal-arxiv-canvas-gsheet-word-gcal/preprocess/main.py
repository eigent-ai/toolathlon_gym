"""Preprocess for terminal-arxiv-canvas-gsheet-word-gcal.
Canvas is read-only. Clear arxiv, gsheet, gcal schemas. Inject arxiv papers + gcal events.
"""
import argparse
import glob
import json
import os
import uuid
from datetime import datetime, timedelta

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_schemas(cur):
    print("[preprocess] Clearing arxiv, gsheet, gcal data...")
    cur.execute("DELETE FROM arxiv.papers")
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    cur.execute("DELETE FROM gcal.events")
    print("[preprocess] Schemas cleared.")


def inject_arxiv_papers(cur):
    print("[preprocess] Injecting arxiv papers...")
    papers = [
        # 4 relevant papers
        {
            "id": "2025.10001",
            "title": "Deep Learning Algorithms for Predictive Analytics in Education",
            "authors": json.dumps([{"name": "Sarah Chen"}, {"name": "Michael Wang"}]),
            "summary": "This paper presents novel deep learning algorithms for predictive analytics in educational settings. We propose a transformer-based architecture for student performance forecasting and curriculum optimization. Our methods leverage attention mechanisms and recurrent modules to capture temporal learning patterns across analytics courses.",
            "categories": json.dumps(["cs.LG", "cs.AI"]),
            "primary_category": "cs.LG",
            "published": "2025-01-15T00:00:00Z",
            "updated": "2025-01-15T00:00:00Z",
        },
        {
            "id": "2025.10002",
            "title": "Advanced Analytics Methods for Algorithm Performance Benchmarking",
            "authors": json.dumps([{"name": "James Liu"}, {"name": "Emma Davis"}]),
            "summary": "We introduce advanced analytics methods for benchmarking algorithm performance across diverse computational tasks. The framework evaluates sorting algorithms, graph algorithms, and optimization routines using statistical analytics and automated testing pipelines.",
            "categories": json.dumps(["cs.DS", "cs.PF"]),
            "primary_category": "cs.DS",
            "published": "2025-02-01T00:00:00Z",
            "updated": "2025-02-01T00:00:00Z",
        },
        {
            "id": "2025.10003",
            "title": "Reinforcement Learning for Dynamic Resource Allocation",
            "authors": json.dumps([{"name": "Priya Patel"}, {"name": "Tom Brown"}]),
            "summary": "A reinforcement learning approach to dynamic resource allocation problems. We apply deep Q-networks and policy gradient methods to optimize scheduling and allocation in analytics-driven systems, demonstrating improvements over traditional algorithmic approaches.",
            "categories": json.dumps(["cs.AI", "cs.LG"]),
            "primary_category": "cs.AI",
            "published": "2025-02-20T00:00:00Z",
            "updated": "2025-02-20T00:00:00Z",
        },
        {
            "id": "2025.10004",
            "title": "Graph Neural Networks for Combinatorial Optimization",
            "authors": json.dumps([{"name": "Alex Kim"}, {"name": "Lisa Zhang"}]),
            "summary": "This work explores graph neural networks applied to combinatorial optimization problems including traveling salesman, graph coloring, and network flow algorithms. We show that learned heuristics can outperform classical algorithms on large-scale instances.",
            "categories": json.dumps(["cs.LG", "cs.DS"]),
            "primary_category": "cs.LG",
            "published": "2025-03-01T00:00:00Z",
            "updated": "2025-03-01T00:00:00Z",
        },
        # 2 noise papers
        {
            "id": "2025.20001",
            "title": "Marine Biodiversity Patterns in Arctic Ecosystems",
            "authors": json.dumps([{"name": "Hans Mueller"}]),
            "summary": "A comprehensive study of marine biodiversity distribution patterns in Arctic ecosystems under climate change scenarios. We analyze phytoplankton diversity and benthic community shifts using long-term monitoring data.",
            "categories": json.dumps(["q-bio.PE"]),
            "primary_category": "q-bio.PE",
            "published": "2025-01-10T00:00:00Z",
            "updated": "2025-01-10T00:00:00Z",
        },
        {
            "id": "2025.20002",
            "title": "Paleolithic Cave Art Dating Using Uranium-Thorium Methods",
            "authors": json.dumps([{"name": "Maria Garcia"}]),
            "summary": "New uranium-thorium dating results for paleolithic cave paintings in southwestern Europe. We establish a refined chronology for artistic development spanning 40000 years of prehistoric human expression.",
            "categories": json.dumps(["physics.geo-ph"]),
            "primary_category": "physics.geo-ph",
            "published": "2025-02-15T00:00:00Z",
            "updated": "2025-02-15T00:00:00Z",
        },
    ]

    for p in papers:
        cur.execute("""
            INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, published, updated, is_downloaded)
            VALUES (%(id)s, %(title)s, %(authors)s, %(summary)s, %(categories)s, %(primary_category)s, %(published)s, %(updated)s, false)
        """, p)
    print(f"[preprocess] Injected {len(papers)} arxiv papers.")


def inject_gcal_events(cur, launch_time):
    print("[preprocess] Injecting existing calendar events...")
    lt = datetime.strptime(launch_time or "2026-03-07 10:00:00", "%Y-%m-%d %H:%M:%S")
    def ts(days, hours, minutes=0):
        return (lt + timedelta(days=days, hours=hours - 10, minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S-05:00")
    # Add some existing events to make calendar look busy
    events = [
        {
            "id": str(uuid.uuid4()),
            "summary": "Department Staff Meeting",
            "description": "Weekly department meeting",
            "start_datetime": ts(3, 9),
            "end_datetime": ts(3, 10),
            "start_timezone": "America/New_York",
            "end_timezone": "America/New_York",
            "status": "confirmed",
        },
        {
            "id": str(uuid.uuid4()),
            "summary": "Faculty Senate Session",
            "description": "Monthly faculty senate",
            "start_datetime": ts(5, 14),
            "end_datetime": ts(5, 16),
            "start_timezone": "America/New_York",
            "end_timezone": "America/New_York",
            "status": "confirmed",
        },
        {
            "id": str(uuid.uuid4()),
            "summary": "Budget Review",
            "description": "Annual budget review session",
            "start_datetime": ts(11, 10),
            "end_datetime": ts(11, 12),
            "start_timezone": "America/New_York",
            "end_timezone": "America/New_York",
            "status": "confirmed",
        },
    ]
    for e in events:
        cur.execute("""
            INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, start_timezone, end_timezone, status)
            VALUES (%(id)s, %(summary)s, %(description)s, %(start_datetime)s, %(end_datetime)s, %(start_timezone)s, %(end_timezone)s, %(status)s)
        """, e)
    print(f"[preprocess] Injected {len(events)} calendar events.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_schemas(cur)
        inject_arxiv_papers(cur)
        inject_gcal_events(cur, args.launch_time)
        conn.commit()
        print("[preprocess] DB operations done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Curriculum_Modernization_Proposal.docx", "current_topics.json",
                        "topic_gaps.json", "extract_topics.py", "gap_analysis.py", "generate_summary.py"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
