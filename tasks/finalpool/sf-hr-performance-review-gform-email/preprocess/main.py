"""
Preprocess for sf-hr-performance-review-gform-email task.

Injects:
  - GForm "Annual Performance Review Form" with 6 questions
  - Clears email tables

Snowflake data is read-only; no injection needed.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import os
import argparse
import json
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

FORM_TITLE = "Annual Performance Review Form"
FORM_QUESTIONS = [
    {
        "title": "Employee ID",
        "question_type": "SHORT_ANSWER",
        "required": True,
        "config": {},
        "position": 0,
    },
    {
        "title": "Department",
        "question_type": "RADIO",
        "required": True,
        "config": {"options": ["Engineering", "Finance", "HR", "Operations", "R&D", "Sales", "Support"]},
        "position": 1,
    },
    {
        "title": "Performance Rating",
        "question_type": "RADIO",
        "required": True,
        "config": {
            "options": [
                "1-Needs Improvement",
                "2-Below Expectations",
                "3-Meets Expectations",
                "4-Exceeds Expectations",
                "5-Outstanding",
            ]
        },
        "position": 2,
    },
    {
        "title": "Key Achievements this year",
        "question_type": "PARAGRAPH",
        "required": True,
        "config": {},
        "position": 3,
    },
    {
        "title": "Areas for Improvement",
        "question_type": "PARAGRAPH",
        "required": False,
        "config": {},
        "position": 4,
    },
    {
        "title": "Goals for next year",
        "question_type": "PARAGRAPH",
        "required": False,
        "config": {},
        "position": 5,
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared gform and email tables.")


def inject_gform(conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO gform.forms (title, document_title, description)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (
            FORM_TITLE,
            FORM_TITLE,
            "Complete this form as part of the annual performance review process.",
        ))
        form_id = cur.fetchone()[0]

        for q in FORM_QUESTIONS:
            cur.execute("""
                INSERT INTO gform.questions (form_id, title, question_type, required, config, position)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
            """, (form_id, q["title"], q["question_type"], q["required"],
                  json.dumps(q["config"]), q["position"]))

    conn.commit()
    print(f"[preprocess] Injected GForm '{FORM_TITLE}' with {len(FORM_QUESTIONS)} questions")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gform(conn)
        ensure_email_folder(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
