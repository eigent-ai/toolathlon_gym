"""
Evaluation script for playwright-yf-market-dashboard-gsheet-word task.

Checks:
1. Google Sheet "Weekly_Market_Analysis" with sector and stock data
2. Weekly_Market_Report.docx with executive summary
3. Email sent with market analysis
"""

import argparse
import json
import os
import sys

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
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


def num_close(a, b, tol=5.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def str_contains(haystack, needle):
    if haystack is None or needle is None:
        return False
    return needle.strip().lower() in str(haystack).strip().lower()


# Expected sector data from dashboard
SECTOR_DATA = {
    "communication services": {"weekly": 2.8, "index": 118.5, "ytd": 12.4},
    "consumer cyclical": {"weekly": -1.2, "index": 105.3, "ytd": 5.7},
    "financial services": {"weekly": 1.5, "index": 112.8, "ytd": 8.9},
    "healthcare": {"weekly": 0.3, "index": 98.7, "ytd": -2.1},
    "energy": {"weekly": 3.1, "index": 122.4, "ytd": 15.2},
}

STOCK_PRICES = {
    "GOOGL": 300.88,
    "AMZN": 218.94,
    "JPM": 293.55,
    "JNJ": 239.63,
    "XOM": 150.76,
}


def check_gsheet():
    """Check Google Sheet with sector and stock data."""
    print("\n=== Checking Google Sheet ===")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Find spreadsheet
        cur.execute("SELECT id, title FROM gsheet.spreadsheets")
        spreadsheets = cur.fetchall()

        found_ss = None
        for ss_id, title in spreadsheets:
            if title and "market" in title.lower():
                found_ss = ss_id
                break

        if not found_ss:
            record("Google Sheet 'Weekly_Market_Analysis' exists", False,
                   f"Found spreadsheets: {[t for _, t in spreadsheets]}")
            cur.close()
            conn.close()
            return False

        record("Google Sheet exists", True)

        # Check sheets
        cur.execute("SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s", (found_ss,))
        sheets = cur.fetchall()
        sheet_names = [t.lower() for _, t in sheets]

        sector_sheet_id = None
        stock_sheet_id = None
        for s_id, s_title in sheets:
            if "sector" in s_title.lower() or "performance" in s_title.lower():
                sector_sheet_id = s_id
            if "stock" in s_title.lower():
                stock_sheet_id = s_id

        has_sector = sector_sheet_id is not None
        has_stock = stock_sheet_id is not None
        record("Has Sector Performance sheet", has_sector, f"Sheets: {sheet_names}")
        record("Has Stock vs Sector sheet", has_stock, f"Sheets: {sheet_names}")

        all_ok = has_sector and has_stock

        # Check sector sheet data
        if sector_sheet_id:
            cur.execute("""
                SELECT row_index, col_index, value FROM gsheet.cells
                WHERE spreadsheet_id = %s AND sheet_id = %s
                ORDER BY row_index, col_index
            """, (found_ss, sector_sheet_id))
            cells = cur.fetchall()

            # Build grid
            grid = {}
            for row, col, val in cells:
                if row not in grid:
                    grid[row] = {}
                grid[row][col] = val

            # Count data rows (excluding header)
            data_rows = {r for r in grid if r > 0}  # row 0 is usually header
            if not data_rows:
                data_rows = {r for r in grid if r > 1}

            ok = len(data_rows) >= 5
            record("Sector sheet has >= 5 data rows", ok, f"Found {len(data_rows)} rows")
            if not ok:
                all_ok = False

            # Check that sector names appear in the data
            all_values = " ".join(str(v).lower() for r in grid.values() for v in r.values())
            for sector_key in ["communication", "energy", "financial", "healthcare"]:
                ok = sector_key in all_values
                record(f"Sector '{sector_key}' in sheet data", ok)
                if not ok:
                    all_ok = False

        # Check stock sheet data
        if stock_sheet_id:
            cur.execute("""
                SELECT row_index, col_index, value FROM gsheet.cells
                WHERE spreadsheet_id = %s AND sheet_id = %s
                ORDER BY row_index, col_index
            """, (found_ss, stock_sheet_id))
            cells = cur.fetchall()

            all_values = " ".join(str(v).upper() for _, _, v in cells)
            for ticker in ["GOOGL", "AMZN", "JPM", "JNJ", "XOM"]:
                ok = ticker in all_values
                record(f"Ticker {ticker} in stock sheet", ok)
                if not ok:
                    all_ok = False

        cur.close()
        conn.close()
        return all_ok

    except Exception as e:
        record("Google Sheet DB accessible", False, str(e))
        return False


def check_word(agent_workspace):
    """Check Weekly_Market_Report.docx."""
    print("\n=== Checking Word Output ===")

    fpath = os.path.join(agent_workspace, "Weekly_Market_Report.docx")
    if not os.path.isfile(fpath):
        record("Word file exists", False, f"Not found: {fpath}")
        return False

    record("Word file exists", True)

    try:
        from docx import Document
        doc = Document(fpath)
        full_text = "\n".join(p.text for p in doc.paragraphs).lower()
    except Exception as e:
        record("Word file readable", False, str(e))
        return False

    all_ok = True

    checks = [
        ("Mentions Energy sector", "energy" in full_text),
        ("Mentions Communication Services", "communication" in full_text),
        ("Mentions Consumer Cyclical", "consumer" in full_text),
        ("Mentions GOOGL or Google", "googl" in full_text or "google" in full_text),
        ("Mentions best/worst or performance", "best" in full_text or "worst" in full_text or
         "top" in full_text or "performing" in full_text or "performance" in full_text),
        ("Mentions weekly return", "weekly" in full_text or "return" in full_text),
    ]

    for name, cond in checks:
        record(name, cond)
        if not cond:
            all_ok = False

    return all_ok


def check_email():
    """Check email with market analysis."""
    print("\n=== Checking Email ===")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT subject, from_addr, to_addr, body_text FROM email.messages")
        emails = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        record("Email DB accessible", False, str(e))
        return False

    all_ok = True
    found_email = False

    for subject, from_addr, to_addr, body_text in emails:
        subj_lower = (subject or "").lower()
        if "market" in subj_lower and ("analysis" in subj_lower or "report" in subj_lower):
            found_email = True
            record("Market analysis email exists", True)

            from_ok = str_contains(from_addr, "analyst") or str_contains(from_addr, "investment")
            record("Email from analyst address", from_ok, f"From: {from_addr}")
            if not from_ok:
                all_ok = False

            body_lower = (body_text or "").lower()
            body_ok = ("energy" in body_lower or "consumer" in body_lower or
                       "sector" in body_lower)
            record("Email body mentions sectors", body_ok,
                   f"Body preview: {(body_text or '')[:200]}")
            if not body_ok:
                all_ok = False
            break

    if not found_email:
        record("Market analysis email exists", False,
               f"Found {len(emails)} emails, none matching")
        all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    gsheet_ok = check_gsheet()
    word_ok = check_word(args.agent_workspace)
    email_ok = check_email()

    print(f"\n=== SUMMARY ===")
    print(f"  GSheet: {'PASS' if gsheet_ok else 'FAIL'}")
    print(f"  Word:   {'PASS' if word_ok else 'FAIL'}")
    print(f"  Email:  {'PASS' if email_ok else 'FAIL'}")
    print(f"  Passed: {PASS_COUNT}, Failed: {FAIL_COUNT}")

    overall = gsheet_ok and word_ok and email_ok
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
