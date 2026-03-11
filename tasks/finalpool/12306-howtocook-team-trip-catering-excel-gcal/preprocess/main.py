"""
Preprocess for 12306-howtocook-team-trip-catering-excel-gcal task.

Clears and injects:
- 2 gcal events (existing company calendar context)
- 1 email from events@company.com asking for coordination plan
- Clears notion pages
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
        cur.execute("DELETE FROM notion.pages")
    conn.commit()
    print("[preprocess] Cleared email, gcal, notion tables.")


def get_or_create_inbox(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        conn.commit()
        return cur.fetchone()[0]


def inject_gcal_events(conn):
    events = [
        {
            "id": str(uuid.uuid4()),
            "summary": "Monthly All-Hands Meeting",
            "start_datetime": "2026-03-10T09:00:00+08:00",
            "end_datetime": "2026-03-10T10:00:00+08:00",
            "start_timezone": "Asia/Shanghai",
            "end_timezone": "Asia/Shanghai",
            "creator": json.dumps({"email": "admin@company.com"}),
            "organizer": json.dumps({"email": "admin@company.com"}),
            "attendees": json.dumps([{"email": "all@company.com"}]),
            "description": "Monthly company all-hands meeting. Note: team building trip members will be traveling and will miss this.",
            "location": "Beijing HQ Conference Room A",
        },
        {
            "id": str(uuid.uuid4()),
            "summary": "Shanghai Partner Strategy Meeting",
            "start_datetime": "2026-03-10T15:00:00+08:00",
            "end_datetime": "2026-03-10T16:00:00+08:00",
            "start_timezone": "Asia/Shanghai",
            "end_timezone": "Asia/Shanghai",
            "creator": json.dumps({"email": "bd@company.com"}),
            "organizer": json.dumps({"email": "bd@company.com"}),
            "attendees": json.dumps([{"email": "events@company.com"}, {"email": "partner@shanghai.com"}]),
            "description": "Strategy alignment meeting with Shanghai partner. This is the primary reason for the team trip to Shanghai.",
            "location": "Shanghai Partner Office",
        },
    ]
    with conn.cursor() as cur:
        for ev in events:
            cur.execute("""
                INSERT INTO gcal.events
                    (id, summary, start_datetime, end_datetime, start_timezone, end_timezone,
                     creator, organizer, attendees, description, location)
                VALUES (%s, %s, %s::timestamptz, %s::timestamptz, %s, %s,
                        %s::jsonb, %s::jsonb, %s::jsonb, %s, %s)
            """, (
                ev["id"], ev["summary"],
                ev["start_datetime"], ev["end_datetime"],
                ev["start_timezone"], ev["end_timezone"],
                ev["creator"], ev["organizer"], ev["attendees"],
                ev["description"], ev["location"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(events)} gcal events.")


def inject_email(conn, folder_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
            VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), %s)
        """, (
            folder_id,
            str(uuid.uuid4()),
            "Team Building Trip to Shanghai - Coordination Needed",
            "events@company.com",
            json.dumps(["coordinator@company.com"]),
            (
                "Hi,\n\nWe are planning a team building trip from Beijing to Shanghai on March 10, 2026 "
                "for 15 team members. We need you to coordinate the full plan including train tickets, "
                "a team dinner menu, and a day schedule.\n\n"
                "Please prepare:\n"
                "1. Rail travel plan (prefer the early G11 train departing 07:00)\n"
                "2. A catered team dinner menu for the evening (around 18:00)\n"
                "3. A full day timeline in Excel\n"
                "4. Post the plan to our team knowledge base\n"
                "5. Add all activities to the shared calendar\n\n"
                "Budget reference: 800 CNY per person for travel.\n\n"
                "Please send the completed plan back to this email.\n\nThanks,\nevents@company.com"
            ),
        ))
    conn.commit()
    print("[preprocess] Injected request email.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gcal_events(conn)
        folder_id = get_or_create_inbox(conn)
        inject_email(conn, folder_id)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
