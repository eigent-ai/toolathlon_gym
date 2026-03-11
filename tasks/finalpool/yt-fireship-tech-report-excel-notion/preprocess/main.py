"""
Preprocess for yt-fireship-tech-report-excel-notion task.

- Clears gcal, notion, email tables
- Injects 1 noise gcal event (team sync on 2026-03-09 09:00-10:00)
- Injects 1 email from manager asking about tech trends
"""
import os
import argparse
import json
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def clear_tables(conn):
    with conn.cursor() as cur:
        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
        # Clear notion
        try:
            cur.execute("DELETE FROM notion.comments")
        except Exception:
            pass
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        # Clear email
        try:
            cur.execute("DELETE FROM email.attachments")
        except Exception:
            pass
        try:
            cur.execute("DELETE FROM email.sent_log")
        except Exception:
            pass
        cur.execute("DELETE FROM email.messages")
    conn.commit()
    print("[preprocess] Cleared gcal.events, notion tables, email.messages")


def inject_gcal_noise(conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gcal.events (summary, description, start_datetime, end_datetime, start_timezone, end_timezone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "Team Sync",
            "Regular team sync meeting.",
            "2026-03-09 09:00:00+00",
            "2026-03-09 10:00:00+00",
            "UTC",
            "UTC",
        ))
    conn.commit()
    print("[preprocess] Injected noise gcal event: Team Sync on 2026-03-09")


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
            "Tech Trends Report - Q1 2026",
            "manager@company.com",
            json.dumps(["you@company.com"]),
            "2026-03-05 10:00:00+00",
            "Hi, could you please compile a technology trend report based on the most popular Fireship videos from 2024-2025? We need this for our Q1 review. Include the top 10 videos and summarize which tech topics are trending. Also, please publish the findings to our team knowledge base and schedule a weekly tech review meeting. Thanks!",
        ))
    conn.commit()
    print("[preprocess] Injected manager email asking for tech trends report")


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
