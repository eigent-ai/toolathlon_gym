"""Preprocess for yf-sector-rotation-excel-notion-email.
Clears notion and email data, then injects noise entries.
"""
import os
import argparse
import json
import uuid
import psycopg2
from datetime import datetime

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        # Clear existing notion and email data
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        conn.commit()
        print("[preprocess] Cleared notion and email data.")

        # Inject 3 noise Notion pages
        noise_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.databases (id, title, properties)
            VALUES (%s, %s, %s)
        """, (
            noise_db_id,
            json.dumps([{"type": "text", "text": {"content": "Project Tracker"}, "plain_text": "Project Tracker"}]),
            json.dumps({"Name": {"type": "title"}, "Status": {"type": "select"}}),
        ))

        noise_pages = [
            ("Q4 Budget Review", "Finance team quarterly budget review notes"),
            ("Marketing Campaign Plan", "2026 marketing strategy and timeline"),
            ("Engineering Sprint Backlog", "Current sprint items and estimates"),
        ]
        for title, desc in noise_pages:
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, parent, properties)
                VALUES (%s, %s, %s)
            """, (
                page_id,
                json.dumps({"type": "database_id", "database_id": noise_db_id}),
                json.dumps({
                    "title": {"title": [{"plain_text": title, "text": {"content": title}}]},
                    "Description": {"rich_text": [{"plain_text": desc}]},
                }),
            ))

        # Inject 2 noise emails
        # Get or create a folder
        cur.execute("SELECT id FROM email.folders WHERE name='Inbox' LIMIT 1")
        folder = cur.fetchone()
        if not folder:
            cur.execute("INSERT INTO email.folders (name) VALUES ('Inbox') RETURNING id")
            folder = cur.fetchone()
        folder_id = folder[0]

        noise_emails = [
            ("admin@firm.com", ["ops@firm.com"], "Server Maintenance Window",
             "Scheduled maintenance this weekend from 2AM-6AM EST."),
            ("hr@firm.com", ["all_staff@firm.com"], "Benefits Enrollment Reminder",
             "Open enrollment closes Friday. Please submit your selections."),
        ]
        for from_addr, to_addr, subject, body in noise_emails:
            cur.execute("""
                INSERT INTO email.messages (folder_id, from_addr, to_addr, subject, body_text)
                VALUES (%s, %s, %s, %s, %s)
            """, (folder_id, from_addr, json.dumps(to_addr), subject, body))

        conn.commit()
        print("[preprocess] Injected 3 noise Notion pages and 2 noise emails.")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
