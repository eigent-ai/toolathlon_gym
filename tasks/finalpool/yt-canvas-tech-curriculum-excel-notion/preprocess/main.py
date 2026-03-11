"""
Preprocess for yt-canvas-tech-curriculum-excel-notion task.

Clears notion and email tables so the agent starts fresh.
YouTube data (youtube schema) and Canvas data (canvas schema) are READ-ONLY.

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
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared notion and email tables.")


def verify_readonly_data(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM youtube.videos WHERE channel_title = 'Fireship'")
        yt_count = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*) FROM canvas.courses
            WHERE name ILIKE '%analytics%' OR name ILIKE '%algorithms%'
            OR name ILIKE '%computing%' OR name ILIKE '%data%'
            OR name ILIKE '%software%'
        """)
        course_count = cur.fetchone()[0]
    print(f"[preprocess] Fireship videos: {yt_count} (read-only)")
    print(f"[preprocess] Matching courses: {course_count} (read-only)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        verify_readonly_data(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
