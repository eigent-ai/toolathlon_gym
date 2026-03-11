"""
Preprocess for terminal-sf-wc-support-gsheet-word-email task.

Clears Google Sheet and email tables. Injects noise data.
Snowflake and WooCommerce are read-only; no injection needed.
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
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.permissions")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            conn.rollback()
    conn.commit()
    print("[preprocess] Cleared gsheet and email tables.")


def inject_noise_gsheet(conn):
    """Inject noise Google Sheet data that the agent should ignore."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gsheet.spreadsheets (id, title) VALUES ('noise_ss_001', 'Old Sales Report Q4')
        """)
        cur.execute("""
            INSERT INTO gsheet.sheets (spreadsheet_id, title, "index")
            VALUES ('noise_ss_001', 'Revenue', 0)
            RETURNING id
        """)
        sheet_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value)
            VALUES ('noise_ss_001', %s, 1, 1, 'Region'),
                   ('noise_ss_001', %s, 1, 2, 'Revenue'),
                   ('noise_ss_001', %s, 2, 1, 'North'),
                   ('noise_ss_001', %s, 2, 2, '120000')
        """, (sheet_id, sheet_id, sheet_id, sheet_id))
    conn.commit()
    print("[preprocess] Injected noise Google Sheet data.")


def inject_noise_emails(conn, launch_dt):
    """Inject noise emails that the agent should ignore."""
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
        d3 = (launch_dt - timedelta(days=51)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(f"""
            INSERT INTO email.messages (folder_id, subject, from_addr, to_addr, body_text, date)
            VALUES
            (%s, 'Weekly Team Standup Notes', 'manager@company.com',
             '["team@company.com"]'::jsonb,
             'Please review the standup notes for this week.', '{d1}'),
            (%s, 'Office Supply Order Confirmation', 'supplies@vendor.com',
             '["admin@company.com"]'::jsonb,
             'Your order for office supplies has been confirmed.', '{d2}'),
            (%s, 'RE: Customer Feedback Survey', 'analytics@company.com',
             '["cs_leadership@company.com"]'::jsonb,
             'The Q4 customer feedback survey results are attached.', '{d3}')
        """, (folder_id, folder_id, folder_id))
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
        inject_noise_gsheet(conn)
        inject_noise_emails(conn, launch_dt)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
