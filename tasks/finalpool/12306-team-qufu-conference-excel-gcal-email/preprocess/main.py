"""
Preprocess for 12306-team-qufu-conference-excel-gcal-email.

Injects:
- 1 gcal event: "Confucian Studies Conference" 2026-03-12 to 2026-03-15
- 2 emails: from beijing_team@uni.edu and shanghai_team@uni.edu asking about travel
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
    print("[preprocess] Cleared tables.")


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
            "Confucian Studies Conference",
            "Annual international conference on Confucian studies. Location: Qufu International Conference Center.",
            "2026-03-12 09:00:00",
            "2026-03-15 17:00:00",
            "Asia/Shanghai",
            "Asia/Shanghai",
        ))
    conn.commit()
    print("[preprocess] Injected GCal event: Confucian Studies Conference.")


def inject_emails(conn, folder_id):
    emails = [
        {
            "message_id": "msg-beijing-team-001",
            "subject": "Travel Arrangements to Qufu Conference - Beijing Team",
            "from_addr": "beijing_team@uni.edu",
            "to_addr": ["conference@confucius-institute.org"],
            "date": "2026-03-05 10:00:00+08",
            "body": (
                "Hello,\n\nWe are three team members from Beijing (Prof. Li, Dr. Wang, "
                "and Ms. Zhang) attending the Confucian Studies Conference in Qufu on "
                "March 12-15, 2026. Could you please arrange our travel from Beijing to "
                "Qufu on March 12? We would like to coordinate with the Shanghai team "
                "for a synchronized arrival. Please let us know the train details and "
                "schedule.\n\nThank you,\nBeijing Research Team"
            ),
        },
        {
            "message_id": "msg-shanghai-team-001",
            "subject": "Travel Arrangements to Qufu Conference - Shanghai Team",
            "from_addr": "shanghai_team@uni.edu",
            "to_addr": ["conference@confucius-institute.org"],
            "date": "2026-03-05 11:00:00+08",
            "body": (
                "Hi,\n\nWe are two team members from Shanghai (Prof. Chen and Dr. Liu) "
                "attending the Confucian Studies Conference in Qufu on March 12-15, 2026. "
                "We would like to coordinate our arrival with the Beijing team so we can "
                "share the ground transfer. Please help us plan our train journey from "
                "Shanghai to Qufu on March 12.\n\nBest,\nShanghai Research Team"
            ),
        },
    ]
    with conn.cursor() as cur:
        for e in emails:
            cur.execute("""
                INSERT INTO email.messages
                    (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
            """, (
                folder_id, e["message_id"], e["subject"], e["from_addr"],
                json.dumps(e["to_addr"]), e["date"], e["body"],
            ))
    conn.commit()
    print("[preprocess] Injected 2 emails from team members.")


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
        inject_emails(conn, folder_id)
    finally:
        conn.close()

    print("[preprocess] Preprocessing complete for 12306-team-qufu-conference-excel-gcal-email.")


if __name__ == "__main__":
    main()
