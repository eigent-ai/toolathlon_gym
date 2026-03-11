"""
Preprocess for yt-woocommerce-product-excel-email task.

Clears email tables so the agent starts fresh.
YouTube (youtube schema) and WooCommerce (wc schema) data are READ-ONLY.

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
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared email tables.")


def ensure_email_folders(conn):
    with conn.cursor() as cur:
        for folder_name in ("INBOX", "Sent"):
            cur.execute("SELECT id FROM email.folders WHERE name = %s LIMIT 1", (folder_name,))
            if not cur.fetchone():
                cur.execute("INSERT INTO email.folders (name) VALUES (%s)", (folder_name,))
    conn.commit()
    print("[preprocess] Email folders ensured.")


def verify_readonly_data(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM youtube.videos
            WHERE channel_title = 'Fireship' AND published_at >= '2024-01-01'
        """)
        yt_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM wc.products")
        wc_count = cur.fetchone()[0]
    print(f"[preprocess] Fireship 2024+ videos: {yt_count} (read-only)")
    print(f"[preprocess] WooCommerce products: {wc_count} (read-only)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        ensure_email_folders(conn)
        verify_readonly_data(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
