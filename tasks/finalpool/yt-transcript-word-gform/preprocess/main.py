"""
Preprocess for yt-transcript-word-gform task.

Clears gform tables, email tables for clean state.
The Afrobeat transcript is already in youtube.transcripts (READ-ONLY).
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

FORM_TITLE = "Afrobeat Mix Feedback"


def clear_tables(conn):
    with conn.cursor() as cur:
        # Clear matching gform data - responses cascade from forms via FK
        cur.execute("""
            DELETE FROM gform.responses WHERE form_id IN (
                SELECT id FROM gform.forms WHERE title ILIKE %s
            )
        """, (f"%{FORM_TITLE}%",))
        cur.execute("""
            DELETE FROM gform.questions WHERE form_id IN (
                SELECT id FROM gform.forms WHERE title ILIKE %s
            )
        """, (f"%{FORM_TITLE}%",))
        cur.execute("DELETE FROM gform.forms WHERE title ILIKE %s",
                    (f"%{FORM_TITLE}%",))
        # Clear email tables (must clear sent_log before messages due to FK)
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared gform and email tables.")


def verify_transcript(conn):
    """Verify the Afrobeat transcript exists (READ-ONLY check)."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT video_id, title, LENGTH(content) as content_len
            FROM youtube.transcripts
            WHERE video_id = '7ZQzGq32kAY'
        """)
        row = cur.fetchone()
        if row:
            print(f"[preprocess] Transcript found: video_id={row[0]}, title={row[1]}, length={row[2]}")
        else:
            print("[preprocess] WARNING: Afrobeat transcript not found in youtube.transcripts!")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        verify_transcript(conn)
        ensure_email_folder(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
