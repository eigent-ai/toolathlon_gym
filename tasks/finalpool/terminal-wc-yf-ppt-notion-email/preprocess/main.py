"""Preprocess for terminal-wc-yf-ppt-notion-email.
Clears notion and email. WC and YF are read-only. Injects noise data."""
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
              json.dumps([{"type": "text", "text": {"content": "Old Inventory Tracker"}}]),
              json.dumps([{"type": "text", "text": {"content": "Deprecated inventory system"}}]),
              json.dumps({"Name": {"id": "title", "type": "title", "title": {}}}),
              json.dumps({"type": "workspace", "workspace": True})))

        for i in range(3):
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, parent, properties, created_time, last_edited_time)
                VALUES (%s, %s::jsonb, %s::jsonb, NOW(), NOW())
            """, (page_id,
                  json.dumps({"type": "database_id", "database_id": noise_db_id}),
                  json.dumps({"Name": {"title": [{"text": {"content": f"Legacy Item {i+1}"}}]}})))
        print("[preprocess] Injected noise notion data.")

        # Inject noise email data
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            inbox_id = row[0]
        else:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            inbox_id = cur.fetchone()[0]

        noise_emails = [
            ("Weekly Team Standup Notes", "admin@company.com", "team@company.com",
             "Here are the standup notes from this week. Please review action items."),
            ("Q1 Budget Review", "finance@company.com", "directors@company.com",
             "Attached is the Q1 budget review. Overall spending is within targets."),
            ("Office Supply Order Confirmation", "supplies@vendor.com", "office@company.com",
             "Your order #12345 has been confirmed and will ship next week."),
        ]
        for subj, from_addr, to_addr, body in noise_emails:
            msg_id = f"<{uuid.uuid4()}@noise.local>"
            cur.execute("""
                INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), %s, true)
            """, (inbox_id, msg_id, subj, from_addr, json.dumps([to_addr]), body))
        print("[preprocess] Injected noise email data.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean any leftover agent outputs
    if args.agent_workspace:
        for pattern in ["Market_Strategy_Presentation.pptx", "market_correlation.py",
                        "category_analysis.py", "market_correlation.json",
                        "category_market_analysis.json"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
