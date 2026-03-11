"""
Preprocess for yt-transcript-notion-song-report-gcal-email task.

Injects:
  - 1 email from editorial@musicblog.com asking for analysis report
  - 2 gcal events: Monthly Editorial Meeting and Content Planning Session
  - Clears email, gcal, notion tables before injecting

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
import json
import os
import uuid
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
        "summary": "Monthly Editorial Meeting",
        "description": "Monthly all-hands editorial team meeting. Agenda: content pipeline review, Q2 planning.",
        "start": "2026-03-10 14:00:00",
        "end": "2026-03-10 15:00:00",
    },
    {
        "summary": "Content Planning Session",
        "description": "Quarterly content planning session. Topics: upcoming features, artist collaborations, social strategy.",
        "start": "2026-03-16 10:00:00",
        "end": "2026-03-16 11:00:00",
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared gcal, notion, email tables.")


def inject_gcal_events(conn):
    with conn.cursor() as cur:
        for ev in GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime,
                    start_timezone, end_timezone, creator, organizer, attendees)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
            """, (
                ev["summary"], ev["description"], ev["start"], ev["end"],
                "Asia/Shanghai", "Asia/Shanghai",
                json.dumps({}), json.dumps({}), json.dumps([]),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(GCAL_EVENTS)} GCal events.")


def inject_emails(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()
            row = cur.fetchone()
        folder_id = row[0]

        email_data = {
            "message_id": "msg-editorial-001",
            "subject": "Afrobeat Mix Analysis - Status Update Needed",
            "from_addr": "editorial@musicblog.com",
            "to_addr": json.dumps(["editor@afrobeatstoday.com"]),
            "date": "2026-03-07 09:00:00+00",
            "body_text": (
                "Hi,\n\n"
                "We need the full analysis report for the Afrobeat mix video (7ZQzGq32kAY) by end of week. "
                "Please include the tracklist, artist breakdown, and the publication schedule for the three planned articles. "
                "Make sure the report is ready for the editorial meeting on March 10.\n\n"
                "Best,\nEditorial Team\neditorial@musicblog.com"
            ),
            "folder_id": folder_id,
        }
        cur.execute("""
            INSERT INTO email.messages (message_id, subject, from_addr, to_addr, date, body_text, folder_id)
            VALUES (%(message_id)s, %(subject)s, %(from_addr)s, %(to_addr)s::jsonb,
                    %(date)s, %(body_text)s, %(folder_id)s)
            ON CONFLICT (message_id) DO NOTHING
        """, email_data)
    conn.commit()
    print("[preprocess] Injected editorial request email.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal_events(conn)
        inject_emails(conn)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
