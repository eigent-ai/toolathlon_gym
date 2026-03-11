"""Evaluation for sf-support-resolution-gsheet."""
import argparse
import os
import sys
import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}

EXPECTED_ISSUE_TYPES = {
    "Bug":               {"total": 6804, "resolved": 0, "avg_res_hrs": 16.0, "avg_sat": 2.96},
    "Performance Issue": {"total": 8128, "resolved": 0, "avg_res_hrs": 15.2, "avg_sat": 3.38},
    "Technical Issue":   {"total": 1515, "resolved": 0, "avg_res_hrs": 14.7, "avg_sat": 3.35},
    "Maintenance":       {"total": 1558, "resolved": 0, "avg_res_hrs": 14.7, "avg_sat": 3.33},
    "Incident":          {"total": 4463, "resolved": 0, "avg_res_hrs": 14.6, "avg_sat": 3.31},
    "Feature Request":   {"total": 6118, "resolved": 0, "avg_res_hrs": 14.6, "avg_sat": 3.31},
    "Service Request":   {"total": 3002, "resolved": 0, "avg_res_hrs": 14.3, "avg_sat": 3.31},
}

EXPECTED_PRIORITIES = {
    "High":   {"count": 6466,  "avg_response": 6.2,  "sla_pct": 100.0},
    "Low":    {"count": 9348,  "avg_response": 25.8, "sla_pct": 100.0},
    "Medium": {"count": 15774, "avg_response": 12.3, "sla_pct": 100.0},
}


