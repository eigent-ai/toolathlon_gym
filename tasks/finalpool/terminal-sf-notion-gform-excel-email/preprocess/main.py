"""Preprocess script for terminal-sf-notion-gform-excel-email task.
Snowflake HR is read-only. Clear notion, gform, email schemas.
"""
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


def clear_notion(cur):
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    print("[preprocess] Notion data cleared.")


def clear_gform(cur):
    print("[preprocess] Clearing Google Forms data...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    print("[preprocess] Google Forms data cleared.")


def clear_emails(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages WHERE folder_id != 0")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    print("[preprocess] Email data cleared.")


def inject_noise(cur):
    """Inject noise data into email and notion schemas."""
    # Email noise
    cur.execute("SELECT id FROM email.folders WHERE name='INBOX' LIMIT 1")
    row = cur.fetchone()
    if row:
        inbox_id = row[0]
    else:
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        inbox_id = cur.fetchone()[0]
    noise_emails = [
        ("Weekly Staff Meeting", "admin@company.com", json.dumps(["all@company.com"]), "Meeting tomorrow at 10am."),
        ("Parking Update", "facilities@company.com", json.dumps(["all@company.com"]), "New regulations next month."),
    ]
    for subj, from_addr, to_addr, body in noise_emails:
        cur.execute("INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, body_text, is_read, date) VALUES (%s, %s, %s, %s, %s, %s, false, now())",
            (inbox_id, f"noise-{uuid.uuid4()}@company.com", subj, from_addr, to_addr, body))

    # Notion noise
    page_id = str(uuid.uuid4())
    props = {"title": {"title": [{"type": "text", "text": {"content": "Unrelated Meeting Notes"}, "plain_text": "Unrelated Meeting Notes"}]}}
    cur.execute("INSERT INTO notion.pages (id, properties) VALUES (%s, %s::jsonb)", (page_id, json.dumps(props)))
    bid = str(uuid.uuid4())
    cur.execute("INSERT INTO notion.blocks (id, parent_type, parent_id, type, block_data, position) VALUES (%s, %s, %s, %s, %s::jsonb, %s)",
        (bid, "page_id", page_id, "paragraph", json.dumps({"rich_text": [{"type": "text", "text": {"content": "Unrelated content about office supplies"}, "plain_text": "Unrelated content about office supplies"}]}), 0))
    print("[preprocess] Injected noise data.")


def inject_survey_responses(cur):
    """Inject 5 pre-filled survey responses into gform."""
    import uuid
    import json

    print("[preprocess] Injecting survey responses...")
    form_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO gform.forms (id, title, description)
        VALUES (%s, 'Pre-existing Engagement Survey', 'Old survey data for reference')
    """, (form_id,))

    q_ids = []
    questions = [
        ("Role satisfaction rating", "SCALE"),
        ("Work-life balance", "MULTIPLE_CHOICE"),
        ("Career growth rating", "MULTIPLE_CHOICE"),
        ("Manager support rating", "SCALE"),
        ("Company recommendation", "MULTIPLE_CHOICE"),
    ]
    for i, (title, qtype) in enumerate(questions):
        cur.execute("""
            INSERT INTO gform.questions (form_id, title, question_type, required, position)
            VALUES (%s, %s, %s, true, %s) RETURNING id
        """, (form_id, title, qtype, i))
        q_ids.append(cur.fetchone()[0])

    responses = [
        {"q0": "8", "q1": "Satisfied", "q2": "Good", "q3": "4", "q4": "Yes"},
        {"q0": "6", "q1": "Neutral", "q2": "Fair", "q3": "3", "q4": "Maybe"},
        {"q0": "9", "q1": "Very Satisfied", "q2": "Excellent", "q3": "5", "q4": "Yes"},
        {"q0": "5", "q1": "Dissatisfied", "q2": "Poor", "q3": "2", "q4": "No"},
        {"q0": "7", "q1": "Satisfied", "q2": "Good", "q3": "4", "q4": "Yes"},
    ]
    for j, resp in enumerate(responses):
        answers = {}
        for k, qid in enumerate(q_ids):
            answers[str(qid)] = {"questionId": str(qid), "textAnswers": {"answers": [{"value": resp[f"q{k}"]}]}}
        cur.execute("""
            INSERT INTO gform.responses (form_id, respondent_email, answers)
            VALUES (%s, %s, %s)
        """, (form_id, f"employee{j+1}@company.com", json.dumps(answers)))

    print("[preprocess] Injected 5 survey responses.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_notion(cur)
        clear_gform(cur)
        clear_emails(cur)
        inject_survey_responses(cur)
        inject_noise(cur)
        conn.commit()
        print("[preprocess] DB cleanup done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Employee_Engagement_Report.xlsx", "engagement_analysis_output.txt"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
