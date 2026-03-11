"""Preprocess for sf-hr-talent-review-excel-word-gcal-email.

Clears writable schemas (gcal, email) used by this task.
Snowflake data is read-only and pre-populated.
PDF and groundtruth files are pre-generated static assets.
"""
import argparse
import os
import json
import shutil
from datetime import datetime, timedelta

import psycopg2

DB = dict(
    host=os.environ.get("PGHOST", "localhost"), port=5432,
    dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
    user="eigent", password="camel"
)


def clear_and_inject(launch_time_str):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Clear writable schemas used by this task
    # Email: child tables first
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.drafts")
    cur.execute("DELETE FROM email.messages")

    # Ensure INBOX folder exists
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    inbox = cur.fetchone()
    if not inbox:
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        inbox = cur.fetchone()
    cur.execute("SELECT id FROM email.folders WHERE name = 'Sent' LIMIT 1")
    sent = cur.fetchone()
    if not sent:
        cur.execute("INSERT INTO email.folders (name) VALUES ('Sent') RETURNING id")

    # GCal: clear events
    cur.execute("DELETE FROM gcal.events")

    # Inject a noise email to make inbox non-empty
    inbox_id_query = "(SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1)"
    cur.execute(f"""
        INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
        VALUES (
            {inbox_id_query},
            '<noise-001@company.com>',
            'Office Renovation Schedule',
            'facilities@company.com',
            '["hr_leadership@company.com"]'::jsonb,
            %s,
            'Please note the office renovation will begin next month on the 3rd floor.',
            true
        )
    """, (launch_time_str,))

    # Inject noise calendar events
    if launch_time_str:
        launch_dt = datetime.strptime(launch_time_str, "%Y-%m-%d %H:%M:%S")
    else:
        launch_dt = datetime(2026, 3, 7, 10, 0, 0)

    cur.execute("""
        INSERT INTO gcal.events (summary, description, start_datetime, start_timezone, end_datetime, end_timezone,
                                 creator, organizer, attendees)
        VALUES (%s, %s, %s, 'UTC', %s, 'UTC', '{}'::jsonb, '{}'::jsonb, '[]'::jsonb)
    """, (
        "Weekly All-Hands Meeting",
        "Regular company-wide standup",
        (launch_dt + timedelta(days=7)).strftime("%Y-%m-%d 14:00:00+00"),
        (launch_dt + timedelta(days=7)).strftime("%Y-%m-%d 15:00:00+00"),
    ))

    conn.commit()
    cur.close()
    conn.close()
    print("Preprocess complete: cleared email/gcal, injected noise data.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    clear_and_inject(args.launch_time)

    # Copy initial_workspace files to agent_workspace if specified
    if args.agent_workspace:
        initial_ws = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "initial_workspace")
        if os.path.isdir(initial_ws):
            for f in os.listdir(initial_ws):
                src = os.path.join(initial_ws, f)
                if os.path.isfile(src) and not f.startswith("."):
                    shutil.copy2(src, os.path.join(args.agent_workspace, f))
            print(f"Copied initial_workspace files to {args.agent_workspace}")


if __name__ == "__main__":
    main()
