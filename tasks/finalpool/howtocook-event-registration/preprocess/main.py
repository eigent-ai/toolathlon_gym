"""
Preprocess for howtocook-event-registration task.
Clears writable schemas: gform, gcal, notion, email.
HowToCook is read-only (no changes needed).
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


def clear_writable_schemas(conn):
    """Clear all data from writable schemas used by this task."""
    cur = conn.cursor()

    # Clear gform data (order matters due to foreign keys)
    print("[preprocess] Clearing Google Form data...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")

    # Clear gcal data
    print("[preprocess] Clearing Google Calendar events...")
    cur.execute("DELETE FROM gcal.events")

    # Clear notion data (order matters due to foreign keys)
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")

    # Clear email data (order matters due to foreign keys)
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    cur.execute("DELETE FROM email.drafts")

    conn.commit()
    cur.close()
    print("[preprocess] All writable schemas cleared.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, help="Launch time")
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_writable_schemas(conn)
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")
