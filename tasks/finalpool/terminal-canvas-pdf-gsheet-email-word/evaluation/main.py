"""Evaluation script for terminal-canvas-pdf-gsheet-email-word."""
import os
import argparse, json, os, sys

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel"
}

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_str = str(detail)[:200] if detail else ""
        print(f"  [FAIL] {name}: {detail_str}")


def get_conn():
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)


def check_gsheet():
    print("\n=== Checking Google Sheets ===")
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT id, title FROM gsheet.spreadsheets WHERE LOWER(title) LIKE %s",
                    ("%faculty%workload%tracker%",))
        rows = cur.fetchall()
        if not rows:
            cur.execute("SELECT id, title FROM gsheet.spreadsheets")
            all_ss = cur.fetchall()
            check("Faculty_Workload_Tracker spreadsheet exists", False,
                  f"Found: {[r[1] for r in all_ss]}")
            cur.close()
            conn.close()
            return False

        check("Faculty_Workload_Tracker spreadsheet exists", True)
        ss_id = rows[0][0]

        cur.execute("SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s", (ss_id,))
        sheets = cur.fetchall()
        sheet_titles = [s[1].lower() for s in sheets]

        has_workload = any("workload" in t or "course" in t for t in sheet_titles)
        has_summary = any("summary" in t or "subject" in t for t in sheet_titles)
        check("Course_Workload sheet exists", has_workload, f"Sheets: {sheet_titles}")
        check("Subject_Summary sheet exists", has_summary, f"Sheets: {sheet_titles}")

        # Check Course_Workload content
        workload_sheet_id = None
        for sid, title in sheets:
            if "workload" in title.lower() or "course" in title.lower():
                workload_sheet_id = sid
                break

        if workload_sheet_id:
            cur.execute("SELECT row_index, col_index, value FROM gsheet.cells WHERE sheet_id = %s ORDER BY row_index, col_index",
                        (workload_sheet_id,))
            cells = cur.fetchall()
            data_rows = set(r for r, c, v in cells if r > 0 and v and str(v).strip())
            # Query dynamic course count from Canvas DB
            try:
                conn2 = get_conn()
                cur2 = conn2.cursor()
                cur2.execute("SELECT COUNT(*) FROM canvas.courses")
                expected_workload_rows = cur2.fetchone()[0]
                cur2.close(); conn2.close()
            except Exception:
                expected_workload_rows = 20
            check(f"Course_Workload has >= {expected_workload_rows} rows",
                  len(data_rows) >= expected_workload_rows,
                  f"Found {len(data_rows)} data rows")

            # Check headers
            headers = [str(v).lower() for r, c, v in cells if r == 0 and v]
            has_name = any("name" in h or "course" in h for h in headers)
            has_assign = any("assign" in h for h in headers)
            check("Course_Workload has course name column", has_name, f"Headers: {headers}")
            check("Course_Workload has assignment column", has_assign, f"Headers: {headers}")

        # Check Subject_Summary content
        summary_sheet_id = None
        for sid, title in sheets:
            if "summary" in title.lower() or "subject" in title.lower():
                summary_sheet_id = sid
                break

        if summary_sheet_id:
            cur.execute("SELECT row_index, col_index, value FROM gsheet.cells WHERE sheet_id = %s ORDER BY row_index, col_index",
                        (summary_sheet_id,))
            cells = cur.fetchall()
            data_rows = set(r for r, c, v in cells if r > 0 and v and str(v).strip())
            # Query dynamic unique subject count from Canvas DB
            try:
                conn3 = get_conn()
                cur3 = conn3.cursor()
                cur3.execute("SELECT COUNT(DISTINCT regexp_replace(name, ' \\(.*\\)$', '')) FROM canvas.courses")
                expected_subject_rows = cur3.fetchone()[0]
                cur3.close(); conn3.close()
            except Exception:
                expected_subject_rows = 7
            check(f"Subject_Summary has >= {expected_subject_rows} rows",
                  len(data_rows) >= expected_subject_rows,
                  f"Found {len(data_rows)} data rows")

            all_values = [str(v).lower() for _, _, v in cells if v]
            has_heavy = any("heavy" in v for v in all_values)
            check("Subject_Summary has Heavy rating", has_heavy, f"Values sample: {all_values[:15]}")

        cur.close()
        conn.close()
        return True
    except Exception as e:
        check("Google Sheets accessible", False, str(e))
        return False


def check_word(agent_workspace):
    print("\n=== Checking Word Document ===")
    word_path = os.path.join(agent_workspace, "Faculty_Workload_Report.docx")
    check("Faculty_Workload_Report.docx exists", os.path.exists(word_path))
    if os.path.exists(word_path):
        from docx import Document
        doc = Document(word_path)
        text = " ".join(p.text for p in doc.paragraphs).lower()
        check("Word has substantial content", len(text) > 300, f"length: {len(text)}")
        check("Word mentions workload", "workload" in text)
        check("Word mentions subjects", "finance" in text or "biochem" in text)
        check("Word mentions recommendations", "recommend" in text)


def check_emails():
    print("\n=== Checking Emails ===")
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT subject, to_addr FROM email.messages WHERE subject ILIKE %s",
                    ('%faculty%workload%',))
        emails = cur.fetchall()
        check("Faculty workload email sent", len(emails) >= 1, f"found {len(emails)}")
        if emails:
            check("Email to department-chairs", "department-chairs" in str(emails[0][1]).lower() or "chair" in str(emails[0][1]).lower(),
                  f"to: {emails[0][1]}")

        cur.execute("SELECT subject, to_addr FROM email.messages WHERE subject ILIKE %s",
                    ('%workload%standards%compliance%',))
        compliance = cur.fetchall()
        check("Compliance report email sent", len(compliance) >= 1, f"found {len(compliance)}")

        cur.close()
        conn.close()
    except Exception as e:
        check("Email checks", False, str(e))


def check_script(agent_workspace):
    print("\n=== Checking Terminal Script ===")
    check("workload_analyzer.py exists",
          os.path.exists(os.path.join(agent_workspace, "workload_analyzer.py")))


def check_reverse_validation(agent_workspace):
    print("\n=== Reverse Validation ===")
    # Check no emails sent to wrong recipients
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT to_addr FROM email.messages
            WHERE subject ILIKE '%%faculty%%workload%%'
               OR subject ILIKE '%%workload%%standards%%'
        """)
        emails = cur.fetchall()
        noise_recipients = ["all-staff@university.edu", "students@university.edu"]
        for email_row in emails:
            to_str = str(email_row[0]).lower()
            for noise in noise_recipients:
                if noise in to_str:
                    check("No workload emails sent to wrong recipients", False,
                          f"Sent to noise recipient: {noise}")
                    cur.close(); conn.close()
                    return
        check("No workload emails sent to wrong recipients", True)
        cur.close(); conn.close()
    except Exception as e:
        check("Reverse validation", False, str(e))


def run_evaluation(agent_workspace, groundtruth_workspace, launch_time, res_log_file):
    global PASS_COUNT, FAIL_COUNT
    PASS_COUNT = 0
    FAIL_COUNT = 0

    check_gsheet()
    check_word(agent_workspace)
    check_emails()
    check_script(agent_workspace)
    check_reverse_validation(agent_workspace)

    return FAIL_COUNT == 0, f"Passed {PASS_COUNT}/{PASS_COUNT + FAIL_COUNT} checks"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    success, message = run_evaluation(
        args.agent_workspace, args.groundtruth_workspace,
        args.launch_time, args.res_log_file
    )
    print(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
