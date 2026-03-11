"""Evaluation for sf-support-metrics-pdf-email."""
import argparse
import os
import sys

import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}


def extract_pdf_text(path):
    """Extract text from PDF using available libraries."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except ImportError:
        pass
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except ImportError:
        pass
    with open(path, "rb") as f:
        return f.read().decode("latin-1", errors="ignore")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    task_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    gt_dir = args.groundtruth_workspace or os.path.join(task_root, "groundtruth_workspace")

    all_errors = []

    # --- Check PDF ---
    agent_pdf = os.path.join(args.agent_workspace, "Support_Metrics.pdf")
    if not os.path.exists(agent_pdf):
        print(f"FAIL: Agent output not found: {agent_pdf}")
        sys.exit(1)

    print("  Checking Support_Metrics.pdf...")
    text = extract_pdf_text(agent_pdf).lower()

    # Check title
    if "support metrics report" not in text:
        all_errors.append("PDF missing title 'Support Metrics Report'")

    # Check sections
    if "overview" not in text:
        all_errors.append("PDF missing 'Overview' section")
    if "issue type" not in text:
        all_errors.append("PDF missing 'Issue Type' section")
    if "priority" not in text:
        all_errors.append("PDF missing 'Priority' section")

    # Validate data against DB
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT "ISSUE_TYPE", COUNT(*) as cnt,
          ROUND(AVG("RESPONSE_TIME_HOURS")::numeric, 2) as avg_resp,
          ROUND(AVG("CUSTOMER_SATISFACTION"), 2) as avg_csat
        FROM sf_data."SUPPORT_CENTER__PUBLIC__TICKETS"
        GROUP BY "ISSUE_TYPE"
        ORDER BY cnt DESC
    """)
    issue_types = cur.fetchall()

    cur.execute("""
        SELECT "PRIORITY", COUNT(*) as cnt,
          ROUND(AVG("RESPONSE_TIME_HOURS")::numeric, 2) as avg_resp,
          ROUND(AVG("CUSTOMER_SATISFACTION"), 2) as avg_csat
        FROM sf_data."SUPPORT_CENTER__PUBLIC__TICKETS"
        GROUP BY "PRIORITY"
        ORDER BY "PRIORITY"
    """)
    priorities = cur.fetchall()
    conn.close()

    total_tickets = sum(r[1] for r in issue_types)

    # Check issue types present
    expected_issues = ["performance issue", "bug", "feature request", "incident",
                       "service request", "maintenance", "technical issue"]
    for issue in expected_issues:
        if issue not in text:
            all_errors.append(f"PDF missing issue type: {issue}")

    # Check priorities present
    for p in ["high", "medium", "low"]:
        if p not in text:
            all_errors.append(f"PDF missing priority: {p}")

    # Check total ticket count appears
    if str(total_tickets) not in text:
        all_errors.append(f"PDF missing total ticket count: {total_tickets}")

    # Check issue type ticket counts
    for r in issue_types:
        if str(r[1]) not in text:
            all_errors.append(f"PDF missing ticket count {r[1]} for {r[0]}")

    # Check priority ticket counts
    for r in priorities:
        if str(r[1]) not in text:
            all_errors.append(f"PDF missing ticket count {r[1]} for priority {r[0]}")

    if not all_errors:
        print("    PASS")

    # --- Non-blocking: Check email in DB ---
    print("  Checking email (non-blocking)...")
    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, subject, to_addr, body_text
            FROM email.messages
            WHERE LOWER(subject) LIKE '%support%metrics%'
            OR LOWER(to_addr::text) LIKE '%manager@supportcenter%'
        """)
        emails = cur.fetchall()
        if emails:
            print(f"    Found {len(emails)} matching email(s)")
        else:
            # Also check sent_log
            cur.execute("SELECT COUNT(*) FROM email.sent_log")
            sent = cur.fetchone()[0]
            if sent > 0:
                print(f"    Found {sent} sent email(s)")
            else:
                print("    WARNING: No matching email found (non-blocking)")
        conn.close()
    except Exception as e:
        print(f"    WARNING: Email DB check error: {e} (non-blocking)")

    if all_errors:
        print(f"\n=== RESULT: FAIL ({len(all_errors)} errors) ===")
        for e in all_errors[:15]:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("\n=== RESULT: PASS ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
