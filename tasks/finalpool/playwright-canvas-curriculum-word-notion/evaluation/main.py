"""
Evaluation script for playwright-canvas-curriculum-word-notion task.

Checks:
1. Word document Accreditation_Compliance_Report.docx with course evaluations
2. Notion database "Course Compliance Tracker" with 22 entries
3. Emails to departments with non-compliant courses
"""

import argparse
import json
import os
import sys

import psycopg2

try:
    from docx import Document
except ImportError:
    Document = None

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

PASS_COUNT = 0
FAIL_COUNT = 0

# Non-compliant departments based on standards (min 8 assignments, min 3 quizzes)
NON_COMPLIANT_DEPTS = [
    "Applied Analytics",
    "Biochemistry",
    "Data-Driven",
    "Environmental",
]


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def str_contains(haystack, needle):
    if haystack is None or needle is None:
        return False
    return needle.strip().lower() in str(haystack).strip().lower()


def check_word(agent_workspace):
    """Check Word compliance report."""
    print("\n=== Checking Word Document ===")

    doc_path = os.path.join(agent_workspace, "Accreditation_Compliance_Report.docx")
    if not os.path.isfile(doc_path):
        record("Accreditation_Compliance_Report.docx exists", False)
        return False

    record("Accreditation_Compliance_Report.docx exists", True)

    if Document is None:
        record("python-docx available", False, "Cannot import docx")
        return True

    try:
        doc = Document(doc_path)
        full_text = "\n".join(p.text for p in doc.paragraphs).lower()

        record(
            "Doc mentions accreditation/compliance",
            "accreditation" in full_text or "compliance" in full_text,
        )

        # Check course names mentioned (spot check)
        record(
            "Doc mentions Applied Analytics",
            "applied analytics" in full_text,
        )
        record(
            "Doc mentions Foundations of Finance",
            "foundations of finance" in full_text,
        )

        # Check compliance status mentioned
        has_status = (
            ("compliant" in full_text and "non-compliant" in full_text)
            or ("pass" in full_text and "fail" in full_text)
        )
        record("Doc has compliance status indicators", has_status)

        # Check summary statistics
        has_summary = any(
            kw in full_text for kw in ["summary", "total", "rate", "overall"]
        )
        record("Doc has summary section", has_summary)

        # Check mentions enough courses (at least 10 course names)
        course_keywords = [
            "applied analytics", "biochemistry", "creative computing",
            "data-driven", "environmental", "foundations of finance",
            "global governance",
        ]
        mentioned = sum(1 for kw in course_keywords if kw in full_text)
        record(
            "Doc covers most departments",
            mentioned >= 5,
            f"Found {mentioned}/7 department names",
        )

        return True
    except Exception as e:
        record("Word doc readable", False, str(e))
        return False


def check_notion():
    """Check Notion database for Course Compliance Tracker."""
    print("\n=== Checking Notion Database ===")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT id, title, properties FROM notion.databases")
        dbs = cur.fetchall()

        found_db = None
        for db_id, title_raw, props in dbs:
            if isinstance(title_raw, list):
                title = " ".join(t.get("plain_text", "") for t in title_raw if isinstance(t, dict))
            elif isinstance(title_raw, str):
                try:
                    parsed = json.loads(title_raw)
                    if isinstance(parsed, list):
                        title = " ".join(t.get("plain_text", "") for t in parsed if isinstance(t, dict))
                    else:
                        title = title_raw
                except (json.JSONDecodeError, TypeError):
                    title = title_raw
            else:
                title = str(title_raw) if title_raw else ""

            title_lower = title.lower()
            if ("compliance" in title_lower or "course" in title_lower) and (
                "tracker" in title_lower or "compliance" in title_lower
            ):
                found_db = db_id
                break

        if not found_db:
            record(
                "Course Compliance Tracker database exists",
                False,
                f"Found {len(dbs)} databases",
            )
            cur.close()
            conn.close()
            return False

        record("Course Compliance Tracker database exists", True)

        # Check entries
        cur.execute(
            "SELECT id, properties FROM notion.pages WHERE parent::text LIKE %s",
            (f'%{found_db}%',),
        )
        pages = cur.fetchall()

        record(
            "Database has 22 entries",
            len(pages) >= 22,
            f"Found {len(pages)} entries",
        )

        # Check for mix of compliant/non-compliant
        compliant_count = 0
        non_compliant_count = 0
        for page_id, page_props in pages:
            if isinstance(page_props, str):
                page_props = json.loads(page_props)
            if isinstance(page_props, dict):
                for key, val in page_props.items():
                    if "status" in key.lower() or "overall" in key.lower():
                        if isinstance(val, dict):
                            select_val = val.get("select", {})
                            if isinstance(select_val, dict):
                                status = (select_val.get("name", "") or "").lower()
                                if "non" in status:
                                    non_compliant_count += 1
                                elif "compliant" in status:
                                    compliant_count += 1

        record(
            "Mix of compliant and non-compliant entries",
            compliant_count > 0 and non_compliant_count > 0,
            f"Compliant: {compliant_count}, Non-Compliant: {non_compliant_count}",
        )

        # Check non-compliant count approximately right (~9)
        record(
            "Approximately 9 non-compliant courses",
            6 <= non_compliant_count <= 12,
            f"Found {non_compliant_count} non-compliant",
        )

        cur.close()
        conn.close()
        return True

    except Exception as e:
        record("Notion DB accessible", False, str(e))
        return False


def check_emails():
    """Check department notification emails."""
    print("\n=== Checking Emails ===")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "SELECT subject, from_addr, to_addr, body_text FROM email.messages"
        )
        emails = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        record("Email DB accessible", False, str(e))
        return False

    # Find accreditation review emails
    review_emails = []
    for subject, from_addr, to_addr, body_text in emails:
        subj_lower = (subject or "").lower()
        if "accreditation" in subj_lower or "compliance" in subj_lower or "review" in subj_lower:
            review_emails.append((subject, from_addr, to_addr, body_text))

    record(
        "Accreditation review emails sent",
        len(review_emails) >= 3,
        f"Found {len(review_emails)} review emails (expected >= 3 for non-compliant depts)",
    )

    # Check that at least some non-compliant departments are mentioned
    all_body = " ".join((e[3] or "").lower() for e in review_emails)
    all_subjects = " ".join((e[0] or "").lower() for e in review_emails)
    combined = all_body + " " + all_subjects

    depts_mentioned = 0
    for dept_kw in NON_COMPLIANT_DEPTS:
        if dept_kw.lower() in combined:
            depts_mentioned += 1

    record(
        "Non-compliant departments mentioned",
        depts_mentioned >= 3,
        f"Found {depts_mentioned}/4 expected departments",
    )

    # Check body mentions non-compliance details
    has_details = any(
        kw in combined for kw in ["assignment", "quiz", "fail", "non-compliant", "below", "minimum"]
    )
    record("Email body mentions compliance failures", has_details)

    return len(review_emails) >= 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    word_ok = check_word(args.agent_workspace)
    notion_ok = check_notion()
    email_ok = check_emails()

    print(f"\n=== SUMMARY ===")
    print(f"  Word:   {'PASS' if word_ok else 'FAIL'}")
    print(f"  Notion: {'PASS' if notion_ok else 'FAIL'}")
    print(f"  Email:  {'PASS' if email_ok else 'FAIL'}")
    print(f"  Passed: {PASS_COUNT}, Failed: {FAIL_COUNT}")

    overall = word_ok and notion_ok and email_ok
    print(f"  Overall:  {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
