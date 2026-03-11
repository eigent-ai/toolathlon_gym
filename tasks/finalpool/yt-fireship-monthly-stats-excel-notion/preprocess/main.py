"""
Preprocess for yt-fireship-monthly-stats-excel-notion task.

Clears notion pages with matching title, clears gcal events,
clears email tables, and ensures email folder exists.

YouTube data is READ-ONLY - do not touch youtube schema.
"""
import os
import argparse
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

NOTION_PAGE_TITLE = "Fireship Channel Analysis 2024-2025"


def clear_tables(conn):
    with conn.cursor() as cur:
        # Clear notion pages with matching title in properties JSON
        cur.execute("""
            DELETE FROM notion.pages
            WHERE properties::text ILIKE %s
        """, (f"%{NOTION_PAGE_TITLE}%",))
        # Clear email tables (must clear sent_log before messages due to FK)
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared notion pages, email tables.")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()
            print("[preprocess] Created INBOX email folder.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        ensure_email_folder(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
