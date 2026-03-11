"""Preprocess for terminal-yf-sf-gsheet-word-gcal.
Clears gsheet and gcal schemas. Injects conflicting calendar events.
Snowflake and Yahoo Finance are read-only."""
import argparse
import json
import os
import glob as globmod
import uuid
import psycopg2
from datetime import datetime, timedelta

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
        cur.execute("DELETE FROM gsheet.spreadsheets")
        conn.commit()
        print("[preprocess] Cleared gsheet data.")

        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
        conn.commit()
        print("[preprocess] Cleared gcal data.")

        # Inject conflicting calendar events as offsets from launch_time
        lt = datetime.strptime(args.launch_time or "2026-03-07 10:00:00", "%Y-%m-%d %H:%M:%S")
        def ts(days, hours, minutes=0):
            return (lt + timedelta(days=days, hours=hours - 10, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S-05:00")
        conflict_events = [
            {
                "summary": "Sales Pipeline Review",
                "description": "Weekly pipeline review with sales leadership",
                "start": ts(2, 9),
                "end": ts(2, 10, 30),
            },
            {
                "summary": "All-Hands Meeting",
                "description": "Monthly company all-hands",
                "start": ts(2, 14),
                "end": ts(2, 15, 30),
            },
            {
                "summary": "Product Roadmap Planning",
                "description": "Q2 product roadmap discussion",
                "start": ts(3, 9),
                "end": ts(3, 11),
            },
            {
                "summary": "Lunch with Client - Acme Corp",
                "description": "Client lunch meeting",
                "start": ts(3, 12),
                "end": ts(3, 13, 30),
            },
            {
                "summary": "Engineering Standup",
                "description": "Cross-team standup",
                "start": ts(4, 9),
                "end": ts(4, 9, 30),
            },
            {
                "summary": "Budget Review - Finance",
                "description": "Quarterly budget review with finance team",
                "start": ts(4, 10),
                "end": ts(4, 12),
            },
            {
                "summary": "HR Policy Update Session",
                "description": "Updated HR policies walkthrough",
                "start": ts(4, 13),
                "end": ts(4, 14),
            },
            {
                "summary": "Customer Success Check-in",
                "description": "Weekly CS team sync",
                "start": ts(5, 9),
                "end": ts(5, 10),
            },
            {
                "summary": "Board Prep Meeting",
                "description": "Prepare materials for board meeting",
                "start": ts(5, 14),
                "end": ts(5, 16),
            },
            {
                "summary": "Team Building Workshop",
                "description": "Quarterly team building activity",
                "start": ts(6, 9),
                "end": ts(6, 12),
            },
            {
                "summary": "Sprint Retrospective",
                "description": "End of sprint retro",
                "start": ts(6, 14),
                "end": ts(6, 15),
            },
        ]

        for evt in conflict_events:
            cur.execute(
                """INSERT INTO gcal.events (summary, description, start_datetime, end_datetime,
                   start_timezone, end_timezone, status)
                   VALUES (%s, %s, %s, %s, 'America/New_York', 'America/New_York', 'confirmed')""",
                (evt["summary"], evt["description"], evt["start"], evt["end"]))

        conn.commit()
        print(f"[preprocess] Injected {len(conflict_events)} calendar events.")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up any previous outputs in agent workspace
    if args.agent_workspace:
        for pattern in ["Compensation_Review_Memo.docx", "compute_bonuses.py",
                        "market_adjustment.py", "validate_bonuses.py",
                        "current_bonuses.json", "market_adjusted_bonuses.json"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
