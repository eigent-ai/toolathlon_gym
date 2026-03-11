"""Preprocess for wc-tax-compliance-excel-gcal-gform. Clears gcal, gform, email data and injects noise."""
import os
import argparse
from datetime import datetime, timedelta

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    launch_dt = datetime.strptime(args.launch_time, "%Y-%m-%d %H:%M:%S") if args.launch_time else datetime(2026, 3, 7, 10, 0, 0)

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        # Clear existing data
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")

        # Inject noise calendar events
        ev1_start = (launch_dt + timedelta(days=3, hours=-1)).strftime("%Y-%m-%d %H:%M:%S+00")
        ev1_end = (launch_dt + timedelta(days=3, minutes=-30)).strftime("%Y-%m-%d %H:%M:%S+00")
        cur.execute(f"""
            INSERT INTO gcal.events (summary, start_datetime, end_datetime, description)
            VALUES ('Team Standup', '{ev1_start}', '{ev1_end}',
                    'Daily standup meeting')
        """)
        ev2_start = (launch_dt + timedelta(days=8, hours=4)).strftime("%Y-%m-%d %H:%M:%S+00")
        ev2_end = (launch_dt + timedelta(days=8, hours=5)).strftime("%Y-%m-%d %H:%M:%S+00")
        cur.execute(f"""
            INSERT INTO gcal.events (summary, start_datetime, end_datetime, description)
            VALUES ('Budget Review Meeting', '{ev2_start}', '{ev2_end}',
                    'Quarterly budget review with finance')
        """)

        # Inject noise form
        cur.execute("""
            INSERT INTO gform.forms (title, description)
            VALUES ('Employee Satisfaction Survey', 'Annual employee satisfaction feedback form')
            RETURNING id
        """)
        noise_form_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO gform.questions (form_id, title, question_type, required, position)
            VALUES (%s, 'How satisfied are you with your role?', 'SCALE', true, 0)
        """, (noise_form_id,))
        cur.execute("""
            INSERT INTO gform.questions (form_id, title, question_type, required, position)
            VALUES (%s, 'Additional comments', 'PARAGRAPH_TEXT', false, 1)
        """, (noise_form_id,))

        conn.commit()
        print("[preprocess] Cleared gcal, gform, email data and injected noise.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
