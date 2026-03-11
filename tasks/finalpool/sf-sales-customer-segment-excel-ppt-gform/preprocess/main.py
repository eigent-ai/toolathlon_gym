"""
Preprocess script for sf-sales-customer-segment-excel-ppt-gform.
Snowflake Sales DW is read-only. Clear gform data and inject noise.
"""
import argparse
import glob
import os
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
        print("[preprocess] Clearing Google Forms data...")
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")

        print("[preprocess] Clearing email data...")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages WHERE folder_id != 0")
        cur.execute("DELETE FROM email.drafts")

        # Inject 1 noise form
        noise_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gform.forms (id, title, description)
            VALUES (%s, 'Employee Onboarding Checklist', 'HR onboarding form for new hires')
        """, (noise_id,))
        cur.execute("""
            INSERT INTO gform.questions (form_id, title, question_type, required, position)
            VALUES (%s, 'Full Name', 'TEXT', true, 0)
        """, (noise_id,))
        cur.execute("""
            INSERT INTO gform.questions (form_id, title, question_type, required, position)
            VALUES (%s, 'Department', 'MULTIPLE_CHOICE', true, 1)
        """, (noise_id,))

        conn.commit()
        print("[preprocess] DB cleanup and noise injection done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean agent workspace artifacts if present
    if args.agent_workspace:
        for pattern in ["Customer_Segment_Analysis.xlsx", "QBR_Presentation.pptx"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
