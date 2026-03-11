"""Preprocess script for terminal-sf-wc-support-email-gcal-excel."""
import os
import argparse, json, os, sys
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel"
}

TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_conn():
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)


def clear_writable_schemas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM email.attachments")
    try:
        cur.execute("DELETE FROM email.sent_log")
    except Exception:
        pass
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    cur.execute("DELETE FROM gcal.events")
    conn.commit()
    cur.close()
    conn.close()
    print("[preprocess] Cleared email and gcal schemas")


def inject_noise_data(launch_time):
    conn = get_conn()
    cur = conn.cursor()
    launch_dt = datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S")

    # Noise emails
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    row = cur.fetchone()
    inbox_id = row[0] if row else 1

    cur.execute("""INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
        VALUES (%s, '<noise-quality-001@co.com>', 'Office Renovation Update', 'facilities@company.com', %s, %s, 'The break room renovation will be completed by Friday.', true)""",
        (inbox_id, json.dumps(['staff@company.com']), launch_dt - timedelta(hours=5)))

    cur.execute("""INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
        VALUES (%s, '<noise-quality-002@co.com>', 'Team Lunch This Thursday', 'hr@company.com', %s, %s, 'Join us for the monthly team lunch at 12pm in the cafeteria.', true)""",
        (inbox_id, json.dumps(['all-staff@company.com']), launch_dt - timedelta(hours=2)))

    conn.commit()
    cur.close()
    conn.close()
    print("[preprocess] Noise data injected")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    clear_writable_schemas()
    inject_noise_data(args.launch_time)


if __name__ == "__main__":
    main()
