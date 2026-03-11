"""
Preprocess for terminal-canvas-howtocook-gsheet-notion-email task.

Clears gsheet, notion, email schemas. Injects noise data in each.
Canvas and HowToCook are read-only.
"""
import argparse
import os
import uuid
from datetime import datetime, timedelta

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_schemas(conn):
    with conn.cursor() as cur:
        # Clear gsheet
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        # Clear notion
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        # Clear email
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
    conn.commit()
    print("[preprocess] Cleared gsheet, notion, email schemas.")


def inject_noise_gsheet(conn):
    """Inject a noise spreadsheet the agent should ignore."""
    with conn.cursor() as cur:
        ss_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)",
            (ss_id, "Budget Tracking Q1 2026"),
        )
        cur.execute(
            "INSERT INTO gsheet.sheets (spreadsheet_id, title, index, row_count, column_count) "
            "VALUES (%s, %s, 0, 10, 4) RETURNING id",
            (ss_id, "Q1_Budget"),
        )
        sheet_id = cur.fetchone()[0]
        for i, (label, val) in enumerate(
            [("Department", "Marketing"), ("Budget", "45000"), ("Spent", "31200"), ("Remaining", "13800")]
        ):
            cur.execute(
                "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) "
                "VALUES (%s, %s, 0, %s, %s)",
                (ss_id, sheet_id, i, label),
            )
            cur.execute(
                "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) "
                "VALUES (%s, %s, 1, %s, %s)",
                (ss_id, sheet_id, i, val),
            )
    conn.commit()
    print("[preprocess] Injected noise gsheet data.")


def inject_noise_notion(conn):
    """Inject a noise Notion database the agent should ignore."""
    with conn.cursor() as cur:
        db_id = str(uuid.uuid4())
        cur.execute(
            """INSERT INTO notion.databases (id, title, description, properties, parent)
            VALUES (%s, %s, %s, %s, %s)""",
            (
                db_id,
                '[{"type": "text", "text": {"content": "Department Projects"}}]',
                '[{"type": "text", "text": {"content": "Internal project tracker"}}]',
                '{"Name": {"title": {}}, "Status": {"select": {"options": [{"name": "Open"}, {"name": "Closed"}]}}}',
                '{"type": "workspace", "workspace": true}',
            ),
        )
        page_id = str(uuid.uuid4())
        cur.execute(
            """INSERT INTO notion.pages (id, parent, properties, archived)
            VALUES (%s, %s, %s, false)""",
            (
                page_id,
                f'{{"type": "database_id", "database_id": "{db_id}"}}',
                '{"Name": {"title": [{"text": {"content": "Website Redesign"}}]}, "Status": {"select": {"name": "Open"}}}',
            ),
        )
    conn.commit()
    print("[preprocess] Injected noise notion data.")


def inject_noise_email(conn, launch):
    """Inject noise emails the agent should ignore."""

    def dt(days, hours, minutes=0):
        return (launch + timedelta(days=days, hours=hours, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")

    # Offsets from launch_time (default 2026-03-07 10:00:00):
    # Mar 1 09:00 = launch - 6d - 1h
    # Mar 3 14:30 = launch - 3d - 19h - 30m  (equivalently -4d +4h +30m)
    # Mar 5 11:00 = launch - 2d + 1h
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
            VALUES
            ((SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1),
             'noise-msg-001', 'Q1 Budget Review Meeting', 'finance@university.edu',
             '["admin@university.edu"]', %s, 'Please review the attached Q1 budget report before our meeting next week.', true),
            ((SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1),
             'noise-msg-002', 'Campus Parking Update', 'facilities@university.edu',
             '["all_staff@university.edu"]', %s, 'Starting March 15, lot B will be closed for resurfacing. Please use lot C instead.', true),
            ((SELECT id FROM email.folders WHERE name = 'Sent' LIMIT 1),
             'noise-msg-003', 'Re: Faculty Retreat Planning', 'dean@university.edu',
             '["faculty_committee@university.edu"]', %s, 'The retreat is confirmed for April 20. Please submit your session proposals by March 25.', true)
            """,
            (dt(-6, -1), dt(-4, 4, 30), dt(-2, 1)),
        )
    conn.commit()
    print("[preprocess] Injected noise email data.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    launch = datetime.strptime(args.launch_time or "2026-03-07 10:00:00", "%Y-%m-%d %H:%M:%S")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_schemas(conn)
        inject_noise_gsheet(conn)
        inject_noise_notion(conn)
        inject_noise_email(conn, launch)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
