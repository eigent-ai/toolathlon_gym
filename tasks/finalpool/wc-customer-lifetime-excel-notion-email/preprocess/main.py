"""
Preprocess script for wc-customer-lifetime-excel-notion-email task.

WooCommerce data is read-only. This script:
1. Clears Notion data and injects noise pages
2. Clears email data and injects noise emails
"""

import os
import argparse
import json
import uuid
from datetime import datetime, timezone

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def clear_notion(cur):
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    print("[preprocess] Notion data cleared.")


def inject_notion_noise(cur):
    print("[preprocess] Injecting Notion noise pages...")
    now = datetime.now(timezone.utc)

    noise_pages = [
        {"title": "Q4 Marketing Budget", "content": "Budget allocation for marketing campaigns"},
        {"title": "Team Meeting Notes - Jan 2026", "content": "Weekly standup notes and action items"},
        {"title": "Product Roadmap 2026", "content": "Feature priorities for the upcoming year"},
        {"title": "Vendor Contact List", "content": "Supplier and vendor information"},
    ]

    for page in noise_pages:
        page_id = str(uuid.uuid4())
        properties = {
            "title": {
                "id": "title",
                "type": "title",
                "title": [{"type": "text", "text": {"content": page["title"]}, "plain_text": page["title"]}],
            }
        }
        cur.execute(
            """INSERT INTO notion.pages (id, object, created_time, last_edited_time, created_by, last_edited_by,
               cover, icon, parent, archived, in_trash, properties, url, public_url)
               VALUES (%s, 'page', %s, %s, %s, %s, NULL, NULL, %s, false, false, %s, %s, NULL)""",
            (
                page_id,
                now,
                now,
                json.dumps({"object": "user", "id": "system"}),
                json.dumps({"object": "user", "id": "system"}),
                json.dumps({"type": "workspace", "workspace": True}),
                json.dumps(properties),
                f"https://www.notion.so/{page_id.replace('-', '')}",
            ),
        )
        # Add a block with content
        block_id = str(uuid.uuid4())
        cur.execute(
            """INSERT INTO notion.blocks (id, object, parent_type, parent_id, created_time, last_edited_time,
               created_by, last_edited_by, type, has_children, archived, in_trash, block_data, position)
               VALUES (%s, 'block', 'page_id', %s, %s, %s, %s, %s, 'paragraph', false, false, false, %s, 0)""",
            (
                block_id,
                page_id,
                now,
                now,
                json.dumps({"object": "user", "id": "system"}),
                json.dumps({"object": "user", "id": "system"}),
                json.dumps({
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": page["content"]}, "plain_text": page["content"]}]
                    }
                }),
            ),
        )
    print(f"[preprocess] Injected {len(noise_pages)} noise Notion pages.")


def clear_emails(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    cur.execute("DELETE FROM email.drafts")
    print("[preprocess] Email data cleared.")


def inject_email_noise(cur):
    print("[preprocess] Injecting noise emails...")
    now = datetime.now(timezone.utc)

    # Get INBOX folder id
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    row = cur.fetchone()
    if not row:
        print("[preprocess] WARNING: No INBOX folder found, skipping email noise.")
        return
    inbox_id = row[0]

    noise_emails = [
        {
            "subject": "Monthly Newsletter - March 2026",
            "from": "newsletter@marketing.com",
            "to": ["admin@company.com"],
            "body": "Here is your monthly marketing newsletter with the latest updates and promotions.",
        },
        {
            "subject": "Server Maintenance Scheduled",
            "from": "devops@company.com",
            "to": ["admin@company.com"],
            "body": "Planned maintenance window this weekend. Expect 2 hours of downtime Saturday night.",
        },
    ]

    for em in noise_emails:
        cur.execute(
            """INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date,
               body_text, is_read, is_important, is_flagged)
               VALUES (%s, %s, %s, %s, %s, %s, %s, false, false, false)""",
            (
                inbox_id,
                f"<{uuid.uuid4()}@noise.com>",
                em["subject"],
                em["from"],
                json.dumps(em["to"]),
                now,
                em["body"],
            ),
        )
    print(f"[preprocess] Injected {len(noise_emails)} noise emails.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_notion(cur)
        inject_notion_noise(cur)
        clear_emails(cur)
        inject_email_noise(cur)
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
