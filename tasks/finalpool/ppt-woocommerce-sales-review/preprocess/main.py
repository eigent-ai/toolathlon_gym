"""
Preprocess for ppt-woocommerce-sales-review task.

Clears email schema data so the evaluation can verify only emails
sent during the task. WooCommerce and Yahoo Finance are read-only.
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


def clear_email_data():
    """Delete all rows from email tables so evaluation starts clean."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    # Order matters due to foreign keys
    cur.execute("DELETE FROM email.attachments;")
    cur.execute("DELETE FROM email.sent_log;")
    cur.execute("DELETE FROM email.drafts;")
    cur.execute("DELETE FROM email.messages;")

    # Reset message counts on folders
    cur.execute("UPDATE email.folders SET message_count = 0, unread_count = 0;")

    conn.close()
    print("Cleared email data.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    clear_email_data()
    print("Preprocess complete.")


if __name__ == "__main__":
    main()
