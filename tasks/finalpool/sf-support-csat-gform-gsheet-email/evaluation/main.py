"""Evaluation for sf-support-csat-gform-gsheet-email.

Checks:
1. Google Sheet "Support Center Performance Dashboard" with SLA_Compliance and Summary sheets
2. Google Forms "Customer Support Satisfaction Survey" with 4 questions
3. Email to support-management@company.example.com
"""
import argparse
import os
import sys

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")

PASS_COUNT = 0
FAIL_COUNT = 0

# Actual SLA data from DB
SLA_DATA = {
    "high":   {"total": 6466,  "compliant": 778,  "rate": 12.03, "csat": 3.26},
    "medium": {"total": 15774, "compliant": 1645, "rate": 10.43, "csat": 3.26},
    "low":    {"total": 9348,  "compliant": 4204, "rate": 44.97, "csat": 3.25},
}


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name}: {str(detail)[:200]}")


def num_close(a, b, tol=1.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def check_gsheet():
    print("\n=== Checking Google Sheet ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title FROM gsheet.spreadsheets
        WHERE title ILIKE '%support%' AND title ILIKE '%performance%'
    """)
    sheets = cur.fetchall()
    check("Support Center Performance Dashboard spreadsheet exists", len(sheets) >= 1,
          f"Found: {[s[1] for s in sheets]}")

    if not sheets:
        cur.close()
        conn.close()
        return False

    ss_id = sheets[0][0]

    # Check sheets exist
    cur.execute("SELECT title FROM gsheet.sheets WHERE spreadsheet_id = %s", (ss_id,))
    sheet_tabs = [r[0] for r in cur.fetchall()]

    has_sla = any("sla" in t.lower() for t in sheet_tabs)
    has_summary = any("summary" in t.lower() for t in sheet_tabs)
    check("Has SLA_Compliance sheet", has_sla, f"Tabs: {sheet_tabs}")
    check("Has Summary sheet", has_summary, f"Tabs: {sheet_tabs}")

    # Check cells contain priority data
    cur.execute("""
        SELECT c.value FROM gsheet.cells c
        WHERE c.spreadsheet_id = %s
    """, (ss_id,))
    cells = [str(r[0]) for r in cur.fetchall() if r[0] is not None]
    all_vals = " ".join(cells).lower()

    check("Sheet contains 'High' priority data", "high" in all_vals, "Not found")
    check("Sheet contains 'Medium' priority data", "medium" in all_vals, "Not found")
    check("Sheet contains 'Low' priority data", "low" in all_vals, "Not found")

    # Check numeric compliance data appears
    check("Sheet contains ticket counts", any(str(v) in all_vals for v in ["6466", "15774", "9348"]),
          "Ticket counts not found")

    cur.close()
    conn.close()
    return has_sla and has_summary


def check_gform():
    print("\n=== Checking Google Forms ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title FROM gform.forms
        WHERE title ILIKE '%customer%support%' OR title ILIKE '%support%satisfaction%'
    """)
    forms = cur.fetchall()
    check("Customer Support Satisfaction Survey form exists", len(forms) >= 1,
          f"Found: {[f[1] for f in forms]}")

    if forms:
        form_id = forms[0][0]
        cur.execute("SELECT COUNT(*) FROM gform.questions WHERE form_id = %s", (form_id,))
        q_count = cur.fetchone()[0]
        check("Form has 4 questions", q_count == 4, f"Got {q_count}")

    cur.close()
    conn.close()


def check_email():
    print("\n=== Checking Email ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
        WHERE subject ILIKE '%support%' AND subject ILIKE '%performance%'
        ORDER BY date DESC
    """)
    emails = cur.fetchall()
    check("Support performance email exists", len(emails) >= 1, f"Found {len(emails)}")

    if emails:
        e = emails[0]
        to_str = str(e[2])
        check("Email to support-management@company.example.com",
              "support-management@company.example.com" in to_str.lower(), f"to: {to_str}")
        check("Email from analytics@company.example.com",
              "analytics@company.example.com" in (e[1] or "").lower(), f"from: {e[1]}")
        body = (e[3] or "").lower()
        check("Email body mentions SLA or compliance",
              any(kw in body for kw in ["sla", "compliance", "csat", "satisfaction", "high", "medium", "low"]),
              "Body missing key terms")

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    gsheet_ok = check_gsheet()
    check_gform()
    check_email()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    overall = FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
