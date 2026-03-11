"""
Preprocess for terminal-yf-canvas-excel-gcal-email task.

Clears gcal and email tables. Injects conflicting calendar events and noise emails.
Canvas and Yahoo Finance are read-only.
"""
import argparse
import json
import os
import uuid
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
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            conn.rollback()
    conn.commit()
    print("[preprocess] Cleared gcal and email tables.")


def inject_calendar_conflicts(conn, launch_time):
    """Inject some calendar events that create conflicts on certain days."""
    base = datetime.fromisoformat(launch_time.replace("Z", "+00:00")) if launch_time else datetime.now()
    # Find the next Monday from base
    days_to_monday = (7 - base.weekday()) % 7
    if days_to_monday == 0 and base.hour >= 12:
        days_to_monday = 7
    monday = base + timedelta(days=days_to_monday)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    with conn.cursor() as cur:
        # Conflict on first Monday at 2pm (forces workshop 1 to Tuesday)
        conflict_start = monday.replace(hour=14, minute=0)
        conflict_end = monday.replace(hour=16, minute=0)
        cur.execute("""
            INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime,
                                     start_timezone, end_timezone, status)
            VALUES (%s, 'Faculty Senate Meeting', 'Monthly faculty senate meeting',
                    %s, %s, 'America/New_York', 'America/New_York', 'confirmed')
        """, (str(uuid.uuid4()), conflict_start.isoformat(), conflict_end.isoformat()))

        # Conflict on first Wednesday at 1:30pm (forces workshop 3 to Thursday)
        wed = monday + timedelta(days=2)
        conflict_start2 = wed.replace(hour=13, minute=30)
        conflict_end2 = wed.replace(hour=15, minute=0)
        cur.execute("""
            INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime,
                                     start_timezone, end_timezone, status)
            VALUES (%s, 'Department Budget Review', 'Quarterly budget review session',
                    %s, %s, 'America/New_York', 'America/New_York', 'confirmed')
        """, (str(uuid.uuid4()), conflict_start2.isoformat(), conflict_end2.isoformat()))

        # Non-conflicting event (morning, should not interfere)
        thu = monday + timedelta(days=3)
        cur.execute("""
            INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime,
                                     start_timezone, end_timezone, status)
            VALUES (%s, 'Office Hours', 'Regular morning office hours',
                    %s, %s, 'America/New_York', 'America/New_York', 'confirmed')
        """, (str(uuid.uuid4()),
              thu.replace(hour=9, minute=0).isoformat(),
              thu.replace(hour=11, minute=0).isoformat()))

        # Another non-conflicting event on second week
        next_mon = monday + timedelta(days=7)
        cur.execute("""
            INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime,
                                     start_timezone, end_timezone, status)
            VALUES (%s, 'Research Seminar', 'Weekly research seminar',
                    %s, %s, 'America/New_York', 'America/New_York', 'confirmed')
        """, (str(uuid.uuid4()),
              next_mon.replace(hour=10, minute=0).isoformat(),
              next_mon.replace(hour=12, minute=0).isoformat()))

    conn.commit()
    print(f"[preprocess] Injected calendar conflicts (Monday {monday.date()}, Wednesday {wed.date()}).")


def inject_noise_emails(conn):
    """Inject noise emails the agent should ignore."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            row = cur.fetchone()
            conn.commit()
        folder_id = row[0]

        # Ensure Sent folder exists
        cur.execute("SELECT id FROM email.folders WHERE name = 'Sent' LIMIT 1")
        sent_row = cur.fetchone()
        if not sent_row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('Sent') RETURNING id")
            sent_row = cur.fetchone()
            conn.commit()

        cur.execute("""
            INSERT INTO email.messages (folder_id, subject, from_addr, to_addr, body_text, date)
            VALUES
            (%s, 'Textbook Order Confirmation', 'bookstore@university.edu',
             '["prof.chen@university.edu"]'::jsonb,
             'Your order of 30 copies of Financial Markets by Mishkin has been confirmed.', '2026-02-28 09:00:00'),
            (%s, 'Spring Break Schedule', 'registrar@university.edu',
             '["all_faculty@university.edu"]'::jsonb,
             'Spring break will be from March 20 to March 28. All classes suspended.', '2026-03-01 10:00:00'),
            (%s, 'Parking Permit Renewal', 'parking@university.edu',
             '["prof.chen@university.edu"]'::jsonb,
             'Your parking permit expires on April 1. Please renew online.', '2026-03-02 08:30:00'),
            (%s, 'Research Grant Update', 'grants@university.edu',
             '["prof.chen@university.edu"]'::jsonb,
             'Your NSF proposal review is scheduled for next month.', '2026-03-03 14:00:00')
        """, (folder_id, folder_id, folder_id, folder_id))
    conn.commit()
    print("[preprocess] Injected noise email data.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    launch_time = args.launch_time or "2026-03-07T09:00:00"

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_calendar_conflicts(conn, launch_time)
        inject_noise_emails(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
