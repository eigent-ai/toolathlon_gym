"""
Preprocess for howtocook-event-catering-excel-word task.

Injects a Google Form "Menu Approval Survey" with 3 questions.
Clears email tables.

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

FORM_TITLE = "Menu Approval Survey"
FORM_QUESTIONS = [
    {
        "title": "How would you rate the overall menu selection for the team building event?",
        "question_type": "RADIO",
        "required": True,
        "config": {"options": ["Excellent", "Good", "Satisfactory", "Needs Improvement"]},
        "position": 0,
    },
    {
        "title": "Which dishes would you like to confirm or remove from the menu?",
        "question_type": "PARAGRAPH",
        "required": False,
        "config": {},
        "position": 1,
    },
    {
        "title": "Please note any special dietary requirements or additional requests.",
        "question_type": "PARAGRAPH",
        "required": False,
        "config": {},
        "position": 2,
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
            "Please review the proposed catering menu for the corporate team building event.",
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
