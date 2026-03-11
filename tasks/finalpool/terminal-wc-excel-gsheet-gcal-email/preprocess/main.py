"""Preprocess for terminal-wc-excel-gsheet-gcal-email.
Clears gsheet, gcal, email. WooCommerce is read-only. Injects noise data."""
import argparse
import json
import os
import uuid
import glob as globmod
from datetime import datetime, timedelta

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    launch_dt = datetime.strptime(args.launch_time, "%Y-%m-%d %H:%M:%S") if args.launch_time else datetime(2026, 3, 7, 10, 0, 0)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear gsheet
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        print("[preprocess] Cleared gsheet data.")

        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
        print("[preprocess] Cleared gcal data.")

        # Clear email
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        print("[preprocess] Cleared email data.")

        # Inject noise gsheet data
        noise_ss_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gsheet.spreadsheets (id, title, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
        """, (noise_ss_id, "Old Sales Report"))
        cur.execute("""
            INSERT INTO gsheet.sheets (id, spreadsheet_id, title, index, row_count, column_count)
            VALUES (%s, %s, %s, 0, 10, 5)
        """, (1000, noise_ss_id, "Q3 Sales"))
        print("[preprocess] Injected noise gsheet data.")

        # Inject noise gcal event
        noise_start = (launch_dt - timedelta(days=2, hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
        noise_end = (launch_dt - timedelta(days=2, hours=-5)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status)
            VALUES (%s, %s, %s, %s, %s, 'confirmed')
        """, (str(uuid.uuid4()), "Team Standup", "Regular team standup meeting", noise_start, noise_end))
        print("[preprocess] Injected noise gcal data.")

        # Inject noise email
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM email.messages")
            max_id = cur.fetchone()[0] + 1
            cur.execute("""
                INSERT INTO email.messages (id, folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW(), %s, false)
            """, (max_id, folder_id, f"noise-{uuid.uuid4()}@company.com",
                  "Monthly Team Lunch", "hr@company.com",
                  json.dumps(["team@company.com"]),
                  "Please RSVP for the monthly team lunch."))
            print("[preprocess] Injected noise email data.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Inventory_Lifecycle_Report.xlsx", "demand_forecast.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
