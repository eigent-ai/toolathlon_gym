"""Preprocess for sf-hr-attrition-forecast-excel-word-gcal.
Clears gcal and email data, injects noise calendar events."""
import os
import argparse
import uuid
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
        # Clear writable schemas
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        conn.commit()
        print("[preprocess] Cleared gcal events and email data.")

        # Inject noise calendar events
        noise_events = [
            {
                "summary": "Weekly Team Standup",
                "description": "Regular weekly standup meeting for the engineering team.",
                "start_datetime": "2026-03-16 09:00:00+00",
                "end_datetime": "2026-03-16 09:30:00+00",
                "location": "Conference Room A",
            },
            {
                "summary": "Q1 Budget Review",
                "description": "Quarterly budget review with finance leadership.",
                "start_datetime": "2026-03-17 14:00:00+00",
                "end_datetime": "2026-03-17 15:00:00+00",
                "location": "Board Room",
            },
            {
                "summary": "Product Roadmap Planning",
                "description": "Cross-functional meeting to discuss Q2 product roadmap.",
                "start_datetime": "2026-03-18 10:00:00+00",
                "end_datetime": "2026-03-18 11:30:00+00",
                "location": "Virtual",
            },
            {
                "summary": "All Hands Meeting",
                "description": "Monthly company-wide all hands meeting.",
                "start_datetime": "2026-03-19 16:00:00+00",
                "end_datetime": "2026-03-19 17:00:00+00",
                "location": "Main Auditorium",
            },
        ]

        for evt in noise_events:
            cur.execute("""
                INSERT INTO gcal.events (id, summary, description,
                    start_datetime, end_datetime, location, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()), evt["summary"], evt["description"],
                evt["start_datetime"], evt["end_datetime"],
                evt.get("location", ""), "confirmed"
            ))
        conn.commit()
        print(f"[preprocess] Injected {len(noise_events)} noise calendar events.")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
