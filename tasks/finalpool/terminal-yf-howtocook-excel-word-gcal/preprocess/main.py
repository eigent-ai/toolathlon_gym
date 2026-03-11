"""
Preprocess for terminal-yf-howtocook-excel-word-gcal task.

Clears Google Calendar. Injects existing calendar events (some conflicting
with target Wednesdays) plus noise events. YF and HowToCook are read-only.
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
        cur.execute("DELETE FROM gcal.events")
    conn.commit()
    print("[preprocess] Cleared gcal events.")


def inject_calendar_events(conn, launch):
    """Inject existing calendar events. Two conflict with target Wednesdays,
    plus noise events on other days. All dates are offsets from launch_time."""

    def dt(days, hours, minutes=0):
        return (launch + timedelta(days=days, hours=hours, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")

    # Offsets computed from launch_time default "2026-03-07 10:00:00"
    events = [
        # Conflict: launch+11d1h = Wed March 18 11:00 (forces session 1 to Thu March 19)
        ('All-Hands Company Meeting', dt(11, 1), dt(11, 3),
         'Quarterly all-hands meeting for all employees', 'Main Auditorium'),
        # Conflict: launch+25d0h = Wed April 1 10:00 (forces session 3 to Thu April 2)
        ('Q1 Budget Review', dt(25, 0), dt(25, 4),
         'End of quarter budget review with finance team', 'Board Room'),
        # Noise: Mon March 17 09:00 = launch+9d23h
        ('Team Standup', dt(9, 23), dt(9, 23, 30),
         'Daily standup meeting', 'Room 201'),
        # Noise: Fri March 20 10:00 = launch+13d0h
        ('HR Orientation', dt(13, 0), dt(13, 2),
         'New employee orientation session', 'Room 105'),
        # Noise: Tue March 24 14:00 = launch+17d4h
        ('Sales Training', dt(17, 4), dt(17, 6),
         'Monthly sales training workshop', 'Room 302'),
        # Noise: Sun April 5 22:00 = launch+29d12h
        ('IT Maintenance Window', dt(29, 12), dt(29, 16),
         'Scheduled server maintenance', 'Data Center'),
    ]

    with conn.cursor() as cur:
        for summary, start, end, desc, loc in events:
            cur.execute(
                "INSERT INTO gcal.events (summary, start_datetime, end_datetime, description, location) "
                "VALUES (%s, %s, %s, %s, %s)",
                (summary, start, end, desc, loc),
            )
    conn.commit()
    print("[preprocess] Injected 6 calendar events (2 conflicts + 4 noise).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    launch = datetime.strptime(args.launch_time or "2026-03-07 10:00:00", "%Y-%m-%d %H:%M:%S")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_calendar_events(conn, launch)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
