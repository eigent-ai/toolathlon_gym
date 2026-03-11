"""
Preprocess for terminal-yf-excel-word-gform-email task.

Clears gform and email tables. Injects noise data.
Yahoo Finance is read-only.
"""
import argparse
import json
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
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            conn.rollback()
    conn.commit()
    print("[preprocess] Cleared gform and email tables.")


def inject_noise_gform(conn):
    """Inject noise form data the agent should ignore."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gform.forms (id, title, document_title, description)
            VALUES ('noise_form_001', 'Office Supplies Request Form',
                    'Office Supplies Request Form',
                    'Use this form to request office supplies.')
        """)
        cur.execute("""
            INSERT INTO gform.questions (id, form_id, item_id, title, question_type, required, config, position)
            VALUES ('noise_q_001', 'noise_form_001', 'noise_item_001',
                    'What supplies do you need?', 'PARAGRAPH', true, '{}'::jsonb, 0)
        """)
    conn.commit()
    print("[preprocess] Injected noise gform data.")


def inject_noise_emails(conn, launch_dt):
    """Inject noise emails."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            row = cur.fetchone()
            conn.commit()
        folder_id = row[0]
        d1 = (launch_dt - timedelta(days=56)).strftime("%Y-%m-%d %H:%M:%S")
        d2 = (launch_dt - timedelta(days=54)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(f"""
            INSERT INTO email.messages (folder_id, subject, from_addr, to_addr, body_text, date)
            VALUES
            (%s, 'Market Update: Weekly Summary', 'market_updates@broker.com',
             '["portfolio_team@company.com"]'::jsonb,
             'Markets were mixed this week with tech leading gains.', '{d1}'),
            (%s, 'Board Meeting Reminder', 'admin@company.com',
             '["board@company.com"]'::jsonb,
             'Reminder: Quarterly board meeting next Tuesday at 2pm.', '{d2}')
        """, (folder_id, folder_id))
    conn.commit()
    print("[preprocess] Injected noise email data.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    launch_dt = datetime.strptime(args.launch_time, "%Y-%m-%d %H:%M:%S") if args.launch_time else datetime(2026, 3, 7, 10, 0, 0)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_noise_gform(conn)
        inject_noise_emails(conn, launch_dt)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
