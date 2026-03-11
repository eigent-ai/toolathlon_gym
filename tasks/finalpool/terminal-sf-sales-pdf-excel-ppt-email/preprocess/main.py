"""
Preprocess for terminal-sf-sales-pdf-excel-ppt-email task.

Clears email tables. Injects noise emails.
Snowflake is read-only.
"""
import argparse
import os
from datetime import datetime, timedelta

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
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            conn.rollback()
    conn.commit()
    print("[preprocess] Cleared email tables.")


def inject_noise_emails(conn, launch_dt):
    """Inject noise emails."""
    dt1 = (launch_dt + timedelta(days=-61)).strftime('%Y-%m-%d')
    dt2 = (launch_dt + timedelta(days=-58)).strftime('%Y-%m-%d')
    dt3 = (launch_dt + timedelta(days=-56)).strftime('%Y-%m-%d')
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            row = cur.fetchone()
            conn.commit()
        folder_id = row[0]
        cur.execute(f"""
            INSERT INTO email.messages (folder_id, subject, from_addr, to_addr, body_text, date)
            VALUES
            (%s, 'FY2024 Annual Report Draft', 'finance@company.com',
             '["board@company.com"]'::jsonb,
             'Please review the attached annual report draft by end of week.', '{dt1} 09:00:00'),
            (%s, 'New Product Launch Timeline', 'product@company.com',
             '["marketing@company.com"]'::jsonb,
             'The Q2 product launch is on track. Key milestones attached.', '{dt2} 14:00:00'),
            (%s, 'RE: Sales Team Retreat Planning', 'hr@company.com',
             '["regional_managers@company.com"]'::jsonb,
             'The retreat venue has been confirmed for April 15-17.', '{dt3} 11:30:00')
        """, (folder_id, folder_id, folder_id))
    conn.commit()
    print("[preprocess] Injected noise email data.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    launch_dt = datetime.strptime(args.launch_time, "%Y-%m-%d %H:%M:%S") if args.launch_time else datetime(2026, 3, 7)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_noise_emails(conn, launch_dt)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
