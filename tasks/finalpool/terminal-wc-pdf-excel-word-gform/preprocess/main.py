"""Preprocess for terminal-wc-pdf-excel-word-gform.
Clears gform. Injects noise form. WC is read-only."""
import argparse
import glob as globmod
import json
import os
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear gform data
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        conn.commit()
        print("[preprocess] Cleared gform data.")

        # Inject noise form
        noise_form_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gform.forms (id, title, document_title, description)
            VALUES (%s, %s, %s, %s)
        """, (noise_form_id, "Employee Satisfaction Survey", "Employee Satisfaction Survey",
              "Annual employee satisfaction survey"))

        noise_questions = [
            ("How satisfied are you with your role?", "SCALE", 1),
            ("Any comments about the workplace?", "PARAGRAPH_TEXT", 2),
        ]
        for title, qtype, pos in noise_questions:
            cur.execute("""
                INSERT INTO gform.questions (id, form_id, item_id, title, question_type, required, position)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), noise_form_id, str(uuid.uuid4()), title, qtype, True, pos))

        conn.commit()
        print("[preprocess] Injected noise gform.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up agent workspace
    if args.agent_workspace:
        for pattern in ["Product_Quality_Audit.xlsx", "Quality_Audit_Report.docx", "quality_audit.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
