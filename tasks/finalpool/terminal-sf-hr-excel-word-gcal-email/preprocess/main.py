"""Preprocess for terminal-sf-hr-excel-word-gcal-email.
Clears gcal and email. Snowflake is read-only. Injects noise data."""
import argparse
import json
import os
import uuid
import glob as globmod

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear gcal
        cur.execute("DELETE FROM gcal.events")
        print("[preprocess] Cleared gcal data.")

        # Clear email
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        print("[preprocess] Cleared email data.")

        # Inject noise gcal events
        for i, title in enumerate(["All-Hands Meeting", "Budget Review"]):
            cur.execute("""
                INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status)
                VALUES (%s, %s, %s, %s, %s, 'confirmed')
            """, (str(uuid.uuid4()), title, f"Regular {title.lower()}",
                  f"2026-03-{6+i:02d} 10:00:00", f"2026-03-{6+i:02d} 11:00:00"))
        print("[preprocess] Injected noise gcal data.")

        # Inject noise email
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM email.messages")
            max_id = cur.fetchone()[0]
            for i in range(2):
                max_id += 1
                cur.execute("""
                    INSERT INTO email.messages (id, folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW(), %s, false)
                """, (max_id, folder_id, f"noise-{uuid.uuid4()}@company.com",
                      f"Office Update #{i+1}", "admin@company.com",
                      json.dumps(["all@company.com"]),
                      f"This is a routine office update #{i+1}."))
            print("[preprocess] Injected noise email data.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Performance_Review_Report.xlsx", "Review_Policy_Memo.docx", "rating_analysis.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
