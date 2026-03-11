"""
Preprocess for 12306-yf-investor-roadshow-excel-ppt-email task.

Clears and injects:
- 2 emails (from investors@fundmanager.com and shanghai_partners@finance.com)
"""
import argparse
import json
import os
import uuid
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM email.attachments")
        try:
            cur.execute("DELETE FROM email.sent_log")
        except Exception:
            pass
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared email tables.")


def get_or_create_inbox(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        conn.commit()
        return cur.fetchone()[0]


def inject_emails(conn, folder_id):
    emails = [
        {
            "subject": "Q1 2026 Roadshow - Schedule Request",
            "from_addr": "investors@fundmanager.com",
            "to_addr": json.dumps(["analyst@firm.com"]),
            "body": (
                "Dear Analyst,\n\n"
                "We are excited to participate in the Q1 2026 investor roadshow. Could you please "
                "send us the confirmed schedule, including travel dates, arrival times, and meeting agenda? "
                "We would also appreciate receiving the financial presentation and supporting materials "
                "in advance so our team can prepare relevant questions.\n\n"
                "We are particularly interested in the revenue and earnings per share trends, "
                "as well as any forward guidance.\n\n"
                "Best regards,\ninvestors@fundmanager.com"
            ),
        },
        {
            "subject": "Availability Confirmed - March 10 Meeting",
            "from_addr": "shanghai_partners@finance.com",
            "to_addr": json.dumps(["analyst@firm.com"]),
            "body": (
                "Hi,\n\n"
                "We confirm availability for a meeting on March 10, 2026 at our Shanghai office. "
                "We can accommodate you any time after 13:30. Please let us know the confirmed time "
                "once you have your travel arrangements finalized. We look forward to discussing "
                "the quarterly results and investment outlook.\n\n"
                "Best,\nshanghai_partners@finance.com"
            ),
        },
    ]
    with conn.cursor() as cur:
        for em in emails:
            cur.execute("""
                INSERT INTO email.messages
                    (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), %s)
            """, (
                folder_id,
                str(uuid.uuid4()),
                em["subject"], em["from_addr"], em["to_addr"], em["body"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(emails)} emails.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        folder_id = get_or_create_inbox(conn)
        inject_emails(conn, folder_id)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
