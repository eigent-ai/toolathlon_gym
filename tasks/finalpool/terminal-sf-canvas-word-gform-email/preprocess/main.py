"""Preprocess for terminal-sf-canvas-word-gform-email.
Clears gform and email. Injects survey form with 5 questions and 15 responses. Injects noise emails."""
import argparse
import json
import os
import uuid

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432,
          dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
          user="eigent", password="camel")


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
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            conn.rollback()
            # Re-clear in case rollback undid previous deletes
            cur.execute("DELETE FROM gform.responses")
            cur.execute("DELETE FROM gform.questions")
            cur.execute("DELETE FROM gform.forms")
            cur.execute("DELETE FROM email.attachments")
            cur.execute("DELETE FROM email.sent_log")
            cur.execute("DELETE FROM email.messages")
        conn.commit()
        print("[preprocess] Cleared gform, email schemas.")

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name='INBOX' LIMIT 1")
        inbox_id = cur.fetchone()[0]

        noise_emails = [
            ("Office Holiday Schedule", "admin@company.com",
             json.dumps(["all@company.com"]),
             "Please review the updated holiday schedule for Q2 2026."),
            ("IT System Maintenance Window", "it@company.com",
             json.dumps(["all@company.com"]),
             "Scheduled maintenance on Saturday from 2am to 6am."),
            ("Quarterly Revenue Report", "finance@company.com",
             json.dumps(["leadership@company.com"]),
             "Q4 revenue exceeded targets by 12%. Full report attached."),
            ("New Employee Onboarding", "hr@company.com",
             json.dumps(["managers@company.com"]),
             "Welcome 15 new hires joining next Monday. Please prepare workstations."),
            ("Parking Lot Resurfacing", "facilities@company.com",
             json.dumps(["all@company.com"]),
             "Lot B will be closed for resurfacing March 15-17."),
        ]
        for subj, from_addr, to_addr, body in noise_emails:
            cur.execute(
                "INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, "
                "body_text, is_read, date) VALUES (%s, %s, %s, %s, %s, %s, false, now())",
                (inbox_id, f"noise-{uuid.uuid4()}@company.com", subj, from_addr, to_addr, body)
            )
        conn.commit()
        print("[preprocess] Injected 5 noise emails.")

        # Inject Training Feedback Survey form with 5 questions and 15 responses
        form_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO gform.forms (id, title, document_title, description) "
            "VALUES (%s, %s, %s, %s)",
            (form_id, "Training Feedback Survey", "Training Feedback Survey",
             "Survey to gather feedback on internal training programs")
        )

        q1_id = str(uuid.uuid4())
        q2_id = str(uuid.uuid4())
        q3_id = str(uuid.uuid4())
        q4_id = str(uuid.uuid4())
        q5_id = str(uuid.uuid4())

        questions = [
            (q1_id, "Overall Training Satisfaction", "RADIO",
             json.dumps({"choices": ["1", "2", "3", "4", "5"]}), 1),
            (q2_id, "Which module was most useful?", "TEXT", None, 2),
            (q3_id, "What improvements would you suggest?", "TEXT", None, 3),
            (q4_id, "Would you recommend this training to colleagues?", "RADIO",
             json.dumps({"choices": ["Yes", "No"]}), 4),
            (q5_id, "Preferred training format", "RADIO",
             json.dumps({"choices": ["Online", "In-Person", "Hybrid"]}), 5),
        ]

        for qid, title, qtype, config, pos in questions:
            cur.execute(
                "INSERT INTO gform.questions (id, form_id, title, question_type, required, config, position) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (qid, form_id, title, qtype, True, config, pos)
            )
        conn.commit()
        print("[preprocess] Injected survey form with 5 questions.")

        # Inject 15 sample responses
        satisfaction_scores = [4, 5, 3, 4, 3, 5, 4, 2, 4, 5, 3, 4, 3, 5, 4]
        modules = [
            "Data visualization techniques", "Statistical analysis module",
            "Dashboard design", "A/B testing methodology", "Data cleaning and prep",
            "Predictive modeling", "Data visualization techniques", "Survey design",
            "Statistical analysis module", "Dashboard design",
            "Machine learning basics", "Data cleaning and prep",
            "A/B testing methodology", "Predictive modeling", "Data visualization techniques"
        ]
        suggestions = [
            "More hands-on exercises", "Add real-world case studies",
            "Shorter sessions with breaks", "More interactive content",
            "Better pre-course materials", "Include certification option",
            "More group projects", "Reduce lecture time",
            "Add advanced topics", "Better pacing of content",
            "More practice datasets", "Include peer review sessions",
            "Add mentorship component", "More industry examples",
            "Flexible scheduling options"
        ]
        recommends = ["Yes", "Yes", "No", "Yes", "Yes", "No", "Yes", "No", "Yes", "Yes",
                      "No", "Yes", "Yes", "Yes", "Yes"]
        formats = ["Hybrid", "Online", "Hybrid", "In-Person", "Hybrid",
                   "Online", "Hybrid", "In-Person", "Hybrid", "Online",
                   "Hybrid", "Hybrid", "Online", "Hybrid", "In-Person"]

        for i in range(15):
            resp_id = str(uuid.uuid4())
            answers = json.dumps({
                q1_id: str(satisfaction_scores[i]),
                q2_id: modules[i],
                q3_id: suggestions[i],
                q4_id: recommends[i],
                q5_id: formats[i],
            })
            cur.execute(
                "INSERT INTO gform.responses (id, form_id, respondent_email, answers) "
                "VALUES (%s, %s, %s, %s)",
                (resp_id, form_id, f"employee{i+1}@company.com", answers)
            )
        conn.commit()
        print("[preprocess] Injected 15 survey responses.")

        # Also inject a noise form
        noise_form_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO gform.forms (id, title, document_title) VALUES (%s, %s, %s)",
            (noise_form_id, "Office Snack Preferences", "Snack Survey")
        )
        nq1 = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO gform.questions (id, form_id, title, question_type, position) "
            "VALUES (%s, %s, %s, %s, %s)",
            (nq1, noise_form_id, "Favorite snack type?", "TEXT", 1)
        )
        for i in range(3):
            cur.execute(
                "INSERT INTO gform.responses (id, form_id, respondent_email, answers) "
                "VALUES (%s, %s, %s, %s)",
                (str(uuid.uuid4()), noise_form_id, f"snacker{i+1}@company.com",
                 json.dumps({nq1: ["Chips", "Fruit", "Cookies"][i]}))
            )
        conn.commit()
        print("[preprocess] Injected noise form.")

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
