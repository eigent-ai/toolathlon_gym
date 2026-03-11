"""Preprocess for terminal-canvas-notion-study-gcal-excel.
Clears notion and gcal writable schemas. Canvas is read-only."""
import argparse
import json
import os
import glob as globmod
import uuid
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        cur.execute("DELETE FROM gcal.events")
        conn.commit()
        print("[preprocess] Cleared notion and gcal data.")

        # Inject notion noise
        page_id = str(uuid.uuid4())
        props = {"title": {"title": [{"type": "text", "text": {"content": "Unrelated Meeting Notes"}, "plain_text": "Unrelated Meeting Notes"}]}}
        cur.execute("INSERT INTO notion.pages (id, properties) VALUES (%s, %s::jsonb)", (page_id, json.dumps(props)))
        bid = str(uuid.uuid4())
        cur.execute("INSERT INTO notion.blocks (id, parent_type, parent_id, type, block_data, position) VALUES (%s, %s, %s, %s, %s::jsonb, %s)",
            (bid, "page_id", page_id, "paragraph", json.dumps({"rich_text": [{"type": "text", "text": {"content": "Unrelated content about office supplies"}, "plain_text": "Unrelated content about office supplies"}]}), 0))

        # Inject gcal noise
        cur.execute("INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status) VALUES (%s, %s, %s, %s, %s, 'confirmed')",
            (str(uuid.uuid4()), "Team Standup", "Regular standup meeting", "2026-03-05 09:00:00", "2026-03-05 09:30:00"))
        cur.execute("INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status) VALUES (%s, %s, %s, %s, %s, 'confirmed')",
            (str(uuid.uuid4()), "Lunch Break Yoga", "Wellness activity", "2026-03-06 12:00:00", "2026-03-06 12:45:00"))
        conn.commit()
        print("[preprocess] Injected noise data.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Study_Plan_Report.xlsx", "study_planner.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
