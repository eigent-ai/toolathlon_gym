"""Preprocess for terminal-canvas-sf-excel-ppt-gcal.
Clears gcal. Injects noise calendar events. Canvas and SF are read-only."""
import argparse
import glob as globmod
import os
import uuid

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

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
        conn.commit()
        print("[preprocess] Cleared gcal events.")

        # Inject noise calendar events
        noise_events = [
            ("Team Standup", "2026-03-16 09:00:00", "2026-03-16 09:30:00", "Daily standup meeting"),
            ("Lunch with Client", "2026-03-17 12:00:00", "2026-03-17 13:00:00", "Client lunch at downtown"),
            ("Project Deadline Review", "2026-03-18 15:00:00", "2026-03-18 16:00:00", "Quarterly review"),
        ]
        for summary, start, end, desc in noise_events:
            cur.execute("""
                INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status)
                VALUES (%s, %s, %s, %s, %s, 'confirmed')
            """, (str(uuid.uuid4()), summary, desc, start, end))
        conn.commit()
        print("[preprocess] Injected 3 noise calendar events.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up agent workspace
    if args.agent_workspace:
        for pattern in ["Skills_Gap_Analysis.xlsx", "Skills_Gap_Presentation.pptx", "gap_analyzer.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
