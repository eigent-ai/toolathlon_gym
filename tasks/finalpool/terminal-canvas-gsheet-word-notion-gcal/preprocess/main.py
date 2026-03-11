"""Preprocess for terminal-canvas-gsheet-word-notion-gcal.
Clears gsheet, notion, gcal. Injects noise. Canvas is read-only."""
import argparse
import glob as globmod
import json
import os
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
        # Clear gsheet
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.permissions")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        conn.commit()
        print("[preprocess] Cleared gsheet data.")

        # Clear notion
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        conn.commit()
        print("[preprocess] Cleared notion data.")

        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
        conn.commit()
        print("[preprocess] Cleared gcal events.")

        # Inject noise gcal events
        noise_events = [
            ("Department Meeting", "2026-03-16 08:00:00", "2026-03-16 09:00:00", "Weekly department meeting"),
            ("Curriculum Committee", "2026-03-18 16:00:00", "2026-03-18 17:00:00", "Quarterly curriculum review"),
        ]
        for summary, start, end, desc in noise_events:
            cur.execute("""
                INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status)
                VALUES (%s, %s, %s, %s, %s, 'confirmed')
            """, (str(uuid.uuid4()), summary, desc, start, end))

        # Inject noise notion database
        noise_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.databases (id, title, description, properties, parent, created_time, last_edited_time)
            VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, NOW(), NOW())
        """, (noise_db_id,
              json.dumps([{"type": "text", "text": {"content": "Meeting Notes Archive"}}]),
              json.dumps([{"type": "text", "text": {"content": "Archive of meeting notes"}}]),
              json.dumps({"Title": {"type": "title", "title": {}}}),
              json.dumps({"type": "workspace", "workspace": True})))

        # Inject noise gsheet
        noise_ss_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gsheet.spreadsheets (id, title, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
        """, (noise_ss_id, "Budget Tracking 2025"))

        conn.commit()
        print("[preprocess] Injected noise data.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up agent workspace
    if args.agent_workspace:
        for pattern in ["Academic_Advising_Report.xlsx", "Advising_Recommendations.docx", "advising_analyzer.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
