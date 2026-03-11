"""
Preprocess for 12306-sf-hr-training-travel-excel-email-gcal.

Injects:
- 1 gcal event: "Training Program Kickoff" 2026-03-10 15:00-17:00 in Shanghai
- 1 email from training@hr-dept.com requesting travel planning
- Clears email, gcal tables (NOT snowflake - read-only)
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
                start_timezone, end_timezone, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            "Training Program Kickoff",
            "Corporate training program kickoff session for Sales and Marketing staff.",
            "2026-03-10 15:00:00",
            "2026-03-10 17:00:00",
            "Asia/Shanghai",
            "Asia/Shanghai",
            "Shanghai Training Center, 100 Nanjing Road",
        ))
    conn.commit()
    print("[preprocess] Injected GCal event: Training Program Kickoff.")


def inject_email(conn, folder_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
        """, (
            folder_id,
            "msg-training-hr-001",
            "Travel Planning Request - Shanghai Training March 10",
            "training@hr-dept.com",
            json.dumps(["hrmanager@company.com"]),
            "2026-03-06 09:00:00+08",
            (
                "Hi HR Manager,\n\nWe need to organize rail travel for our Sales and "
                "Marketing team members who will attend the corporate training program "
                "in Shanghai on March 10, 2026. The training kickoff starts at 15:00. "
                "Please identify eligible employees (Sales or Marketing department, at "
                "least 3 years of experience, up to 5 people) and arrange their train "
                "travel from Beijing to Shanghai and back. We need a full travel report "
                "with budget breakdown in Excel format.\n\nThanks,\nTraining Department"
            ),
        ))
    conn.commit()
    print("[preprocess] Injected email from training@hr-dept.com.")


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

    print("[preprocess] Preprocessing complete for 12306-sf-hr-training-travel-excel-email-gcal.")


if __name__ == "__main__":
    main()
