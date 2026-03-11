"""
Preprocess for yt-transcript-afrobeat-song-list-excel-email task.

Clears email, notion tables.
Injects an email from music@label.com requesting the Afrobeat tracklist analysis.
Injects a notion user.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
import os
import uuid
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        cur.execute("DELETE FROM notion.users")
    conn.commit()
    print("[preprocess] Cleared email and notion tables.")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        conn.commit()
        return cur.fetchone()[0]


def inject_email(conn, folder_id):
    with conn.cursor() as cur:
        msg_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (
            folder_id,
            msg_id,
            "Request: Afrobeat Mix Tracklist Analysis",
            "music@label.com",
            '["curator@musicteam.com"]',
            "Hi,\n\nWe need a full tracklist analysis of the Afrobeat Mix 2024 video "
            "(video ID: 7ZQzGq32kAY). Please identify all songs and artists featured, "
            "organize them into a spreadsheet, write up your curator notes, publish the "
            "tracklist to our team wiki, and email me the final results.\n\n"
            "We need the Excel file Afrobeat_Tracklist.xlsx with a Tracklist sheet and "
            "an Artist_Summary sheet, plus a Word document Curator_Notes.docx.\n\n"
            "Thanks,\nMusic Label Team"
        ))
    conn.commit()
    print("[preprocess] Injected request email from music@label.com.")


def inject_notion_user(conn):
    with conn.cursor() as cur:
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.users (id, name, type, person)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (user_id, "Music Curator", "person", '{"email": "curator@musicteam.com"}'))
    conn.commit()
    print("[preprocess] Injected Notion user.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        folder_id = ensure_email_folder(conn)
        inject_email(conn, folder_id)
        inject_notion_user(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
