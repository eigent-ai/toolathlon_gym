"""
Check that the agent created the Google Sheet with correct course overview data.
Queries the gsheet schema in PostgreSQL.
"""

import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

EXPECTED_COURSE_CODES = [
    "AAA-2014J", "BBB-2014J", "CCC-2014J", "DDD-2014J",
    "EEE-2014J", "FFF-2014J", "GGG-2014J",
]


def num_close(a, b, tol=0.5):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def query_expected_overview():
    """Query expected course overview data from Canvas tables."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.course_code,
            (SELECT COUNT(*) FROM canvas.enrollments e
             WHERE e.course_id = c.id AND e.type = 'StudentEnrollment') as enrolled,
            ROUND(AVG(s.score::float)::numeric, 2) as avg_score
        FROM canvas.courses c
        JOIN canvas.assignments a ON a.course_id = c.id
        JOIN canvas.submissions s ON s.assignment_id = a.id AND s.score IS NOT NULL
        WHERE c.course_code LIKE '%%2014J%%'
        GROUP BY c.id, c.course_code
        ORDER BY c.course_code
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {r[0]: (int(r[1]), float(r[2])) for r in rows}


def check_gsheet():
    """
    Verify the Google Sheet was created with correct course overview data.
    Returns (passed_count, failed_count, error_details).
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    passed = 0
    failed = 0
    errors = []

    # Check that a spreadsheet with "fall 2014" in the title exists
    cur.execute("""
        SELECT id, title FROM gsheet.spreadsheets
        WHERE LOWER(title) LIKE '%%fall 2014%%'
    """)
    spreadsheets = cur.fetchall()

    if not spreadsheets:
        cur.close()
        conn.close()
        return 0, 1, ["No Google Sheet found with 'Fall 2014' in title"]

    ss_id = spreadsheets[0][0]
    ss_title = spreadsheets[0][1]
    passed += 1
    print(f"  [check_gsheet] Found spreadsheet: '{ss_title}' (id={ss_id})")

    # Find any sheet in the spreadsheet
    cur.execute("""
        SELECT id, title FROM gsheet.sheets
        WHERE spreadsheet_id = %s
        ORDER BY id LIMIT 1
    """, (ss_id,))
    sheets = cur.fetchall()

    if not sheets:
        failed += 1
        errors.append("No sheets found in the spreadsheet")
        cur.close()
        conn.close()
        return passed, failed, errors

    sheet_id = sheets[0][0]
    passed += 1

    # Fetch all cells for this sheet
    cur.execute("""
        SELECT row_index, col_index, value FROM gsheet.cells
        WHERE spreadsheet_id = %s AND sheet_id = %s
        ORDER BY row_index, col_index
    """, (ss_id, sheet_id))

    cells = {}
    for row_idx, col_idx, value in cur.fetchall():
        cells[(row_idx, col_idx)] = value

    cur.close()
    conn.close()

    if not cells:
        failed += 1
        errors.append("No cells found in the sheet")
        return passed, failed, errors

    # Get expected data
    try:
        expected = query_expected_overview()
    except Exception as e:
        return passed, 1, errors + [f"Error querying expected data: {e}"]

    # Find rows containing course codes
    max_row = max(r for r, c in cells.keys())
    max_col = max(c for r, c in cells.keys())

    data_rows = {}
    for row_idx in range(0, max_row + 1):
        row_vals = []
        for col_idx in range(0, max_col + 1):
            row_vals.append(cells.get((row_idx, col_idx), ""))
        for val in row_vals:
            if val and "2014J" in str(val):
                data_rows[str(val).strip()] = row_vals
                break

    # Check each expected course code is present
    for code in EXPECTED_COURSE_CODES:
        if code not in data_rows:
            failed += 1
            errors.append(f"GSheet: Course {code} not found")
            continue

        row_vals = data_rows[code]
        exp_enrolled, exp_avg = expected.get(code, (0, 0))

        enrolled_found = False
        avg_found = False

        for val in row_vals:
            val_str = str(val).strip()
            if num_close(val_str, exp_enrolled, 1):
                enrolled_found = True
            if num_close(val_str, exp_avg, 0.5):
                avg_found = True

        row_ok = True
        if not enrolled_found:
            row_ok = False
            errors.append(f"GSheet {code}: enrolled count {exp_enrolled} not found")
        if not avg_found:
            row_ok = False
            errors.append(f"GSheet {code}: avg score {exp_avg} not found")

        if row_ok:
            passed += 1
        else:
            failed += 1

    return passed, failed, errors
