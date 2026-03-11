"""Preprocess for terminal-canvas-excel-word-notion-email.
Clears notion and email writable schemas. Injects noise data. Canvas is read-only."""
import argparse
import json
import os
import uuid
import glob as globmod

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
        # Clear notion
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        print("[preprocess] Cleared notion data.")

        # Clear email
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        print("[preprocess] Cleared email data.")

        # Inject noise notion data
        noise_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.databases (id, title, description, properties, parent, created_time, last_edited_time)
            VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, NOW(), NOW())
        """, (noise_db_id,
              json.dumps([{"type": "text", "text": {"content": "Old Course Notes"}}]),
              json.dumps([{"type": "text", "text": {"content": "Archived course materials"}}]),
              json.dumps({"Title": {"id": "title", "type": "title", "title": {}}}),
              json.dumps({"type": "workspace", "workspace": True})))

        for i in range(3):
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, parent, properties, created_time, last_edited_time)
                VALUES (%s, %s::jsonb, %s::jsonb, NOW(), NOW())
            """, (page_id,
                  json.dumps({"type": "database_id", "database_id": noise_db_id}),
                  json.dumps({"Title": {"title": [{"text": {"content": f"Archived Note {i+1}"}}]}})))
        print("[preprocess] Injected noise notion data.")

        # Inject noise email
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM email.messages")
            max_id = cur.fetchone()[0]
            for i in range(2):
                max_id += 1
                cur.execute("""
                    INSERT INTO email.messages (id, folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW(), %s, false)
                """, (max_id, folder_id, f"noise-{uuid.uuid4()}@example.com",
                      f"Weekly Newsletter #{i+1}", "newsletter@university.edu",
                      json.dumps(["advisor@university.edu"]),
                      f"This is noise email content #{i+1}."))
            print("[preprocess] Injected noise email data.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean workspace
    if args.agent_workspace:
        for pattern in ["Student_Risk_Analysis.xlsx", "Intervention_Plan.docx", "risk_scorer.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
