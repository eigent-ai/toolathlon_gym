"""
Preprocess for yt-fireship-gform-survey-excel-gcal task.

- Clears gcal, email, gform tables
- Injects 1 email from community@devclub.io asking for monthly engagement report
- Injects 1 gcal noise event: "Community Q&A" on 2026-04-01 16:00-17:00
"""
import argparse
import json
import os
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
        try:
            cur.execute("DELETE FROM email.attachments")
        except Exception:
            pass
        try:
            cur.execute("DELETE FROM email.sent_log")
        except Exception:
            pass
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
    conn.commit()
    print("[preprocess] Cleared gcal.events, email.messages, gform tables")


def inject_gcal_noise(conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gcal.events (summary, description, start_datetime, end_datetime, start_timezone, end_timezone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "Community Q&A",
            "Monthly community Q&A session.",
            "2026-04-01 16:00:00+00",
            "2026-04-01 17:00:00+00",
            "UTC",
            "UTC",
        ))
    conn.commit()
    print("[preprocess] Injected noise gcal event: Community Q&A on 2026-04-01 16:00-17:00")


def inject_email(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
        else:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            folder_id = cur.fetchone()[0]
            conn.commit()

        cur.execute("""
            INSERT INTO email.messages (folder_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s)
        """, (
            folder_id,
            "Monthly Engagement Report - March 2026",
            "community@devclub.io",
            json.dumps(["manager@devclub.io"]),
            "2026-03-06 10:00:00+00",
            "Hi, please prepare the monthly engagement report for the Fireship community. We need the top 8 videos by view count covering JavaScript, TypeScript, React, AI/ML, Systems, and DevOps topics. Also create a community preference survey form with questions about topic interests and viewing habits. Compile the video stats in Community_Report.xlsx and schedule a community standup on April 1st. Please send the report summary and survey link to community@devclub.io. Thanks!",
        ))
    conn.commit()
    print("[preprocess] Injected community@devclub.io email")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal_noise(conn)
        inject_email(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
