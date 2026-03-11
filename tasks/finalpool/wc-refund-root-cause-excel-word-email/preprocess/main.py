"""
Preprocess for wc-refund-root-cause-excel-word-email task.

WooCommerce data is read-only. This script:
1. Clears email data
2. Injects 2-3 noise emails in inbox
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


def clear_emails(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    print("[preprocess] Email data cleared.")


def ensure_folders(cur):
    """Ensure INBOX and Sent folders exist."""
    for folder_name in ["INBOX", "Sent"]:
        cur.execute("SELECT id FROM email.folders WHERE name = %s LIMIT 1", (folder_name,))
        if not cur.fetchone():
            cur.execute("INSERT INTO email.folders (name) VALUES (%s)", (folder_name,))
    print("[preprocess] Email folders ensured.")


def inject_noise_emails(cur):
    """Inject a few noise emails so the inbox isn't empty."""
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    inbox_row = cur.fetchone()
    inbox_id = inbox_row[0] if inbox_row else 1

    noise_emails = [
        {
            "subject": "Q1 Marketing Campaign Results",
            "from_addr": "marketing@company.com",
            "to_addr": json.dumps(["team@company.com"]),
            "body_text": "Hi team, please find attached the Q1 marketing campaign results. "
                         "Overall conversion rates improved by 12% compared to last quarter.",
        },
        {
            "subject": "Office Maintenance Schedule - March",
            "from_addr": "facilities@company.com",
            "to_addr": json.dumps(["all@company.com"]),
            "body_text": "Please be advised that the HVAC system maintenance is scheduled for "
                         "March 15-16. The building temperature may fluctuate during this period.",
        },
        {
            "subject": "Re: Team Lunch Friday",
            "from_addr": "sarah.jones@company.com",
            "to_addr": json.dumps(["qa_team@company.com"]),
            "body_text": "Sounds great! I'll book the Italian place. Everyone please confirm "
                         "attendance by Thursday EOD.",
        },
    ]

    for email in noise_emails:
        cur.execute("""
            INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr,
                                        date, body_text, is_read, is_important, is_flagged)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s, true, false, false)
        """, (
            inbox_id,
            f"<noise-{uuid.uuid4()}@company.com>",
            email["subject"],
            email["from_addr"],
            email["to_addr"],
            email["body_text"],
        ))

    print(f"[preprocess] Injected {len(noise_emails)} noise emails.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_emails(cur)
        ensure_folders(cur)
        inject_noise_emails(cur)
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
