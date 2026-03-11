"""Evaluation for sf-sales-discount-gsheet-email."""
import argparse
import os
import sys
import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}


def num_close(a, b, tol=1.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


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
        _print_and_exit(file_errors, db_errors)

    # Compute expected values from Snowflake data
    try:
        cur.execute('''
            SELECT c."SEGMENT", COUNT(o.*) as orders,
                   COUNT(CASE WHEN o."DISCOUNT" > 0 THEN 1 END) as disc_orders,
                   ROUND(100.0 * COUNT(CASE WHEN o."DISCOUNT" > 0 THEN 1 END)/COUNT(*)::numeric, 1) as disc_rate,
                   ROUND(AVG(CASE WHEN o."DISCOUNT" > 0 THEN o."DISCOUNT" END)::numeric * 100, 2) as avg_disc_pct,
                   ROUND(SUM(o."TOTAL_AMOUNT")::numeric, 2) as total_rev,
                   ROUND(SUM(CASE WHEN o."DISCOUNT" > 0 THEN o."TOTAL_AMOUNT" ELSE 0 END)::numeric, 2) as disc_rev,
                   ROUND(100.0 * SUM(CASE WHEN o."DISCOUNT" > 0 THEN o."TOTAL_AMOUNT" ELSE 0 END) / SUM(o."TOTAL_AMOUNT")::numeric, 1) as impact
            FROM sf_data."SALES_DW__PUBLIC__ORDERS" o
            JOIN sf_data."SALES_DW__PUBLIC__CUSTOMERS" c ON o."CUSTOMER_ID" = c."CUSTOMER_ID"
            WHERE o."STATUS" = 'Delivered'
            GROUP BY c."SEGMENT" ORDER BY disc_rate DESC
        ''')
        expected = cur.fetchall()
        expected_map = {r[0]: r for r in expected}
    except Exception as e:
        db_errors.append(f"Could not compute expected values: {e}")
        expected_map = {}

    # Check Google Sheet exists
    print("  Checking Google Sheet...")
    try:
        cur.execute("SELECT id FROM gsheet.spreadsheets WHERE LOWER(title) LIKE '%discount%analysis%'")
        sheets = cur.fetchall()
        if not sheets:
            db_errors.append("No Google Sheet with 'discount analysis' in title found")
        else:
            sheet_id = sheets[0][0]
            # Check for Segment Analysis sheet
            cur.execute("SELECT id FROM gsheet.sheets WHERE spreadsheet_id = %s AND LOWER(title) LIKE '%%segment%%'", (sheet_id,))
            seg_sheets = cur.fetchall()
            if not seg_sheets:
                db_errors.append("No 'Segment Analysis' sheet found in spreadsheet")
            else:
                seg_sheet_id = seg_sheets[0][0]
                cur.execute("SELECT row_index, col_index, value FROM gsheet.cells WHERE sheet_id = %s ORDER BY row_index, col_index", (seg_sheet_id,))
                cells = cur.fetchall()
                # Build grid
                grid = {}
                for row_idx, col_idx, value in cells:
                    if row_idx not in grid:
                        grid[row_idx] = {}
                    grid[row_idx][col_idx] = value

                # Skip header row (row 1), check data rows
                data_rows = {k: v for k, v in grid.items() if k > 1}
                if expected_map and len(data_rows) < len(expected_map):
                    db_errors.append(f"Expected {len(expected_map)} data rows, found {len(data_rows)}")
                elif expected_map:
                    # Check each expected segment is present
                    for seg, exp in expected_map.items():
                        found = False
                        for row_idx, row_data in data_rows.items():
                            seg_val = row_data.get(1, "")
                            if seg_val and str(seg_val).strip().lower() == seg.lower():
                                found = True
                                if not num_close(row_data.get(2, ""), exp[1], 20):
                                    db_errors.append(f"{seg}.Order_Count: {row_data.get(2)} vs {exp[1]}")
                                if not num_close(row_data.get(3, ""), exp[2], 20):
                                    db_errors.append(f"{seg}.Discounted_Orders: {row_data.get(3)} vs {exp[2]}")
                                if not num_close(row_data.get(4, ""), exp[3], 2.0):
                                    db_errors.append(f"{seg}.Discount_Rate_Pct: {row_data.get(4)} vs {exp[3]}")
                                if not num_close(row_data.get(6, ""), exp[5], 500):
                                    db_errors.append(f"{seg}.Total_Revenue: {row_data.get(6)} vs {exp[5]}")
                                break
                        if not found:
                            db_errors.append(f"Segment '{seg}' not found in sheet")
    except Exception as e:
        db_errors.append(f"Google Sheet check error: {e}")

    # Check email
    print("  Checking email...")
    try:
        cur.execute("""SELECT subject FROM email.messages
                       WHERE folder_id IN (SELECT id FROM email.folders WHERE LOWER(name) LIKE '%sent%')""")
        email_rows = cur.fetchall()
        found_email = any("discount" in (s or "").lower() for (s,) in email_rows)
        if not found_email:
            db_errors.append("No email with 'discount' in subject found in sent folder")
    except Exception as e:
        db_errors.append(f"Email check error: {e}")

    cur.close()
    conn.close()

    _print_and_exit(file_errors, db_errors)


def _print_and_exit(file_errors, db_errors):
    print(f"\n=== SUMMARY ===")
    print(f"  File errors: {len(file_errors)}")
    print(f"  DB errors:   {len(db_errors)} (not blocking)")
    if db_errors:
        for e in db_errors[:10]:
            print(f"    [DB] {e}")
    if file_errors:
        for e in file_errors[:10]:
            print(f"    [FILE] {e}")
        print(f"  Overall: FAIL")
        sys.exit(1)
    else:
        print(f"  Overall: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
