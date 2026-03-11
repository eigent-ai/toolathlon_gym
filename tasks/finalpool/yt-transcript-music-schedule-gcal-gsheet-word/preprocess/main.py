"""
Preprocess for yt-transcript-music-schedule-gcal-gsheet-word task.

Clears gcal, gsheet, email tables.
Injects 2 gcal events (studio conflicts) and 1 email from station@radioafrica.fm.

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
        "summary": "Studio Recording",
        "description": "Live recording session - studio fully booked.",
        "start": "2026-04-06 14:00:00+00",
        "end": "2026-04-06 18:00:00+00",
    },
    {
        "summary": "Tech Maintenance",
        "description": "Equipment maintenance check.",
        "start": "2026-04-13 09:00:00+00",
        "end": "2026-04-13 11:00:00+00",
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared gcal, gsheet, email tables.")


def inject_gcal_events(conn):
    with conn.cursor() as cur:
        for ev in GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime)
                VALUES (%s, %s, %s, %s)
            """, (ev["summary"], ev["description"], ev["start"], ev["end"]))
    conn.commit()
    print(f"[preprocess] Injected {len(GCAL_EVENTS)} studio calendar events.")


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
            "April 2026 Afrobeat Show - Schedule Needed",
            "station@radioafrica.fm",
            '["dj@radioshow.com"]',
            "Hey,\n\nWe need to finalize the schedule for the Afrobeat Sunday Show "
            "running through April 2026. Please analyze the Afrobeat Mix 2024 video "
            "(ID: 7ZQzGq32kAY) to build the playlist, create the broadcast schedule "
            "spreadsheet with Playlist and Show_Schedule sheets, book the four Sunday "
            "evening show slots on the calendar, and send me a radio show script "
            "document (Radio_Show_Script.docx).\n\n"
            "Reply once everything is set up.\n\nThanks,\nRadio Africa FM"
        ))
    conn.commit()
    print("[preprocess] Injected request email from station@radioafrica.fm.")


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
