"""Preprocess script for sf-notion-project-tracker-excel-gcal-email."""
import os
import argparse, json, os, sys, shutil, subprocess, time
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel"
}

TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_conn():
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)

def clear_writable_schemas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM gcal.events")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    conn.commit()
    cur.close()
    conn.close()

def inject_data(launch_time):
    conn = get_conn()
    cur = conn.cursor()
    launch_dt = datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S")
    cur.execute("""INSERT INTO gcal.events (summary, start_datetime, end_datetime, status)
        VALUES ('Team Standup', %s, %s, 'confirmed')""",
        (launch_dt.replace(hour=9), launch_dt.replace(hour=9, minute=30)))
    cur.execute("""INSERT INTO gcal.events (summary, start_datetime, end_datetime, status)
        VALUES ('Lunch Break', %s, %s, 'confirmed')""",
        (launch_dt.replace(hour=12), launch_dt.replace(hour=13)))
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    row = cur.fetchone()
    inbox_id = row[0] if row else 1
    cur.execute("""INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
        VALUES (%s, '<noise-001@co.com>', 'Weekly Newsletter', 'newsletter@company.com', %s, %s, 'This week updates...', true)""",
        (inbox_id, json.dumps(['all@company.com']), launch_dt - timedelta(hours=5)))
    cur.execute("""INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
        VALUES (%s, '<noise-002@co.com>', 'Server Maintenance', 'ops@company.com', %s, %s, 'Planned maintenance Saturday', false)""",
        (inbox_id, json.dumps(['team@company.com']), launch_dt - timedelta(hours=3)))
    # Noise notion data
    cur.execute("""INSERT INTO notion.pages (id, parent, properties, archived)
        VALUES ('noise-page-001',
        '{"type": "workspace", "workspace": true}'::jsonb,
        '{"title": {"id": "title", "type": "title", "title": [{"type": "text", "text": {"content": "Meeting Notes Archive"}}]}}'::jsonb,
        false)""")
    conn.commit()
    cur.close()
    conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    clear_writable_schemas()
    inject_data(args.launch_time)

if __name__ == "__main__":
    main()