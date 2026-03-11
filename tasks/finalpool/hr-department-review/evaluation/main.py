"""
Evaluation script for hr-department-review task.

Checks:
1. Word document Department_Review_2025.docx exists and contains all 7 departments
   with correct headcount, avg salary, avg performance rating.
2. 7 emails sent to correct department managers with correct content.
"""

import argparse
import json
import os
import re
import sys

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PASS_COUNT = 0
FAIL_COUNT = 0


def load_expected_depts():
    """Query PostgreSQL to compute expected department data from Snowflake HR_ANALYTICS tables."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                e."DEPARTMENT",
                COUNT(e."EMPLOYEE_ID") AS headcount,
                ROUND(AVG(e."SALARY")::numeric, 2) AS avg_salary,
                ROUND(AVG(e."PERFORMANCE_RATING")::numeric, 2) AS avg_perf,
                LOWER(REPLACE(mgr."EMPLOYEE_NAME", ' ', '')) || '@company.com' AS manager_email
            FROM sf_data."HR_ANALYTICS__PUBLIC__EMPLOYEES" e
            JOIN sf_data."HR_ANALYTICS__PUBLIC__DEPARTMENTS" d
                ON e."DEPARTMENT" = d."DEPARTMENT_NAME"
            JOIN sf_data."HR_ANALYTICS__PUBLIC__EMPLOYEES" mgr
                ON d."MANAGER_ID" = mgr."EMPLOYEE_ID"
            GROUP BY e."DEPARTMENT", mgr."EMPLOYEE_NAME"
            ORDER BY e."DEPARTMENT"
        """)
        rows = cur.fetchall()
        cur.close()

        depts = {}
        for dept, headcount, avg_salary, avg_perf, manager_email in rows:
            depts[dept] = {
                "headcount": int(headcount),
                "avg_salary": float(avg_salary),
                "avg_perf": float(avg_perf),
                "manager_email": manager_email,
            }
        return depts
    finally:
        conn.close()


# Expected department data computed from Snowflake HR_ANALYTICS at evaluation time
EXPECTED_DEPTS = load_expected_depts()


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_str = f": {str(detail)[:200]}" if detail else ""
        print(f"  [FAIL] {name}{detail_str}")


