"""Preprocess for terminal-howtocook-gform-excel-notion-email.
Clears gform, notion, email. HowToCook is MCP-only (read-only). Injects noise data."""
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
        # Clear gform
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        print("[preprocess] Cleared gform data.")

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

        # Inject noise gform
        noise_form_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gform.forms (id, title, document_title, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (noise_form_id, "Old Employee Survey", "Old Employee Survey",
              "This is an archived employee satisfaction survey."))
        cur.execute("""
            INSERT INTO gform.questions (id, form_id, item_id, title, question_type, required, position)
            VALUES (%s, %s, %s, %s, %s, true, 0)
        """, (str(uuid.uuid4()), noise_form_id, str(uuid.uuid4()),
              "How satisfied are you with your workspace?", "SCALE"))
        print("[preprocess] Injected noise gform data.")

        # Inject noise notion data
        noise_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.databases (id, title, description, properties, parent, created_time, last_edited_time)
            VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, NOW(), NOW())
        """, (noise_db_id,
              json.dumps([{"type": "text", "text": {"content": "Old Meeting Notes"}}]),
              json.dumps([{"type": "text", "text": {"content": "Archived meeting notes"}}]),
              json.dumps({"Title": {"id": "title", "type": "title", "title": {}}}),
              json.dumps({"type": "workspace", "workspace": True})))
        for i in range(2):
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, parent, properties, created_time, last_edited_time)
                VALUES (%s, %s::jsonb, %s::jsonb, NOW(), NOW())
            """, (page_id,
                  json.dumps({"type": "database_id", "database_id": noise_db_id}),
                  json.dumps({"Title": {"title": [{"text": {"content": f"Meeting {i+1}"}}]}})))
        print("[preprocess] Injected noise notion data.")

        # Inject noise email
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM email.messages")
            max_id = cur.fetchone()[0] + 1
            cur.execute("""
                INSERT INTO email.messages (id, folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW(), %s, false)
            """, (max_id, folder_id, f"noise-{uuid.uuid4()}@company.com",
                  "Parking Lot Update", "facilities@company.com",
                  json.dumps(["all_staff@company.com"]),
                  "The parking lot will be repaved this weekend."))
            print("[preprocess] Injected noise email data.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Meal_Program_Plan.xlsx", "menu_planner.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
