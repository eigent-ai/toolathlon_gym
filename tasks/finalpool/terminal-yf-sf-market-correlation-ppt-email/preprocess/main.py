"""Preprocess for terminal-yf-sf-market-correlation-ppt-email.
Clears email writable schema. Injects noise emails. Snowflake and Yahoo Finance are read-only."""
import argparse
import json
import os
import glob as globmod
import uuid
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
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
        conn.commit()
        print("[preprocess] Cleared email data.")

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name='INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            inbox_id = row[0]
            noise_emails = [
                ("Team Lunch Friday", "admin@company.com",
                 json.dumps(["all@company.com"]),
                 "Reminder: team lunch this Friday at noon in the cafeteria."),
                ("Office Supply Order", "procurement@company.com",
                 json.dumps(["dept-heads@company.com"]),
                 "Please submit your office supply requests by end of week."),
                ("Parking Lot Maintenance", "facilities@company.com",
                 json.dumps(["all@company.com"]),
                 "Lot B will be closed for resurfacing next Monday."),
            ]
            for subj, from_addr, to_addr, body in noise_emails:
                cur.execute(
                    "INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, "
                    "body_text, is_read, date) VALUES (%s, %s, %s, %s, %s, %s, false, now())",
                    (inbox_id, f"noise-{uuid.uuid4()}@company.com", subj, from_addr, to_addr, body))
            conn.commit()
            print("[preprocess] Injected 3 noise emails.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Market_Correlation_Report.pptx", "correlation_analysis.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
