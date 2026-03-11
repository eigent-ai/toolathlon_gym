"""Preprocess script for sf-support-coaching-plan-excel-notion-gcal.
Clears writable schemas (notion, gcal) and injects noise data.
Copies initial_workspace files to agent workspace.
"""
import argparse
import os
import shutil
import uuid
from datetime import datetime

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def clear_schemas(conn):
    cur = conn.cursor()
    # Clear notion
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    # Clear gcal
    cur.execute("DELETE FROM gcal.events")
    conn.commit()
    cur.close()
    print("[preprocess] Cleared notion and gcal schemas.")


def inject_noise(conn):
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Noise Notion pages (standalone, not in any database)
    for title in ["Team Standup Notes", "Q1 OKR Tracker", "Holiday Schedule 2026"]:
        page_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.pages (id, object, created_time, last_edited_time,
                created_by, last_edited_by, cover, icon, parent, archived, in_trash,
                properties, url, public_url)
            VALUES (%s, 'page', %s, %s, '{}', '{}', NULL, NULL,
                '{"type": "workspace", "workspace": true}',
                false, false, %s, %s, NULL)
        """, (
            page_id, now, now,
            f'{{"title": {{"id": "title", "type": "title", "title": [{{"type": "text", "text": {{"content": "{title}"}}}}]}}}}',
            f"https://www.notion.so/{page_id.replace('-', '')}",
        ))
    print("[preprocess] Injected 3 noise Notion pages.")

    # Noise GCal events
    noise_events = [
        ("Weekly Team Sync", "2026-03-10 09:00:00", "2026-03-10 09:30:00"),
        ("Product Demo", "2026-03-12 14:00:00", "2026-03-12 15:00:00"),
        ("All Hands Meeting", "2026-03-13 16:00:00", "2026-03-13 17:00:00"),
    ]
    for summary, start, end in noise_events:
        cur.execute("""
            INSERT INTO gcal.events (summary, description, start_datetime, end_datetime, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (summary, "Regular team meeting", start, end, "confirmed"))
    print("[preprocess] Injected 3 noise GCal events.")

    conn.commit()
    cur.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    try:
        clear_schemas(conn)
        inject_noise(conn)
    finally:
        conn.close()

    # Copy initial_workspace files to agent workspace
    if args.agent_workspace and os.path.exists(args.agent_workspace):
        initial_ws = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "initial_workspace")
        if os.path.exists(initial_ws):
            for f in os.listdir(initial_ws):
                src = os.path.join(initial_ws, f)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(args.agent_workspace, f))
                    print(f"[preprocess] Copied {f} to agent workspace.")

    # Remove any previously created output files from agent workspace
    if args.agent_workspace:
        for fname in ["Agent_Scorecard.xlsx"]:
            path = os.path.join(args.agent_workspace, fname)
            if os.path.exists(path):
                os.remove(path)
                print(f"[preprocess] Removed old {fname}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
