"""Preprocess: clear email and gcal data for clean evaluation state."""
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

    # Clear email tables
    for t in ["email.attachments", "email.sent_log", "email.messages"]:
        cur.execute(f"DELETE FROM {t}")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        conn.rollback()

    # Clear gcal
    cur.execute("DELETE FROM gcal.events")

    conn.commit()
    cur.close()
    conn.close()
    print("Data cleared for schemas: email, gcal")

if __name__ == "__main__":
    main()
