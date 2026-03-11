"""Preprocess script for terminal-canvas-pdf-gsheet-email-word."""
import os
import argparse, json, os, sys, uuid
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
    # Clear gsheet
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.permissions")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    # Clear email
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
    conn.commit()
    cur.close()
    conn.close()
    print("[preprocess] Cleared gsheet and email schemas")


def inject_noise_data(launch_time):
    conn = get_conn()
    cur = conn.cursor()
    launch_dt = datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S")

    # Noise spreadsheet
    noise_id = str(uuid.uuid4())
    cur.execute("INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)",
                (noise_id, "Budget_Q1_2026"))
    cur.execute("INSERT INTO gsheet.sheets (spreadsheet_id, title, \"index\", row_count, column_count) VALUES (%s, %s, %s, %s, %s)",
                (noise_id, "Budget", 0, 5, 3))

    # Noise email
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    row = cur.fetchone()
    inbox_id = row[0] if row else 1
    cur.execute("""INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
        VALUES (%s, '<noise-canvas-001@univ.edu>', 'Campus Parking Update', 'facilities@university.edu', %s, %s, 'New parking regulations take effect next month.', true)""",
        (inbox_id, json.dumps(['faculty@university.edu']), launch_dt - timedelta(hours=4)))

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
