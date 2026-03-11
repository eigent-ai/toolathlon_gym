"""Preprocess for terminal-wc-sf-notion-excel-email.
Clears notion and email schemas, injects noise data."""
import argparse
import json
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
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Clear notion
        print("[preprocess] Clearing notion schema...")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")

        # Clear email
        print("[preprocess] Clearing email schema...")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")

        # Inject noise notion database - "Project Tracker"
        noise_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.databases (id, title, description, properties, parent)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            noise_db_id,
            json.dumps([{"type": "text", "text": {"content": "Project Tracker"}}]),
            json.dumps([{"type": "text", "text": {"content": "Track ongoing projects"}}]),
            json.dumps({
                "Name": {"id": "title", "type": "title", "title": {}},
                "Status": {"id": "status", "type": "select", "select": {"options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Completed", "color": "blue"}
                ]}},
                "Owner": {"id": "owner", "type": "rich_text", "rich_text": {}}
            }),
            json.dumps({"type": "workspace", "workspace": True})
        ))

        # Add noise notion pages
        for i, (name, owner) in enumerate([
            ("Website Redesign", "Alice"),
            ("Mobile App v2", "Bob"),
            ("Data Pipeline Upgrade", "Charlie"),
        ]):
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, parent, properties, archived)
                VALUES (%s, %s, %s, false)
            """, (
                page_id,
                json.dumps({"type": "database_id", "database_id": noise_db_id}),
                json.dumps({
                    "Name": {"title": [{"text": {"content": name}}]},
                    "Status": {"select": {"name": "Active"}},
                    "Owner": {"rich_text": [{"text": {"content": owner}}]}
                })
            ))

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            inbox_id = row[0]
        else:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            inbox_id = cur.fetchone()[0]

        cur.execute("SELECT id FROM email.folders WHERE name = 'Sent' LIMIT 1")
        row = cur.fetchone()
        if row:
            sent_id = row[0]
        else:
            cur.execute("INSERT INTO email.folders (name) VALUES ('Sent') RETURNING id")
            sent_id = cur.fetchone()[0]

        noise_emails = [
            ("Weekly Team Standup Notes", "manager@company.com", "team@company.com",
             "Here are the standup notes from this week. Please review before Monday."),
            ("Q1 Budget Approval", "finance@company.com", "vp_cx@company.com",
             "The Q1 budget has been approved. Please proceed with planned initiatives."),
            ("New Hire Onboarding Schedule", "hr@company.com", "team@company.com",
             "Welcome our new team members. Onboarding sessions start next Monday."),
            ("Server Maintenance Window", "ops@company.com", "all@company.com",
             "Scheduled maintenance this Saturday from 2AM-6AM. Expect brief downtime."),
            ("Customer Feedback Summary - Jan", "analytics@company.com", "product_team@company.com",
             "January feedback summary attached. Overall sentiment trending positive."),
        ]

        for subj, from_addr, to_addr, body in noise_emails:
            msg_id = f"<noise-{uuid.uuid4()}@company.com>"
            cur.execute("""
                INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s, true)
            """, (inbox_id, msg_id, subj, from_addr,
                  json.dumps([to_addr]), body))

        conn.commit()
        print("[preprocess] Done. Noise data injected into notion and email.")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
