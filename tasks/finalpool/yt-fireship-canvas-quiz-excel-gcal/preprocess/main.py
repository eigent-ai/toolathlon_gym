"""
Preprocess for yt-fireship-canvas-quiz-excel-gcal task.

Clears email, gcal tables.
Injects 2 gcal events and 1 email from students@webdev.edu.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
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
        "summary": "Office Hours",
        "description": "Weekly office hours for Web Development course students.",
        "start": "2026-03-25 10:00:00+00",
        "end": "2026-03-25 11:00:00+00",
    },
    {
        "summary": "Department Meeting",
        "description": "Monthly department meeting for CS faculty.",
        "start": "2026-03-26 10:00:00+00",
        "end": "2026-03-26 11:00:00+00",
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared gcal and email tables.")


def inject_gcal_events(conn):
    with conn.cursor() as cur:
        for ev in GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime)
                VALUES (%s, %s, %s, %s)
            """, (ev["summary"], ev["description"], ev["start"], ev["end"]))
    conn.commit()
    print(f"[preprocess] Injected {len(GCAL_EVENTS)} calendar events.")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        conn.commit()
        return cur.fetchone()[0]


def inject_email(conn, folder_id):
    with conn.cursor() as cur:
        msg_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (
            folder_id,
            msg_id,
            "TypeScript Learning Resources Request",
            "students@webdev.edu",
            '["instructor@webdev.edu"]',
            "Hi Professor,\n\nSeveral students in the Web Development course have been "
            "asking about TypeScript resources. Could you put together a quiz based on "
            "some of the TypeScript tutorial videos you've been recommending? It would "
            "be great to have a structured quiz with a grade tracking spreadsheet and "
            "some quiz review sessions scheduled on the calendar.\n\n"
            "Please send us an announcement once the quiz is ready.\n\n"
            "Thanks,\nWebDev Student Council"
        ))
    conn.commit()
    print("[preprocess] Injected request email from students@webdev.edu.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal_events(conn)
        folder_id = ensure_email_folder(conn)
        inject_email(conn, folder_id)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
