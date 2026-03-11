"""Preprocess: Clear email and gform data before task execution."""
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


def clear_emails(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.drafts")
    cur.execute("DELETE FROM email.messages")
    print("[preprocess] Email data cleared.")


def clear_gform(cur):
    print("[preprocess] Clearing Google Forms data...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    print("[preprocess] Google Forms data cleared.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    clear_emails(cur)
    clear_gform(cur)

    cur.close()
    conn.close()
    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
