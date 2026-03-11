"""Preprocess for terminal-howtocook-pdf-excel-word-gcal.
HowToCook is MCP-only (no DB). Clear gcal and inject noise events."""
import argparse
import glob
import json
import os
from datetime import datetime, timedelta

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_gcal(cur):
    print("[preprocess] Clearing Google Calendar events...")
    cur.execute("DELETE FROM gcal.events")


def inject_noise(cur, launch_time):
    print("[preprocess] Injecting noise calendar events...")
    launch_dt = datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S")

    noise_events = [
        ("Weekly Team Standup", launch_dt.replace(hour=9, minute=0),
         launch_dt.replace(hour=9, minute=30), "Regular team meeting"),
        ("Budget Review Meeting", (launch_dt + timedelta(days=1)).replace(hour=14, minute=0),
         (launch_dt + timedelta(days=1)).replace(hour=15, minute=0), "Q1 budget review"),
        ("Facilities Maintenance", (launch_dt + timedelta(days=2)).replace(hour=8, minute=0),
         (launch_dt + timedelta(days=2)).replace(hour=12, minute=0), "Building maintenance check"),
    ]

    for summary, start, end, desc in noise_events:
        cur.execute("""
            INSERT INTO gcal.events (summary, start_datetime, end_datetime, description, status)
            VALUES (%s, %s, %s, %s, 'confirmed')
        """, (summary, start, end, desc))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_gcal(cur)
        inject_noise(cur, args.launch_time)
        conn.commit()
        print("[preprocess] DB setup done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Campus_Dining_Plan.xlsx", "Meal_Plan_Report.docx",
                        "budget_*.py", "budget_*.json", "selected_*.json"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
