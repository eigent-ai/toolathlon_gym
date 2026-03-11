"""
Preprocess for 12306-wc-supplier-visit-excel-email-gcal task.

Clears and injects:
- 2 emails (from shanghai and guangzhou suppliers)
- 1 gcal event (procurement team meeting before departure)
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
        cur.execute("DELETE FROM gcal.events")
    conn.commit()
    print("[preprocess] Cleared email and gcal tables.")


def get_or_create_inbox(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        conn.commit()
        return cur.fetchone()[0]


def inject_gcal_event(conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gcal.events
                (id, summary, start_datetime, end_datetime, start_timezone, end_timezone,
                 creator, organizer, attendees, description, location)
            VALUES (%s, %s, %s::timestamptz, %s::timestamptz, %s, %s,
                    %s::jsonb, %s::jsonb, %s::jsonb, %s, %s)
        """, (
            str(uuid.uuid4()),
            "Procurement Team Pre-Trip Briefing",
            "2026-03-10T09:00:00+08:00",
            "2026-03-10T10:00:00+08:00",
            "Asia/Shanghai",
            "Asia/Shanghai",
            json.dumps({"email": "procurement@company.com"}),
            json.dumps({"email": "procurement@company.com"}),
            json.dumps([{"email": "buyer@company.com"}]),
            "Pre-trip briefing before departing for supplier visits. Review visit goals and confirm supplier contacts.",
            "Beijing HQ Meeting Room B",
        ))
    conn.commit()
    print("[preprocess] Injected 1 gcal event.")


def inject_emails(conn, folder_id):
    emails = [
        {
            "subject": "Re: Supplier Visit - March Schedule",
            "from_addr": "shanghai_supplier@techworld.com",
            "to_addr": json.dumps(["buyer@company.com"]),
            "body": (
                "Dear Buyer,\n\n"
                "Thank you for being a valued customer. We have noticed your recent orders and "
                "would love to discuss a long-term supply agreement. Our team is available "
                "for an in-person meeting at our Shanghai facility any day next week. "
                "Please let us know your preferred date and time.\n\n"
                "Best regards,\nTechWorld Electronics - Shanghai Office"
            ),
        },
        {
            "subject": "New Supplier Introduction",
            "from_addr": "gz_supplier@supplier.com",
            "to_addr": json.dumps(["buyer@company.com"]),
            "body": (
                "Hello,\n\n"
                "We are a Guangzhou-based electronics components supplier and we came across "
                "your store through a trade directory. We believe our product range matches "
                "several of your high-volume categories. We would be happy to arrange a visit "
                "at our Guangzhou warehouse to show you our full catalog and discuss pricing.\n\n"
                "Please contact us to schedule a meeting.\n\n"
                "Best,\ngz_supplier@supplier.com"
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
        inject_gcal_event(conn)
        folder_id = get_or_create_inbox(conn)
        inject_emails(conn, folder_id)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
