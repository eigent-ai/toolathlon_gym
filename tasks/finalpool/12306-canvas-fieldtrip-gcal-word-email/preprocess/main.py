"""
Preprocess for 12306-canvas-fieldtrip-gcal-word-email.

Injects:
- 1 gcal event: "Regular Class - Cultural Heritage" 2026-03-12 09:00-11:00
- 1 email from students@university.edu requesting field trip info
- Clears email, gcal tables (Canvas is read-only)
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
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared email and gcal tables.")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        fid = cur.fetchone()[0]
    conn.commit()
    return fid


def inject_gcal(conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gcal.events (summary, description, start_datetime, end_datetime,
                start_timezone, end_timezone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "Regular Class - Cultural Heritage",
            "Weekly lecture for Cultural Heritage Studies course. March 12 session.",
            "2026-03-12 09:00:00",
            "2026-03-12 11:00:00",
            "Asia/Shanghai",
            "Asia/Shanghai",
        ))
    conn.commit()
    print("[preprocess] Injected GCal event: Regular Class - Cultural Heritage.")


def inject_email(conn, folder_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
        """, (
            folder_id,
            "msg-students-001",
            "Inquiry About Qufu Field Trip - Cultural Heritage Studies",
            "students@university.edu",
            json.dumps(["professor@university.edu"]),
            "2026-03-06 14:00:00+08",
            (
                "Dear Professor,\n\nWe heard that you are planning a field trip to Qufu "
                "for our Cultural Heritage Studies course. We are very excited about this "
                "opportunity to visit the Confucius Temple and Kong Family Mansion. Could "
                "you please send us the official field trip notice with all the travel "
                "details, including the train schedule, costs, and what we need to bring? "
                "We would appreciate receiving this as soon as possible so we can make "
                "arrangements.\n\nThank you,\nStudents of Cultural Heritage Studies"
            ),
        ))
    conn.commit()
    print("[preprocess] Injected email from students@university.edu.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal(conn)
        folder_id = ensure_email_folder(conn)
        inject_email(conn, folder_id)
    finally:
        conn.close()

    print("[preprocess] Preprocessing complete for 12306-canvas-fieldtrip-gcal-word-email.")


if __name__ == "__main__":
    main()
