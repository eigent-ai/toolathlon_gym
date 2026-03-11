"""
Evaluation for yt-engagement-analysis-gsheet-word task.

Checks:
1. GSheet 'Fireship Engagement Analysis' exists with Engagement_Data sheet
2. Engagement_Data has correct columns and at least 100 rows (all 104 Fireship videos)
3. Monthly_Summary sheet exists with correct columns
4. Engagement_Rate_Pct values are computed correctly (spot check)
5. Word document Engagement_Analysis_Report.docx exists with required sections
6. Email sent to research@company.com with correct subject
"""
import json
import os
import sys
from argparse import ArgumentParser

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


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def check_gsheet():
    print("\n=== Check 1: Google Sheet 'Fireship Engagement Analysis' ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title FROM gsheet.spreadsheets
        WHERE title ILIKE '%%fireship engagement%%'
        ORDER BY id DESC LIMIT 1
    """)
    ss = cur.fetchone()
    record("Spreadsheet 'Fireship Engagement Analysis' exists", ss is not None,
           "No matching spreadsheet found")

    if not ss:
        cur.close()
        conn.close()
        return

    ss_id = ss[0]

    # Check Engagement_Data sheet
    cur.execute("""
        SELECT id, title FROM gsheet.sheets
        WHERE spreadsheet_id = %s AND title ILIKE '%%engagement_data%%'
    """, (ss_id,))
    eng_sheet = cur.fetchone()
    record("Engagement_Data sheet exists", eng_sheet is not None,
           f"Sheets in spreadsheet: {ss_id}")

    if eng_sheet:
        sheet_id = eng_sheet[0]
        cur.execute("SELECT COUNT(*) FROM gsheet.cells WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index > 1", (ss_id, sheet_id,))
        row_count = cur.fetchone()[0]
        # 104 videos, but columns vary - count unique rows
        cur.execute("SELECT COUNT(DISTINCT row_index) FROM gsheet.cells WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index > 1", (ss_id, sheet_id,))
        unique_rows = cur.fetchone()[0]
        record("Engagement_Data has at least 90 data rows (Fireship videos)",
               unique_rows >= 90, f"Found {unique_rows} unique data rows")

        # Check column headers
        cur.execute("""
            SELECT col_index, value FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index = 1
            ORDER BY col_index
        """, (ss_id, sheet_id,))
        headers = [r[1] for r in cur.fetchall()]
        headers_lower = [h.lower() if h else "" for h in headers]
        has_video_id = any("video_id" in h for h in headers_lower)
        has_engagement = any("engagement" in h for h in headers_lower)
        has_view = any("view" in h for h in headers_lower)
        record("Engagement_Data has required columns (Video_ID, Engagement_Rate_Pct, View_Count)",
               has_video_id and has_engagement and has_view,
               f"Headers: {headers}")

        # Spot check: verify top engagement video title appears
        cur.execute("""
            SELECT value FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s
            ORDER BY row_index, col_index
            LIMIT 500
        """, (ss_id, sheet_id,))
        all_vals = [r[0] or "" for r in cur.fetchall()]
        all_text = " ".join(all_vals).lower()
        has_top_video = "open-source" in all_text or "saas" in all_text or "stupid" in all_text
        record("Engagement_Data contains top engagement video content",
               has_top_video, "Top engagement video keywords not found")

    # Check Monthly_Summary sheet
    cur.execute("""
        SELECT id, title FROM gsheet.sheets
        WHERE spreadsheet_id = %s AND title ILIKE '%%monthly_summary%%'
    """, (ss_id,))
    monthly_sheet = cur.fetchone()
    record("Monthly_Summary sheet exists", monthly_sheet is not None)

    if monthly_sheet:
        ms_id = monthly_sheet[0]
        cur.execute("SELECT COUNT(DISTINCT row_index) FROM gsheet.cells WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index > 1", (ss_id, ms_id,))
        month_rows = cur.fetchone()[0]
        record("Monthly_Summary has at least 10 month rows", month_rows >= 10,
               f"Found {month_rows} month rows")

    cur.close()
    conn.close()


def check_word(agent_workspace):
    print("\n=== Check 2: Engagement_Analysis_Report.docx ===")
    doc_path = os.path.join(agent_workspace, "Engagement_Analysis_Report.docx")
    if not os.path.exists(doc_path):
        record("Engagement_Analysis_Report.docx exists", False, f"Not found at {doc_path}")
        return
    record("Engagement_Analysis_Report.docx exists", True)

    try:
        import docx
        doc = docx.Document(doc_path)
    except Exception as e:
        record("Word document readable", False, str(e))
        return
    record("Word document readable", True)

    full_text = "\n".join(p.text for p in doc.paragraphs).lower()

    required_sections = ["overview", "methodology", "key findings", "monthly trends", "conclusions"]
    sections_found = [s for s in required_sections if s in full_text]
    record("Document has all 5 required sections",
           len(sections_found) >= 5,
           f"Found: {sections_found}, Missing: {[s for s in required_sections if s not in sections_found]}")

    has_methodology_formula = "like_count" in full_text or "like count" in full_text or "engagement rate" in full_text
    record("Methodology section explains engagement rate formula", has_methodology_formula)

    # Key findings should mention top videos
    has_top_video = "open-source" in full_text or "saas" in full_text or "css" in full_text or "hackers" in full_text
    record("Key Findings mentions top engaging videos", has_top_video,
           "No top video keywords found in document")

    has_percentage = "%" in full_text or "percent" in full_text or "6.2" in full_text or "5.9" in full_text
    record("Document contains engagement rate percentages", has_percentage)


def check_email():
    print("\n=== Check 3: Email to research@company.com ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT to_addr, subject, body_text FROM email.messages
        WHERE to_addr::text ILIKE '%research@company.com%'
        AND subject ILIKE '%engagement%'
        ORDER BY id DESC LIMIT 5
    """)
    emails = cur.fetchall()
    cur.close()
    conn.close()

    record("Email to research@company.com with engagement subject exists",
           len(emails) > 0, "No matching email found")

    if emails:
        to_addr, subject, body = emails[0]
        record("Email subject contains 'Fireship YouTube Engagement Analysis'",
               "fireship" in subject.lower() and "engagement" in subject.lower(),
               f"Subject: {subject}")

        body_lower = (body or "").lower()
        has_count = any(str(n) in body_lower for n in range(100, 110))
        record("Email body mentions total video count (~104)",
               has_count or "104" in body_lower or "videos" in body_lower,
               f"Body excerpt: {body_lower[:200]}")


def main():
    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    check_gsheet()
    check_word(args.agent_workspace)
    check_email()

    total = PASS_COUNT + FAIL_COUNT
    if total == 0:
        print("\nFAIL: No checks were performed.")
        sys.exit(1)

    accuracy = PASS_COUNT / total * 100
    print(f"\nOverall: {PASS_COUNT}/{total} checks passed ({accuracy:.1f}%)")

    result = {
        "total_passed": PASS_COUNT,
        "total_checks": total,
        "accuracy": accuracy,
    }

    if args.res_log_file:
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    if accuracy >= 70:
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
