"""
Evaluation for yf-dividend-tracker-gsheet.
Checks:
1. Google Sheet "Dividend Tracker" exists in DB with correct stock action data
2. Email sent to investor@portfolio.example.com with dividend summary
"""
import argparse
import json
import os
import sys
from datetime import datetime

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


def str_match(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return str(a).strip().lower() == str(b).strip().lower()


def num_close(a, b, tol=0.1):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def get_expected_data():
    """Query YF DB for expected dividend/action data."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT symbol, data FROM yf.stock_info WHERE symbol IN ('GOOGL','AMZN','JPM','JNJ','XOM') ORDER BY symbol")
    rows = cur.fetchall()

    dividend_stocks = []
    for symbol, data in rows:
        d = data if isinstance(data, dict) else json.loads(data)
        div_rate = d.get('dividendRate')
        if div_rate and float(div_rate) > 0:
            dividend_stocks.append(symbol)

    cur.close()
    conn.close()
    return dividend_stocks


def check_gsheet():
    """Check Google Sheet data in DB."""
    print("\n=== Checking Google Sheet ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Find spreadsheet with "dividend" or "tracker" in title
    cur.execute("""
        SELECT id, title FROM gsheet.spreadsheets
        WHERE LOWER(title) LIKE '%dividend%' OR LOWER(title) LIKE '%tracker%'
    """)
    spreadsheets = cur.fetchall()
    record("Spreadsheet exists", len(spreadsheets) > 0,
           f"No spreadsheet with 'dividend' or 'tracker' found")

    if not spreadsheets:
        cur.close()
        conn.close()
        return False

    sp_id = spreadsheets[0][0]
    print(f"  Found spreadsheet: {spreadsheets[0][1]} (id={sp_id})")

    # Check sheets
    cur.execute("SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s", (sp_id,))
    sheets = cur.fetchall()
    record("At least one sheet exists", len(sheets) > 0)

    if not sheets:
        cur.close()
        conn.close()
        return False

    sheet_id = sheets[0][0]

    # Check cells for content
    cur.execute("""
        SELECT row_index, col_index, value FROM gsheet.cells
        WHERE spreadsheet_id = %s AND sheet_id = %s
        ORDER BY row_index, col_index
    """, (sp_id, sheet_id))
    cells = cur.fetchall()
    record("Sheet has data cells", len(cells) > 5, f"Only {len(cells)} cells found")

    # Check for required symbols in cells
    all_values = " ".join(str(c[2]).lower() for c in cells if c[2])
    for symbol in ['googl', 'jnj', 'jpm', 'xom']:
        record(f"Sheet contains {symbol.upper()}", symbol in all_values)

    # Check for dividend-related content
    record("Sheet mentions dividend",
           "dividend" in all_values or "div" in all_values,
           "No dividend references found")

    cur.close()
    conn.close()
    return True


def check_email():
    """Check email sent to investor."""
    print("\n=== Checking Email ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT subject, from_addr, to_addr, body_text FROM email.messages")
    emails = cur.fetchall()
    record("At least 1 email sent", len(emails) >= 1, f"Found {len(emails)}")

    found = False
    for subject, from_addr, to_addr, body_text in emails:
        subject_lower = (subject or "").lower()
        to_str = str(to_addr or "").lower()
        if "dividend" in subject_lower or "action" in subject_lower:
            found = True
            record("Email subject mentions dividend/action", True)
            record("Email sent to investor",
                   "investor@portfolio.example.com" in to_str,
                   f"To: {to_addr}")
            body_lower = (body_text or "").lower()
            record("Email body mentions GOOGL", "googl" in body_lower)
            record("Email body mentions dividend info",
                   "dividend" in body_lower,
                   "No dividend reference in body")
            break

    if not found:
        record("Dividend summary email exists", False,
               "No email with 'dividend' or 'action' in subject")

    cur.close()
    conn.close()
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    dividend_stocks = get_expected_data()
    print(f"[eval] Expected dividend stocks: {dividend_stocks}")

    gsheet_ok = check_gsheet()
    email_ok = check_email()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    overall = PASS_COUNT > 0 and FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
