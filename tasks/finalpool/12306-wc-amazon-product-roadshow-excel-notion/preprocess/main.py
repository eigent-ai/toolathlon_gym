"""
Preprocess for 12306-wc-amazon-product-roadshow-excel-notion task.

Injects:
  - 3 emails from distributors and manager
  - 1 gcal event: Internal Product Review 2026-03-09 14:00-16:00
  - Clears email, notion, gcal tables before injecting

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
import json
import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

GCAL_EVENTS = [
    {
        "summary": "Internal Product Review",
        "description": "Pre-roadshow internal product review meeting. Finalize demonstration products and pricing for Shanghai and Guangzhou distributor meetings.",
        "start": "2026-03-09 14:00:00",
        "end": "2026-03-09 16:00:00",
    },
]

EMAILS = [
    {
        "message_id": "msg-shanghai-dist-001",
        "subject": "Meeting Availability - Shanghai Office",
        "from_addr": "shanghai_dist@partner.com",
        "to_addr": ["bd@techstoreonline.com"],
        "date": "2026-03-05 09:30:00+00",
        "body_text": (
            "Hello,\n\n"
            "We received your inquiry about a product demonstration visit. Our Shanghai office is available "
            "on March 10, 2026 from 14:00 to 17:00. Please confirm if this time works for your team. "
            "We are particularly interested in your wireless audio and mobile accessories lines. "
            "Could you send us a product catalog in advance?\n\n"
            "Best regards,\nShanghai Distribution Team\nshanghai_dist@partner.com"
        ),
    },
    {
        "message_id": "msg-guangzhou-dist-001",
        "subject": "Product Catalog Request - Guangzhou",
        "from_addr": "guangzhou_dist@partner.com",
        "to_addr": ["bd@techstoreonline.com"],
        "date": "2026-03-06 11:00:00+00",
        "body_text": (
            "Dear Business Development Team,\n\n"
            "We heard that TechStore Online is planning a southern China roadshow. We are very interested "
            "in becoming a regional distributor for your top products. Could you please send us your "
            "current product catalog and pricing sheet? We are especially interested in smart devices "
            "and computing accessories that are popular in the Guangdong market.\n\n"
            "Looking forward to hearing from you,\nGuangzhou Distribution\nguangzhou_dist@partner.com"
        ),
    },
    {
        "message_id": "msg-manager-001",
        "subject": "Roadshow Update Request",
        "from_addr": "manager@company.com",
        "to_addr": ["bd@techstoreonline.com"],
        "date": "2026-03-07 08:00:00+00",
        "body_text": (
            "Hi,\n\n"
            "Can you please send me an update on the Shanghai and Guangzhou roadshow plan? "
            "I need to see the travel itinerary, which products we are featuring, and who the key contacts are. "
            "Please also confirm the total expected travel cost and the meeting schedule. "
            "I would like to review everything before you depart.\n\n"
            "Thanks,\nManager\nmanager@company.com"
        ),
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared gcal, notion, email tables.")


def inject_gcal_events(conn):
    with conn.cursor() as cur:
        for ev in GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime,
                    start_timezone, end_timezone, creator, organizer, attendees)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
            """, (
                ev["summary"], ev["description"], ev["start"], ev["end"],
                "Asia/Shanghai", "Asia/Shanghai",
                json.dumps({}), json.dumps({}), json.dumps([]),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(GCAL_EVENTS)} GCal events.")


def inject_emails(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()
            cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
            row = cur.fetchone()
        folder_id = row[0]

        for em in EMAILS:
            cur.execute("""
                INSERT INTO email.messages (message_id, subject, from_addr, to_addr, date, body_text, folder_id)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s)
                ON CONFLICT (message_id) DO NOTHING
            """, (
                em["message_id"], em["subject"], em["from_addr"],
                json.dumps(em["to_addr"]), em["date"], em["body_text"], folder_id,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(EMAILS)} emails.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal_events(conn)
        inject_emails(conn)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
