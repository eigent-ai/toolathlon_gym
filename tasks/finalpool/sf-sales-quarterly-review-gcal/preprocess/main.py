"""Preprocess: clear gcal and email data for sf-sales-quarterly-review-gcal."""
import os
import argparse
import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Clear gcal events
    cur.execute("DELETE FROM gcal.events")

    # Clear email data
    for t in ["email.attachments", "email.sent_log", "email.messages"]:
        cur.execute(f"DELETE FROM {t}")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass

    conn.commit()
    cur.close()
    conn.close()
    print("Cleared gcal events and email data")


if __name__ == "__main__":
    main()
