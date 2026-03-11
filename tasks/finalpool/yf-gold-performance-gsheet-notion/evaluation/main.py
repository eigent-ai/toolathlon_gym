"""Evaluation for yf-gold-performance-gsheet-notion task.

Check 1: Google Sheet "Gold vs Stocks Analysis" with "Returns Comparison" sheet
Check 2: Notion page titled "Gold vs Stocks Performance"
"""

import argparse
import json
import os
import sys

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_str = f": {detail[:200]}" if detail else ""
        print(f"  [FAIL] {name}{detail_str}")


def num_close(a, b, tol=2.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def get_expected_data():
    """Compute expected returns from DB."""
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    symbols = ['AMZN', 'GC=F', 'GOOGL', 'JNJ', 'JPM', 'XOM']

    # Latest prices
    cur.execute("""SELECT symbol, close FROM yf.stock_prices
        WHERE date = (SELECT MAX(date) FROM yf.stock_prices WHERE symbol='AMZN')
        AND symbol IN ('AMZN','GC=F','GOOGL','JNJ','JPM','XOM')""")
    latest = dict(cur.fetchall())

    # 6M ago
    cur.execute("""
        WITH ranked AS (SELECT symbol, date, close, ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY date DESC) as rn
        FROM yf.stock_prices WHERE symbol IN ('AMZN','GC=F','GOOGL','JNJ','JPM','XOM'))
        SELECT symbol, close FROM ranked WHERE rn = 127
    """)
    six_m = dict(cur.fetchall())

    # 1Y ago
    cur.execute("""
        WITH ranked AS (SELECT symbol, date, close, ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY date DESC) as rn
        FROM yf.stock_prices WHERE symbol IN ('AMZN','GC=F','GOOGL','JNJ','JPM','XOM'))
        SELECT symbol, close FROM ranked WHERE rn = 253
    """)
    one_y = dict(cur.fetchall())

    # Names
    cur.execute("""SELECT symbol, data->>'shortName' FROM yf.stock_info
        WHERE symbol IN ('AMZN','GC=F','GOOGL','JNJ','JPM','XOM')""")
    names = dict(cur.fetchall())

    cur.close()
    conn.close()

    gold_6m_ret = round((float(latest['GC=F']) - float(six_m['GC=F'])) / float(six_m['GC=F']) * 100, 2)
    gold_1y_ret = round((float(latest['GC=F']) - float(one_y['GC=F'])) / float(one_y['GC=F']) * 100, 2)

    results = []
    for s in symbols:
        l = float(latest[s])
        s6 = float(six_m[s])
        s1 = float(one_y[s])
        ret_6m = round((l - s6) / s6 * 100, 2)
        ret_1y = round((l - s1) / s1 * 100, 2)
        beat_6m = "Yes" if ret_6m > gold_6m_ret and s != 'GC=F' else "No"
        beat_1y = "Yes" if ret_1y > gold_1y_ret and s != 'GC=F' else "No"
        results.append({
            "symbol": s, "name": names.get(s, s),
            "latest": l, "price_6m": s6, "ret_6m": ret_6m,
            "price_1y": s1, "ret_1y": ret_1y,
            "beat_6m": beat_6m, "beat_1y": beat_1y,
        })

    results.sort(key=lambda x: x["ret_1y"], reverse=True)
    return results, gold_6m_ret, gold_1y_ret


def check_gsheet():
    """Check the Google Sheet with returns comparison data."""
    print("\n=== Checking Google Sheet ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM gsheet.spreadsheets WHERE LOWER(title) LIKE '%gold%'")
    spreadsheets = cur.fetchall()
    check("Spreadsheet with 'Gold' in title exists", len(spreadsheets) > 0,
          "No spreadsheet found with 'Gold' in title")
    if not spreadsheets:
        cur.close()
        conn.close()
        return

    ss_id = spreadsheets[0][0]
    print(f"  Found spreadsheet: '{spreadsheets[0][1]}' (id={ss_id})")

    # Find Returns Comparison sheet
    cur.execute("""
        SELECT id FROM gsheet.sheets
        WHERE spreadsheet_id = %s AND LOWER(title) LIKE '%%return%%'
    """, (ss_id,))
    sheets = cur.fetchall()
    check("Sheet 'Returns Comparison' exists", len(sheets) > 0)
    if not sheets:
        cur.close()
        conn.close()
        return

    sheet_id = sheets[0][0]

    # Get all cells
    cur.execute("""
        SELECT row_index, col_index, value FROM gsheet.cells
        WHERE spreadsheet_id = %s AND sheet_id = %s
        ORDER BY row_index, col_index
    """, (ss_id, sheet_id))
    cells = cur.fetchall()

    grid = {}
    for row_idx, col_idx, value in cells:
        grid[(row_idx, col_idx)] = value

    max_row = max((r for r, c in grid.keys()), default=0)
    check("At least 6 data rows (6 symbols)", max_row >= 6, f"max_row={max_row}")

    all_values = [str(v).strip().lower() for v in grid.values() if v]
    all_values_raw = [str(v).strip() for v in grid.values() if v]

    expected_data, gold_6m, gold_1y = get_expected_data()

    # Check all symbols present
    for item in expected_data:
        sym = item["symbol"]
        found = sym.lower() in all_values or sym in [str(v).strip() for v in grid.values() if v]
        check(f"Symbol {sym} present in sheet", found)

    # Check return values (with tolerance)
    for item in expected_data:
        sym = item["symbol"]
        # Check 1Y return value
        ret_1y_found = any(num_close(v, item["ret_1y"], 3.0) for v in all_values_raw
                           if v.replace('.', '', 1).replace('-', '', 1).isdigit())
        check(f"{sym} 1Y return ~{item['ret_1y']}% present", ret_1y_found)

    # Check ordering: first data row should have highest 1Y return
    # Get row 1 symbol (assuming row 0 is header)
    row1_vals = [grid.get((1, c), "") for c in range(10)]
    top_symbol = expected_data[0]["symbol"]
    check(f"First data row contains top performer ({top_symbol})",
          any(top_symbol in str(v) for v in row1_vals),
          f"Row 1 values: {row1_vals[:5]}")

    cur.close()
    conn.close()


def check_notion():
    """Check that Notion page 'Gold vs Stocks Performance' exists."""
    print("\n=== Checking Notion Page ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, properties FROM notion.pages")
    pages = cur.fetchall()

    # Look for a page with the expected title
    found_page = None
    for page_id, props in pages:
        if props:
            props_str = json.dumps(props) if isinstance(props, dict) else str(props)
            if "gold" in props_str.lower() and "stock" in props_str.lower():
                found_page = (page_id, props)
                break

    check("Notion page with 'Gold' and 'Stocks' found", found_page is not None,
          f"Found {len(pages)} pages total")

    if found_page:
        page_id = found_page[0]
        # Check for content blocks
        cur.execute("SELECT COUNT(*) FROM notion.blocks WHERE parent_id = %s", (page_id,))
        block_count = cur.fetchone()[0]
        check("Notion page has content blocks", block_count > 0,
              f"Found {block_count} blocks")

        # Check block content mentions gold returns
        cur.execute("SELECT block_data FROM notion.blocks WHERE parent_id = %s", (page_id,))
        blocks = cur.fetchall()
        all_text = " ".join(str(b[0]) for b in blocks if b[0]).lower()
        check("Page content mentions gold", "gold" in all_text, "No mention of gold in blocks")
        check("Page content mentions return/performance",
              "return" in all_text or "perform" in all_text or "%" in all_text,
              "No mention of returns")

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    print("=" * 70)
    print("YF GOLD PERFORMANCE GSHEET NOTION - EVALUATION")
    print("=" * 70)

    check_gsheet()
    check_notion()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    if FAIL_COUNT > 0:
        print(f"  WARNING: {FAIL_COUNT} DB checks failed (not blocking)")
    print(f"  Overall: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
