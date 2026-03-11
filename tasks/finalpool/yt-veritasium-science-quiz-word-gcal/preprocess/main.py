"""
Preprocess for yt-veritasium-science-quiz-word-gcal task.

- Clears gcal, email, gsheet tables
- Injects 2 gcal events as noise/conflict
- Injects 1 email from professor asking for quiz status
"""
import argparse
import json
import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
        try:
            cur.execute("DELETE FROM email.attachments")
        except Exception:
            pass
        try:
            cur.execute("DELETE FROM email.sent_log")
        except Exception:
            pass
        cur.execute("DELETE FROM email.messages")
        # Clear gsheet
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
    conn.commit()
    print("[preprocess] Cleared gcal.events, email.messages, gsheet tables")


def inject_gcal_events(conn):
    events = [
        {
            "summary": "Team Meeting",
            "description": "Weekly team standup.",
            "start": "2026-03-14 09:00:00+00",
            "end": "2026-03-14 10:00:00+00",
        },
        {
            "summary": "Conference",
            "description": "Annual science conference - Day 1.",
            "start": "2026-03-21 11:00:00+00",
            "end": "2026-03-21 13:00:00+00",
        },
    ]
    with conn.cursor() as cur:
        for ev in events:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime, start_timezone, end_timezone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (ev["summary"], ev["description"], ev["start"], ev["end"], "UTC", "UTC"))
    conn.commit()
    print("[preprocess] Injected 2 gcal noise events (Team Meeting, Conference)")


def inject_email(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
        else:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            folder_id = cur.fetchone()[0]
            conn.commit()

        cur.execute("""
            INSERT INTO email.messages (folder_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s)
        """, (
            folder_id,
            "Quiz Preparation Status - Veritasium",
            "professor@university.edu",
            json.dumps(["educator@university.edu"]),
            "2026-03-06 08:30:00+00",
            "Hi, I wanted to check on the status of the science quiz preparation based on the Veritasium videos. Could you please let me know when the quiz document will be ready and if you have scheduled study sessions for the group? The students are eager to get started. Thanks!",
        ))
    conn.commit()
    print("[preprocess] Injected professor email asking for quiz status")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal_events(conn)
        inject_email(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
