"""Preprocess for wc-customer-order-gsheet-email task.

WooCommerce is read-only. This script clears writable schemas
(gsheet, email) to ensure a clean environment.
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


def clear_gsheet(cur):
    print("[preprocess] Clearing Google Sheets data...")
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.permissions")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    print("[preprocess] Google Sheets data cleared.")


def clear_email(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.messages")
    cur.execute("DELETE FROM email.drafts")
    print("[preprocess] Email data cleared.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        clear_gsheet(cur)
        clear_email(cur)
        print("[preprocess] Done. Writable schemas cleared.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
