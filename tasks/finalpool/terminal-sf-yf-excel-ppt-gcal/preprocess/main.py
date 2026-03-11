"""Preprocess for terminal-sf-yf-excel-ppt-gcal.
Clears gcal, injects conflicting calendar events for the scheduling step.
SF and YF are read-only."""
import argparse
import glob as globmod
import json
import os
import uuid
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

    launch = datetime.strptime(args.launch_time or "2026-03-07 10:00:00", "%Y-%m-%d %H:%M:%S")

    def dt(days, hours, minutes=0):
        """Return datetime string as offset from launch_time."""
        return (launch + timedelta(days=days, hours=hours, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
        conn.commit()
        print("[preprocess] Cleared gcal events.")

        # Inject conflicting events for the week starting launch+2 days
        # to make scheduling non-trivial
        conflicts = [
            # launch+1d23h = Monday Mar 9 09:00 (morning blocked)
            ("Board Meeting", dt(1, 23), dt(2, 1),
             "Quarterly board meeting", "confirmed"),
            ("Lunch with Investors", dt(2, 2), dt(2, 3, 30),
             "Investor relations lunch", "confirmed"),
            ("Product Review", dt(2, 4), dt(2, 6),
             "Product roadmap review", "confirmed"),

            # Tuesday Mar 10: mostly free (9-11 available = first 2hr slot)
            ("Team Standup", dt(2, 22, 30), dt(2, 23),
             "Daily standup", "confirmed"),
            ("Client Call", dt(3, 4), dt(3, 5),
             "Call with major client", "confirmed"),

            # Wednesday Mar 11: heavily booked
            ("Strategy Offsite", dt(3, 23), dt(4, 7),
             "Full-day strategy session", "confirmed"),

            # Thursday Mar 12: afternoon packed
            ("HR Review", dt(4, 23), dt(5, 0),
             "HR quarterly review", "confirmed"),
            ("Budget Planning", dt(5, 0, 30), dt(5, 2, 30),
             "FY2027 budget planning", "confirmed"),
            ("All Hands", dt(5, 4), dt(5, 6),
             "Company all-hands meeting", "confirmed"),

            # Friday Mar 13: morning free
            ("Friday Lunch", dt(6, 2), dt(6, 3),
             "Team lunch", "confirmed"),
            ("Sprint Retro", dt(6, 5), dt(6, 6, 30),
             "Sprint retrospective", "confirmed"),
        ]

        # Also inject some noise events outside the target week
        noise = [
            ("Weekly 1:1", dt(9, 0), dt(9, 0, 30),
             "Manager check-in", "confirmed"),
            ("Yoga Class", dt(6, 21), dt(6, 22),
             "Saturday yoga", "confirmed"),
        ]

        for summary, start, end, desc, status in conflicts + noise:
            cur.execute("""
                INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), summary, desc, start, end, status))

        conn.commit()
        print(f"[preprocess] Injected {len(conflicts)} conflict events + {len(noise)} noise events.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean agent workspace
    if args.agent_workspace:
        for pattern in ["Investment_Committee_Briefing.xlsx", "Committee_Briefing.pptx",
                        "briefing_notes.txt", "compute_growth.py", "market_comparison.py",
                        "market_comparison.json"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
