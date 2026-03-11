"""
Preprocess for terminal-canvas-howtocook-excel-word-gcal task.

Clears Google Calendar. Canvas and HowToCook are read-only.
Injects noise calendar events.
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


def inject_noise_gcal(conn, launch_dt):
    """Inject noise calendar events that the agent should ignore."""
    dt1 = (launch_dt + timedelta(days=2)).strftime('%Y-%m-%d')
    dt2 = (launch_dt + timedelta(days=4)).strftime('%Y-%m-%d')
    dt3 = (launch_dt + timedelta(days=6)).strftime('%Y-%m-%d')
    with conn.cursor() as cur:
        cur.execute(f"""
            INSERT INTO gcal.events (summary, start_datetime, end_datetime, description, location)
            VALUES
            ('Department Meeting', '{dt1} 14:00:00', '{dt1} 15:00:00',
             'Monthly department sync meeting', 'Room 301'),
            ('Office Hours', '{dt2} 13:00:00', '{dt2} 14:00:00',
             'Student office hours', 'Room 205'),
            ('Faculty Lunch', '{dt3} 12:00:00', '{dt3} 13:00:00',
             'Weekly faculty lunch gathering', 'Cafeteria')
        """)
    conn.commit()
    print("[preprocess] Injected noise calendar events.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    launch_dt = datetime.strptime(args.launch_time, "%Y-%m-%d %H:%M:%S") if args.launch_time else datetime(2026, 3, 7)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_noise_gcal(conn, launch_dt)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
