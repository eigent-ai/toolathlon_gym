"""
Preprocess script for canvas-quiz-analysis-email task.

Canvas is read-only. This script clears email tables.
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        print("[preprocess] Clearing email data...")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM email.drafts")
        cur.execute("DELETE FROM email.folders")
        print("[preprocess] Email data cleared.")

        # Re-insert standard email folders
        print("[preprocess] Inserting email folders...")
        cur.execute("""
            INSERT INTO email.folders (id, name, delimiter, flags, message_count, unread_count)
            VALUES (1, 'INBOX', '/', '{}', 0, 0),
                   (2, 'Sent', '/', '{}', 0, 0),
                   (3, 'Drafts', '/', '{}', 0, 0),
                   (4, 'Trash', '/', '{}', 0, 0)
            ON CONFLICT (id) DO NOTHING
        """)
        print("[preprocess] Email folders inserted.")
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
