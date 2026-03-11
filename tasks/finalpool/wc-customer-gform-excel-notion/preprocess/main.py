"""Preprocess script for wc-customer-gform-excel-notion."""
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
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
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
    # Noise gform data
    cur.execute("""INSERT INTO gform.forms (id, title, document_title, description)
        VALUES ('noise-form-001', 'Office Supply Request', 'Office Supply Request', 'Internal office supply request form')""")
    cur.execute("""INSERT INTO gform.questions (id, form_id, title, question_type, required, position)
        VALUES ('noise-q1', 'noise-form-001', 'What supplies do you need?', 'TEXT', true, 0)""")
    cur.execute("""INSERT INTO gform.questions (id, form_id, title, question_type, required, position)
        VALUES ('noise-q2', 'noise-form-001', 'Urgency level?', 'RADIO', false, 1)""")
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