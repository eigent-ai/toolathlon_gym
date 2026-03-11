"""Preprocess for yf-portfolio-stress-test-excel-word-gcal.
Clears gcal events, email data, and injects noise calendar events."""
import os
import argparse
import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        # Clear existing data
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")

        # Insert noise calendar events
        noise_events = [
            ("Team Standup", "Daily team sync", "2026-03-16 09:00:00", "2026-03-16 09:30:00"),
            ("Lunch with Client", "Discuss Q2 partnership", "2026-03-18 12:00:00", "2026-03-18 13:00:00"),
            ("Board Meeting", "Quarterly board review", "2026-03-20 14:00:00", "2026-03-20 16:00:00"),
            ("HR Training", "Annual compliance training", "2026-03-25 11:00:00", "2026-03-25 12:00:00"),
        ]
        for summary, desc, start, end in noise_events:
            cur.execute(
                "INSERT INTO gcal.events (summary, description, start_datetime, end_datetime) VALUES (%s, %s, %s, %s)",
                (summary, desc, start, end),
            )

        conn.commit()
        print("[preprocess] Cleared gcal events and email data, inserted noise events.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