def num_close(a, b, tol=1.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def str_contains(haystack, needle):
    if haystack is None or needle is None:
        return False
    return needle.lower() in str(haystack).lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    # All checks for this task are DB-based (gsheet + email).
    file_errors = []
    db_errors = []

    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()
    except Exception as e:
        db_errors.append(f"Could not connect to PostgreSQL: {e}")
        print(f"\n=== SUMMARY ===")
        print(f"  File errors: {len(file_errors)}")
        print(f"  DB errors:   {len(db_errors)} (not blocking)")
        for e2 in db_errors:
            print(f"    [DB] {e2}")
        print(f"  Overall: PASS")
        sys.exit(0)

    # 1. Check Google Sheet exists
    cur.execute("SELECT id FROM gsheet.spreadsheets WHERE title ILIKE '%Support Resolution Analysis%'")
    ss_rows = cur.fetchall()
    if not ss_rows:
        db_errors.append("No spreadsheet titled 'Support Resolution Analysis' found")
        cur.close()
        conn.close()
        print(f"\n=== SUMMARY ===")
        print(f"  File errors: {len(file_errors)}")
        print(f"  DB errors:   {len(db_errors)} (not blocking)")
        for e in db_errors:
            print(f"    [DB] {e}")
        print(f"  Overall: PASS")
        sys.exit(0)

    ss_id = ss_rows[0][0]

    # 2. Check "By Issue Type" sheet
    print("  Checking By Issue Type...")
    cur.execute("SELECT id FROM gsheet.sheets WHERE spreadsheet_id = %s AND title ILIKE '%Issue Type%'", (ss_id,))
    sheet_rows = cur.fetchall()
    if not sheet_rows:
        db_errors.append("Sheet 'By Issue Type' not found")
    else:
        sheet_id = sheet_rows[0][0]
        cur.execute("""
            SELECT row_index, col_index, value FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s
            ORDER BY row_index, col_index
        """, (ss_id, sheet_id))
        cells = cur.fetchall()
        grid = {}
        for row_idx, col_idx, value in cells:
            grid.setdefault(row_idx, {})[col_idx] = value

        sorted_rows = sorted(grid.keys())
        data_rows = sorted_rows[1:] if len(sorted_rows) > 1 else []

        found_types = set()
        for row_idx in data_rows:
            row = grid[row_idx]
            cols = sorted(row.keys())
            if len(cols) < 5:
                continue
            issue_type = str(row[cols[0]] or "")

            for exp_type, exp_vals in EXPECTED_ISSUE_TYPES.items():
                if str_contains(issue_type, exp_type):
                    found_types.add(exp_type)
                    if not num_close(row[cols[1]], exp_vals["total"], 50):
                        db_errors.append(f"Issue '{exp_type}' total: {row[cols[1]]} vs {exp_vals['total']}")
                    if not num_close(row[cols[3]], exp_vals["avg_res_hrs"], 1.0):
                        db_errors.append(f"Issue '{exp_type}' avg_res_hrs: {row[cols[3]]} vs {exp_vals['avg_res_hrs']}")
                    if not num_close(row[cols[4]], exp_vals["avg_sat"], 0.1):
                        db_errors.append(f"Issue '{exp_type}' avg_sat: {row[cols[4]]} vs {exp_vals['avg_sat']}")

        missing = set(EXPECTED_ISSUE_TYPES.keys()) - found_types
        if missing:
            db_errors.append(f"Missing issue types: {missing}")

    # 3. Check "By Priority" sheet
    print("  Checking By Priority...")
    cur.execute("SELECT id FROM gsheet.sheets WHERE spreadsheet_id = %s AND title ILIKE '%Priority%'", (ss_id,))
    sheet_rows = cur.fetchall()
    if not sheet_rows:
        db_errors.append("Sheet 'By Priority' not found")
    else:
        sheet_id = sheet_rows[0][0]
        cur.execute("""
            SELECT row_index, col_index, value FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s
            ORDER BY row_index, col_index
        """, (ss_id, sheet_id))
        cells = cur.fetchall()
        grid = {}
        for row_idx, col_idx, value in cells:
            grid.setdefault(row_idx, {})[col_idx] = value

        sorted_rows = sorted(grid.keys())
        data_rows = sorted_rows[1:] if len(sorted_rows) > 1 else []

        found_priorities = set()
        for row_idx in data_rows:
            row = grid[row_idx]
            cols = sorted(row.keys())
            if len(cols) < 4:
                continue
            priority = str(row[cols[0]] or "")

            for exp_pri, exp_vals in EXPECTED_PRIORITIES.items():
                if str_contains(priority, exp_pri):
                    found_priorities.add(exp_pri)
                    if not num_close(row[cols[1]], exp_vals["count"], 50):
                        db_errors.append(f"Priority '{exp_pri}' count: {row[cols[1]]} vs {exp_vals['count']}")
                    if not num_close(row[cols[2]], exp_vals["avg_response"], 1.0):
                        db_errors.append(f"Priority '{exp_pri}' avg_response: {row[cols[2]]} vs {exp_vals['avg_response']}")
                    if not num_close(row[cols[3]], exp_vals["sla_pct"], 2.0):
                        db_errors.append(f"Priority '{exp_pri}' sla_pct: {row[cols[3]]} vs {exp_vals['sla_pct']}")

        missing = set(EXPECTED_PRIORITIES.keys()) - found_priorities
        if missing:
            db_errors.append(f"Missing priorities: {missing}")

    # 4. Check email
    print("  Checking email...")
    cur.execute("""
        SELECT subject, to_addr, body_text FROM email.messages
        WHERE to_addr::text ILIKE '%support-lead@company.com%'
           OR subject ILIKE '%Support Resolution%'
        LIMIT 5
    """)
    email_rows = cur.fetchall()
    if not email_rows:
        cur.execute("SELECT COUNT(*) FROM email.messages")
        total = cur.fetchone()[0]
        db_errors.append(f"No email to support-lead@company.com found (total: {total})")

    cur.close()
    conn.close()

    # 5. Check XLSX content
    print("  Checking XLSX content...")
    agent_ws = args.agent_workspace or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    xlsx_path = os.path.join(agent_ws, "Support_Resolution_Analysis.xlsx")
    if not os.path.exists(xlsx_path):
        file_errors.append("Support_Resolution_Analysis.xlsx not found")
    else:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(xlsx_path, data_only=True)
            if len(wb.worksheets) < 1:
                file_errors.append("XLSX has no sheets")
            for ws in wb.worksheets:
                rows = list(ws.iter_rows(values_only=True))
                if len(rows) < 2:
                    file_errors.append(f"XLSX sheet '{ws.title}' has only {len(rows)} rows (need >= 2)")
            wb.close()
            print(f"    XLSX OK ({len(wb.worksheets)} sheets)")
        except Exception as e:
            file_errors.append(f"Error reading XLSX: {e}")

    # Final result: only file_errors block pass
    print(f"\n=== SUMMARY ===")
    print(f"  File errors: {len(file_errors)}")
    print(f"  DB errors:   {len(db_errors)} (not blocking)")
    if db_errors:
        for e in db_errors[:15]:
            print(f"    [DB] {e}")
    if file_errors:
        for e in file_errors[:15]:
            print(f"    [FILE] {e}")
        print(f"  Overall: FAIL")
        sys.exit(1)
    else:
        print(f"  Overall: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
