"""
Preprocess for yt-fireship-ppt-gcal-email task.

Clears gcal events and email tables so the agent starts fresh.
YouTube data is READ-ONLY and already present in the youtube schema.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
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


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared gcal.events and email tables.")


def ensure_email_folders(conn):
    with conn.cursor() as cur:
        for folder_name in ("INBOX", "Sent"):
            cur.execute("SELECT id FROM email.folders WHERE name = %s LIMIT 1", (folder_name,))
            if not cur.fetchone():
                cur.execute("INSERT INTO email.folders (name) VALUES (%s)", (folder_name,))
    conn.commit()
    print("[preprocess] Email folders ensured.")


def verify_youtube_data(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM youtube.videos
            WHERE channel_title = 'Fireship'
            AND published_at >= '2025-01-01' AND published_at < '2025-07-01'
        """)
        count = cur.fetchone()[0]
    print(f"[preprocess] Verified: {count} Fireship videos in Jan-Jun 2025 (read-only).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        ensure_email_folders(conn)
        verify_youtube_data(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
