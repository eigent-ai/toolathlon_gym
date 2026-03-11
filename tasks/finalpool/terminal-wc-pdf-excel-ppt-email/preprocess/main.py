"""Preprocess for terminal-wc-pdf-excel-ppt-email.
Clears email. WooCommerce is read-only. Injects noise emails."""
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
        # Clear email
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        print("[preprocess] Cleared email data.")

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            folder_id = row[0]
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM email.messages")
            max_id = cur.fetchone()[0]

            noise_emails = [
                (max_id + 1, "Weekly Sales Digest", "sales@company.com",
                 json.dumps(["team@company.com"]),
                 "Here is the weekly sales summary for your review."),
                (max_id + 2, "Office Maintenance Notice", "facilities@company.com",
                 json.dumps(["all@company.com"]),
                 "The office HVAC system will be serviced this weekend."),
                (max_id + 3, "Supplier Invoice #INV-2026-0315", "accounts@supplier.com",
                 json.dumps(["finance@company.com"]),
                 "Please find attached the invoice for recent shipments."),
                (max_id + 4, "Team Building Event", "hr@company.com",
                 json.dumps(["team@company.com"]),
                 "Join us for the quarterly team building event next Friday."),
            ]
            for eid, subj, from_addr, to_addr, body in noise_emails:
                cur.execute("""
                    INSERT INTO email.messages (id, folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW(), %s, false)
                """, (eid, folder_id, f"noise-{uuid.uuid4()}@company.com",
                      subj, from_addr, to_addr, body))
            print("[preprocess] Injected 4 noise emails.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up agent workspace if provided
    if args.agent_workspace:
        for pattern in ["Recall_Impact_Assessment.xlsx", "Recall_Briefing.pptx",
                        "recall_analysis.py", "customer_impact.py",
                        "recall_impact.json", "customer_impact.json"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
