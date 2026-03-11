"""
Preprocess for yt-veritasium-howtocook-wellness-excel-gcal task.

Clears gcal tables.
Injects 2 gcal events (conflicting with Wednesday morning wellness slots).

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

GCAL_EVENTS = [
    {
        "summary": "Morning Yoga",
        "description": "Weekly morning yoga class - external booking.",
        "start": "2026-04-01 07:00:00+00",
        "end": "2026-04-01 07:30:00+00",
    },
    {
        "summary": "Team Standup",
        "description": "Wellness team morning standup meeting.",
        "start": "2026-04-08 07:00:00+00",
        "end": "2026-04-08 07:30:00+00",
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
    conn.commit()
    print("[preprocess] Cleared gcal events table.")


def inject_gcal_events(conn):
    with conn.cursor() as cur:
        for ev in GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime)
                VALUES (%s, %s, %s, %s)
            """, (ev["summary"], ev["description"], ev["start"], ev["end"]))
    conn.commit()
    print(f"[preprocess] Injected {len(GCAL_EVENTS)} calendar events.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal_events(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
