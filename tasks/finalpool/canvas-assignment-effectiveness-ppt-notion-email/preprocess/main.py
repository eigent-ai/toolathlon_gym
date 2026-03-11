"""
Preprocess script for canvas-assignment-effectiveness-ppt-notion-email task.
Canvas is read-only. Clears notion, email data and injects noise entries.
"""
import os
import argparse
import json
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Clear Notion data
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        print("[preprocess] Cleared Notion data.")

        # Clear email data
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        print("[preprocess] Cleared email data.")

        # Inject noise Notion pages (unrelated content)
        noise_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.databases (id, object, title, properties, parent, archived, is_inline)
            VALUES (%s, 'database', %s, %s, %s, false, false)
        """, (
            noise_db_id,
            json.dumps([{"type": "text", "text": {"content": "Meeting Notes"}}]),
            json.dumps({"Name": {"title": {}}, "Date": {"date": {}}}),
            json.dumps({"type": "workspace", "workspace": True}),
        ))

        for i, title in enumerate(["Q3 Planning Meeting", "Budget Review Session", "Team Retrospective"]):
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, object, parent, archived, in_trash, properties)
                VALUES (%s, 'page', %s, false, false, %s)
            """, (
                page_id,
                json.dumps({"type": "database_id", "database_id": noise_db_id}),
                json.dumps({"Name": {"title": [{"text": {"content": title}}]}}),
            ))
        print("[preprocess] Injected noise Notion data.")

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        inbox_id = row[0] if row else 3073

        noise_emails = [
            ("Weekly Team Update", "manager@company.com",
             json.dumps(["team@company.com"]),
             "Here is the weekly status update for the engineering team."),
            ("Office Supply Request", "admin@company.com",
             json.dumps(["procurement@company.com"]),
             "We need to reorder printer paper and toner cartridges."),
        ]
        for subj, from_addr, to_addr, body in noise_emails:
            cur.execute("""
                INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, body_text)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (inbox_id, str(uuid.uuid4()), subj, from_addr, to_addr, body))
        print("[preprocess] Injected noise emails.")

        conn.commit()
        print("[preprocess] Done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
