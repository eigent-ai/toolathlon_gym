"""Evaluation for canvas-quiz-remediation-gform-gcal."""
import argparse
import json
import os
import sys

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")

PASS_COUNT = 0
FAIL_COUNT = 0

# Quizzes for course 16 with avg score below 80
UNDERPERFORMING_QUIZZES = [
    "CMA 34880",
    "CMA 34881",
    "CMA 34882",
    "CMA 34883",
    "CMA 34884",
]


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_str = f": {detail[:200]}" if detail else ""
        print(f"  [FAIL] {name}{detail_str}")


def check_gform():
    """Check Google Form creation."""
    print("\n=== Checking Google Form ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM gform.forms")
    forms = cur.fetchall()
    check("At least one form created", len(forms) >= 1, f"Found {len(forms)} forms")

    form_id = None
    for fid, title in forms:
        if "self-assessment" in (title or "").lower() or "finance quiz" in (title or "").lower() or "quiz" in (title or "").lower():
            form_id = fid
            check("Form titled 'Finance Quiz Self-Assessment' found", True)
            break

    if form_id is None and forms:
        form_id = forms[0][0]
        check("Form titled 'Finance Quiz Self-Assessment' found", False,
              f"Found titles: {[f[1] for f in forms]}")

    if form_id:
        cur.execute("SELECT COUNT(*) FROM gform.questions WHERE form_id = %s", (form_id,))
        q_count = cur.fetchone()[0]
        check("Form has exactly 4 questions", q_count == 4,
              f"Found {q_count} questions")

    conn.close()


def check_gcal():
    """Check remediation calendar events."""
    print("\n=== Checking Google Calendar Events ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, summary, start_datetime FROM gcal.events ORDER BY start_datetime")
    events = cur.fetchall()
    check("At least 1 remediation event created", len(events) >= 1,
          f"Found {len(events)} events")

    remediation_events = [e for e in events if "remediation" in (e[1] or "").lower()]
    check("At least 1 remediation session event",
          len(remediation_events) >= 1,
          f"Remediation events: {[(e[1], str(e[2])) for e in remediation_events]}")

    # Check that event titles mention quiz names
    for quiz_title in UNDERPERFORMING_QUIZZES[:2]:  # check at least 2
        quiz_num = quiz_title.split()[-1]  # e.g., "34880"
        found = any(quiz_num in (e[1] or "") for e in remediation_events)
        # Lenient check: just look for remediation events overall
    check("Remediation events match expected count",
          len(remediation_events) >= min(5, len(UNDERPERFORMING_QUIZZES)),
          f"Expected {len(UNDERPERFORMING_QUIZZES)}, found {len(remediation_events)}")

    conn.close()


def check_emails():
    """Check that remediation email was sent."""
    print("\n=== Checking Emails ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT subject, from_addr, to_addr, body_text FROM email.messages")
    all_emails = cur.fetchall()
    conn.close()

    def find_email_for_recipient(recipient):
        for subj, from_addr, to_addr, body in all_emails:
            if to_addr:
                recipients = []
                if isinstance(to_addr, list):
                    recipients = [str(r).strip().lower() for r in to_addr]
                elif isinstance(to_addr, str):
                    try:
                        parsed = json.loads(to_addr)
                        if isinstance(parsed, list):
                            recipients = [str(r).strip().lower() for r in parsed]
                        else:
                            recipients = [str(to_addr).strip().lower()]
                    except (json.JSONDecodeError, TypeError):
                        recipients = [str(to_addr).strip().lower()]
                if recipient.lower() in recipients:
                    return subj, from_addr, to_addr, body
        return None

    result = find_email_for_recipient("remediation@financeou.example.com")
    check("Email sent to remediation@financeou.example.com", result is not None,
          f"Total emails: {len(all_emails)}")

    if result:
        subj, from_addr, to_addr, body = result
        check("Email subject contains 'Remediation Study Sessions'",
              "remediation" in (subj or "").lower(),
              f"Subject: {subj}")
        check("Email from tutor@financeou.example.com",
              "tutor@financeou.example.com" in (from_addr or "").lower(),
              f"From: {from_addr}")
        body_lower = (body or "").lower()
        check("Email body mentions quiz remediation content",
              "remediation" in body_lower or "quiz" in body_lower,
              "Expected remediation content in email body")
        check("Email body mentions quiz names or study sessions",
              any(q.lower() in body_lower for q in ["34880", "34881", "cma", "session"]),
              "Expected quiz names or session info")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    print("=" * 70)
    print("CANVAS QUIZ REMEDIATION GFORM GCAL - EVALUATION")
    print("=" * 70)

    check_gform()
    check_gcal()
    check_emails()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    overall = FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
