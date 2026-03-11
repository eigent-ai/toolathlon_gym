"""Preprocess script for terminal-canvas-pdf-excel-notion-gcal."""
import os
import argparse, json, os, uuid
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
    # Clear notion
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    # Clear gcal
    cur.execute("DELETE FROM gcal.events")
    conn.commit()
    cur.close()
    conn.close()
    print("[preprocess] Cleared notion and gcal schemas")


def inject_noise_data(launch_time):
    conn = get_conn()
    cur = conn.cursor()
    launch_dt = datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S")

    # Noise Notion database - unrelated project tracker
    noise_db_id = str(uuid.uuid4())
    cur.execute("""INSERT INTO notion.databases (id, title, description, properties, parent)
        VALUES (%s, %s, %s, %s, %s)""",
        (noise_db_id,
         json.dumps([{"type": "text", "text": {"content": "Project Milestones"}}]),
         json.dumps([{"type": "text", "text": {"content": "Track project deadlines"}}]),
         json.dumps({
             "Name": {"id": "title", "type": "title", "title": {}},
             "Status": {"id": "status", "type": "select", "select": {"options": [
                 {"name": "Open"}, {"name": "Closed"}
             ]}},
         }),
         json.dumps({"type": "workspace", "workspace": True})))

    # Noise notion pages
    for i, (title, status) in enumerate([
        ("Q1 Budget Review", "Open"),
        ("Server Migration", "Closed"),
        ("Marketing Campaign Launch", "Open"),
    ]):
        page_id = str(uuid.uuid4())
        cur.execute("""INSERT INTO notion.pages (id, parent, properties, archived) VALUES (%s, %s, %s, false)""",
            (page_id,
             json.dumps({"type": "database_id", "database_id": noise_db_id}),
             json.dumps({
                 "Name": {"id": "title", "type": "title", "title": [{"type": "text", "text": {"content": title}}]},
                 "Status": {"id": "status", "type": "select", "select": {"name": status}},
             })))

    # Noise calendar events
    cur.execute("""INSERT INTO gcal.events (summary, description, start_datetime, end_datetime, status)
        VALUES (%s, %s, %s, %s, %s)""",
        ("Department Budget Meeting",
         "Quarterly budget review with finance team",
         launch_dt + timedelta(days=5),
         launch_dt + timedelta(days=5, hours=1),
         "confirmed"))

    cur.execute("""INSERT INTO gcal.events (summary, description, start_datetime, end_datetime, status)
        VALUES (%s, %s, %s, %s, %s)""",
        ("Faculty Retreat Planning",
         "Plan upcoming faculty retreat activities",
         launch_dt + timedelta(days=12),
         launch_dt + timedelta(days=12, hours=2),
         "confirmed"))

    # An existing accreditation-related event (noise but relevant topic)
    cur.execute("""INSERT INTO gcal.events (summary, description, start_datetime, end_datetime, status)
        VALUES (%s, %s, %s, %s, %s)""",
        ("Accreditation Committee Meeting",
         "Initial discussion about upcoming accreditation review timeline",
         launch_dt - timedelta(days=10),
         launch_dt - timedelta(days=10) + timedelta(hours=1),
         "confirmed"))

    conn.commit()
    cur.close()
    conn.close()
    print("[preprocess] Noise data injected (notion: 1 db + 3 pages, gcal: 3 events)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    clear_writable_schemas()
    inject_noise_data(args.launch_time)


if __name__ == "__main__":
    main()
