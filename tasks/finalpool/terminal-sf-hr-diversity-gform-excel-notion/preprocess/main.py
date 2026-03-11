"""Preprocess for terminal-sf-hr-diversity-gform-excel-notion.
SF HR data is read-only. Clear gform and notion, inject noise data."""
import argparse
import glob
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


def clear_gform(cur):
    print("[preprocess] Clearing Google Forms data...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")


def clear_notion(cur):
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")


def inject_noise(cur):
    print("[preprocess] Injecting noise data...")
    # Noise Google Form
    noise_form_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO gform.forms (id, title, description)
        VALUES (%s, 'Employee Satisfaction Survey Q4', 'Quarterly satisfaction check')
    """, (noise_form_id,))
    for i, (title, qtype) in enumerate([
        ("How satisfied are you with your role?", "MULTIPLE_CHOICE"),
        ("Rate your work-life balance", "MULTIPLE_CHOICE"),
        ("Any additional comments?", "TEXT"),
    ]):
        cur.execute("""
            INSERT INTO gform.questions (form_id, title, question_type, required, position)
            VALUES (%s, %s, %s, false, %s)
        """, (noise_form_id, title, qtype, i))

    # Noise Notion database
    noise_db_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO notion.databases (id, object, title, properties, parent, archived, is_inline)
        VALUES (%s, 'database', %s, '{}', '{"type":"page_id","page_id":"root"}', false, false)
    """, (noise_db_id, json.dumps([{"type": "text", "text": {"content": "Q4 Project Tracker"}}])))

    for project in ["Website Redesign", "API Migration", "Data Pipeline"]:
        page_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.pages (id, object, parent, archived, in_trash, properties)
            VALUES (%s, 'page', %s, false, false, %s)
        """, (page_id, json.dumps({"type": "database_id", "database_id": noise_db_id}),
              json.dumps({"Name": {"title": [{"text": {"content": project}}]}})))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_gform(cur)
        clear_notion(cur)
        inject_noise(cur)
        conn.commit()
        print("[preprocess] DB setup done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Diversity_Metrics_Report.xlsx", "diversity_*.py", "diversity_*.json", "dept_*.json"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
