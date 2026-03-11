"""Preprocess script for sf-hr-satisfaction-gform-excel-gcal."""
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
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
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
    # Noise gform data
    cur.execute("""INSERT INTO gform.forms (id, title, document_title, description)
        VALUES ('noise-form-001', 'Office Supply Request', 'Office Supply Request', 'Internal office supply request form')""")
    cur.execute("""INSERT INTO gform.questions (id, form_id, title, question_type, required, position)
        VALUES ('noise-q1', 'noise-form-001', 'What supplies do you need?', 'TEXT', true, 0)""")
    cur.execute("""INSERT INTO gform.questions (id, form_id, title, question_type, required, position)
        VALUES ('noise-q2', 'noise-form-001', 'Urgency level?', 'RADIO', false, 1)""")
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