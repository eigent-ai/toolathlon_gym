"""
Preprocess script for canvas-enrollment-forecast-excel-gform-email task.
Clears gform and email data, injects noise records. Canvas is read-only.
"""
import os
import argparse
import json
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Clear gform data
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        print("[preprocess] Cleared gform data.")

        # Clear email data
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        print("[preprocess] Cleared email data.")

        # Inject noise form
        noise_form_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gform.forms (id, title, description)
            VALUES (%s, %s, %s)
        """, (noise_form_id, "Campus Facilities Feedback",
              "Share your thoughts on campus facilities"))
        cur.execute("""
            INSERT INTO gform.questions (id, form_id, title, question_type, position)
            VALUES (%s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), noise_form_id, "Rate the library", "RADIO", 0))
        cur.execute("""
            INSERT INTO gform.questions (id, form_id, title, question_type, position)
            VALUES (%s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), noise_form_id, "Additional comments", "TEXT", 1))
        print("[preprocess] Injected noise form.")

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name = 'Inbox' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('Inbox') RETURNING id")
            row = cur.fetchone()
        inbox_id = row[0]

        cur.execute("SELECT id FROM email.folders WHERE name = 'Sent' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('Sent') RETURNING id")
            row = cur.fetchone()
        sent_id = row[0]

        for i, (subj, from_addr, to_addr) in enumerate([
            ("Faculty Meeting Reminder", "admin@university.edu",
             json.dumps(["all_faculty@university.edu"])),
            ("Budget Update Q3", "finance@university.edu",
             json.dumps(["department_heads@university.edu"])),
            ("Parking Permit Renewal", "facilities@university.edu",
             json.dumps(["staff@university.edu"])),
        ]):
            cur.execute("""
                INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, body_text)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
            """, (inbox_id, str(uuid.uuid4()), subj, from_addr, to_addr,
                  f"This is noise email {i+1} for testing purposes."))
        print("[preprocess] Injected noise emails.")

        conn.commit()
        print("[preprocess] Done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
