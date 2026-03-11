"""Preprocess for terminal-canvas-gform-gcal-excel-email.
Clears gform, gcal, and email data. Injects noise emails and a GForm with responses.
"""
import argparse
import json
import uuid

import os
import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432,
          dbname=os.environ.get("PGDATABASE", "toolathlon_gym"), user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        # Clear writable schemas
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM email.drafts")
        conn.commit()
        print("[preprocess] Cleared gform, gcal, email schemas.")

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name='INBOX' LIMIT 1")
        inbox_id = cur.fetchone()[0]

        noise_emails = [
            ("Weekly Staff Meeting Reminder", "admin@university.edu",
             json.dumps(["all-staff@university.edu"]),
             "Reminder: weekly staff meeting tomorrow at 10am in Room 204."),
            ("Library System Maintenance", "it@university.edu",
             json.dumps(["faculty@university.edu"]),
             "The library system will be offline for maintenance this Saturday."),
            ("Campus Parking Update", "facilities@university.edu",
             json.dumps(["all@university.edu"]),
             "New parking regulations take effect next month. Please review the updated policy."),
            ("Research Grant Deadline", "grants@university.edu",
             json.dumps(["researchers@university.edu"]),
             "The deadline for submitting Spring 2026 research grant proposals is April 15."),
        ]
        for subj, from_addr, to_addr, body in noise_emails:
            cur.execute(
                "INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, "
                "body_text, is_read, date) VALUES (%s, %s, %s, %s, %s, %s, false, now())",
                (inbox_id, f"noise-{uuid.uuid4()}@university.edu", subj, from_addr, to_addr, body)
            )
        conn.commit()
        print("[preprocess] Injected 4 noise emails.")

        # Inject a GForm with study habit responses (existing survey the agent should find)
        form_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO gform.forms (id, title, document_title) VALUES (%s, %s, %s)",
            (form_id, "Previous Semester Study Habits Survey", "Study Habits Survey")
        )
        q1_id = str(uuid.uuid4())
        q2_id = str(uuid.uuid4())
        q3_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO gform.questions (id, form_id, title, question_type, position) "
            "VALUES (%s, %s, %s, %s, %s)",
            (q1_id, form_id, "How do you usually prepare for quizzes?", "SHORT_ANSWER", 1)
        )
        cur.execute(
            "INSERT INTO gform.questions (id, form_id, title, question_type, position) "
            "VALUES (%s, %s, %s, %s, %s)",
            (q2_id, form_id, "Rate your confidence level (1-5)", "SCALE", 2)
        )
        cur.execute(
            "INSERT INTO gform.questions (id, form_id, title, question_type, position) "
            "VALUES (%s, %s, %s, %s, %s)",
            (q3_id, form_id, "Preferred study time", "MULTIPLE_CHOICE", 3)
        )
        # Add some responses
        for i in range(5):
            resp_id = str(uuid.uuid4())
            answers = {
                q1_id: f"Response {i+1}: Review notes and practice problems",
                q2_id: str(3 + (i % 3)),
                q3_id: ["Morning", "Evening", "Afternoon", "Night", "Weekend"][i]
            }
            cur.execute(
                "INSERT INTO gform.responses (id, form_id, respondent_email, answers) "
                "VALUES (%s, %s, %s, %s)",
                (resp_id, form_id, f"student{i+1}@university.edu", json.dumps(answers))
            )
        conn.commit()
        print("[preprocess] Injected noise GForm with 5 responses.")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
