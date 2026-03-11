"""
Preprocess for 12306-beijing-shanghai-trip-notion-gcal-word.

Injects:
- 1 gcal event: "Client Meeting in Shanghai" on 2026-03-10 14:00-16:00
- 1 email from travel@consulting.com requesting booking assistance
- Clears email, gcal, notion tables
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
        cur.execute("DELETE FROM notion.pages")
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
    print("[preprocess] Cleared gcal, notion, email tables.")


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
            "Client Meeting in Shanghai",
            "Important client strategy meeting at Shanghai office. Please arrange travel.",
            "2026-03-10 14:00:00",
            "2026-03-10 16:00:00",
            "Asia/Shanghai",
            "Asia/Shanghai",
        ))
    conn.commit()
    print("[preprocess] Injected GCal event: Client Meeting in Shanghai.")


def inject_email(conn, folder_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
        """, (
            folder_id,
            "msg-travel-001",
            "Travel Booking Assistance Needed - Beijing to Shanghai March 10",
            "travel@consulting.com",
            json.dumps(["consultant@company.com"]),
            "2026-03-07 09:00:00+08",
            (
                "Hi,\n\nWe have an important client meeting in Shanghai on March 10, 2026 "
                "from 14:00 to 16:00. Please help book a round-trip high-speed train "
                "from Beijing to Shanghai and back on the same day. We prefer second-class "
                "seats and need to arrive in Shanghai before the meeting starts. "
                "Please prepare a formal travel plan document.\n\nBest regards,\n"
                "Travel Department\ntravel@consulting.com"
            ),
        ))
    conn.commit()
    print("[preprocess] Injected email from travel@consulting.com.")


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

    print("[preprocess] Preprocessing complete for 12306-beijing-shanghai-trip-notion-gcal-word.")


if __name__ == "__main__":
    main()
