"""
Preprocess script for notion-snowflake-quarterly task.

1. Clears Notion data (blocks, comments, pages, databases, users)
2. Clears Google Sheets data (cells, sheets, spreadsheets)
3. Injects a Notion page "Q4 2024 Sales Targets" with regional revenue targets as blocks
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


def clear_notion(cur):
    """Clear all Notion data."""
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM notion.users")
    print("[preprocess] Notion data cleared.")


def clear_gsheet(cur):
    """Clear all Google Sheets data."""
    print("[preprocess] Clearing Google Sheets data...")
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.sheets")
    # Need to clear permissions before spreadsheets due to FK constraint
    try:
        cur.execute("DELETE FROM gsheet.permissions")
    except Exception:
        pass
    cur.execute("DELETE FROM gsheet.spreadsheets")
    print("[preprocess] Google Sheets data cleared.")


def inject_notion_targets(cur):
    """Inject the Q4 2024 Sales Targets page with regional target blocks."""
    print("[preprocess] Injecting Notion Q4 targets page...")

    page_id = "q4-targets-" + uuid.uuid4().hex[:8]
    page_properties = json.dumps({
        "title": {
            "id": "title",
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {"content": "Q4 2024 Sales Targets", "link": None},
                    "plain_text": "Q4 2024 Sales Targets",
                }
            ],
        }
    })
    page_parent = json.dumps({"type": "workspace", "workspace": True})

    cur.execute(
        """INSERT INTO notion.pages (id, object, parent, properties, url, archived, in_trash)
           VALUES (%s, 'page', %s, %s, %s, false, false)""",
        (page_id, page_parent, page_properties, f"https://www.notion.so/{page_id}"),
    )

    # Add blocks: heading + one paragraph per region
    blocks = [
        ("heading_1", "Regional Revenue Targets", 0),
        ("paragraph", "Asia Pacific: $80,000", 1),
        ("paragraph", "Europe: $85,000", 2),
        ("paragraph", "Latin America: $75,000", 3),
        ("paragraph", "Middle East: $85,000", 4),
        ("paragraph", "North America: $80,000", 5),
    ]

    for block_type, text_content, position in blocks:
        block_id = "block-" + uuid.uuid4().hex[:12]
        block_data = json.dumps({
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text_content, "link": None},
                    "plain_text": text_content,
                }
            ]
        })
        cur.execute(
            """INSERT INTO notion.blocks
               (id, parent_type, parent_id, type, block_data, position, archived, in_trash)
               VALUES (%s, 'page_id', %s, %s, %s, %s, false, false)""",
            (block_id, page_id, block_type, block_data, position),
        )

    print(f"[preprocess] Injected page '{page_id}' with {len(blocks)} blocks.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_notion(cur)
        clear_gsheet(cur)
        inject_notion_targets(cur)
        conn.commit()
        print("[preprocess] Database operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Database error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