def normalize_text(text):
    """Normalize text for comparison: lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def number_appears(value, text):
    """Check if a number appears in text, with or without comma formatting."""
    val_str = str(value)
    # Try exact match
    if val_str in text:
        return True
    # Try with commas (e.g., 7,096)
    try:
        int_val = int(value)
        formatted = f"{int_val:,}"
        if formatted in text:
            return True
    except (ValueError, TypeError):
        pass
    # Try float with 2 decimals
    try:
        float_val = float(value)
        formatted_2d = f"{float_val:.2f}"
        if formatted_2d in text:
            return True
        # Also try with comma thousands
        int_part = int(float_val)
        dec_part = formatted_2d.split(".")[1]
        formatted_comma = f"{int_part:,}.{dec_part}"
        if formatted_comma in text:
            return True
    except (ValueError, TypeError):
        pass
    return False


def check_word_doc(agent_workspace):
    """Check Department_Review_2025.docx."""
    print("\n=== Checking Word Document ===")
    from docx import Document

    doc_path = os.path.join(agent_workspace, "Department_Review_2025.docx")
    check("Word file exists", os.path.isfile(doc_path), f"Expected {doc_path}")
    if not os.path.isfile(doc_path):
        return False

    try:
        doc = Document(doc_path)
    except Exception as e:
        check("Word file readable", False, str(e))
        return False

    # Collect all text
    all_paragraphs = []
    for para in doc.paragraphs:
        all_paragraphs.append(para.text.strip())
    all_text = " ".join(all_paragraphs)
    all_text_lower = all_text.lower()

    # Check all 7 department names appear
    for dept in EXPECTED_DEPTS:
        dept_lower = dept.lower()
        # For R&D, also accept "r&d", "r & d", "r and d"
        if dept == "R&D":
            found = any(
                variant in all_text_lower
                for variant in ["r&d", "r & d", "r and d", "r&amp;d"]
            )
        else:
            found = dept_lower in all_text_lower
        check(f"Department '{dept}' mentioned in document", found)

    # Check headcount values appear
    for dept, data in EXPECTED_DEPTS.items():
        hc = data["headcount"]
        found = number_appears(hc, all_text)
        check(f"Headcount {hc} for '{dept}' in document", found,
              f"Value {hc} not found")

    # Check avg salary values appear (within some format)
    for dept, data in EXPECTED_DEPTS.items():
        avg_sal = data["avg_salary"]
        found = number_appears(avg_sal, all_text)
        check(f"Avg salary {avg_sal} for '{dept}' in document", found,
              f"Value {avg_sal} not found")

    # Check avg performance rating values appear
    for dept, data in EXPECTED_DEPTS.items():
        avg_perf = data["avg_perf"]
        perf_str = f"{avg_perf:.2f}"
        found = perf_str in all_text
        check(f"Avg perf rating {perf_str} for '{dept}' in document", found,
              f"Value {perf_str} not found")

    return True


def check_emails():
    """Check that 7 emails were sent to the correct managers."""
    print("\n=== Checking Emails ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
        WHERE folder_id = 2 OR folder_id IS NULL
    """)
    all_emails = cur.fetchall()

    # If no emails in folder 2, try all emails
    if len(all_emails) == 0:
        cur.execute("""
            SELECT subject, from_addr, to_addr, body_text
            FROM email.messages
        """)
        all_emails = cur.fetchall()

    check("At least 7 emails exist", len(all_emails) >= 7,
          f"Found {len(all_emails)} emails")

    def parse_recipients(to_addr):
        """Parse to_addr field into a list of lowercase email strings."""
        if to_addr is None:
            return []
        if isinstance(to_addr, list):
            return [str(r).strip().lower() for r in to_addr]
        to_str = str(to_addr).strip()
        try:
            parsed = json.loads(to_str)
            if isinstance(parsed, list):
                return [str(r).strip().lower() for r in parsed]
            return [to_str.lower()]
        except (json.JSONDecodeError, TypeError):
            return [to_str.lower()]

    def find_email_for(target_email):
        for subj, from_addr, to_addr, body in all_emails:
            recipients = parse_recipients(to_addr)
            if target_email.lower() in recipients:
                return subj, from_addr, to_addr, body
        return None

    matched_emails = set()
    for dept, data in EXPECTED_DEPTS.items():
        manager_email = data["manager_email"]
        result = find_email_for(manager_email)
        check(f"Email sent to {manager_email} ({dept})", result is not None)

        if result:
            subj, from_addr, to_addr, body = result
            matched_emails.add(manager_email)
            subj_lower = (subj or "").lower()
            body_lower = (body or "").lower()

            # Check subject contains department name
            dept_lower = dept.lower()
            if dept == "R&D":
                dept_in_subject = any(
                    v in subj_lower for v in ["r&d", "r & d", "r and d", "r&amp;d", "rd"]
                )
            else:
                dept_in_subject = dept_lower in subj_lower
            check(f"Email to {dept}: subject contains department name",
                  dept_in_subject,
                  f"Subject: {(subj or '')[:100]}")

            # Check body mentions department name
            if dept == "R&D":
                dept_in_body = any(
                    v in body_lower for v in ["r&d", "r & d", "r and d", "r&amp;d"]
                )
            else:
                dept_in_body = dept_lower in body_lower
            check(f"Email to {dept}: body mentions department name",
                  dept_in_body,
                  f"Body start: {(body or '')[:100]}")

            # Check body mentions headcount or avg salary
            hc = data["headcount"]
            avg_sal = data["avg_salary"]
            body_text = body or ""
            has_hc = number_appears(hc, body_text)
            has_sal = number_appears(avg_sal, body_text)
            check(f"Email to {dept}: body mentions headcount or avg salary",
                  has_hc or has_sal,
                  f"Neither {hc} nor {avg_sal} found in body")

    # Reverse check: no unexpected emails beyond the 7
    all_recipient_emails = set()
    for subj, from_addr, to_addr, body in all_emails:
        for r in parse_recipients(to_addr):
            all_recipient_emails.add(r)
    expected_emails = {d["manager_email"].lower() for d in EXPECTED_DEPTS.values()}
    unexpected = all_recipient_emails - expected_emails
    # Allow some tolerance - just warn, don't fail for a couple extra
    check("No more than 2 unexpected email recipients",
          len(unexpected) <= 2,
          f"Unexpected recipients: {unexpected}")

    cur.close()
    conn.close()
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    word_ok = check_word_doc(args.agent_workspace)
    email_ok = check_emails()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    all_passed = FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if all_passed else 'FAIL'}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
