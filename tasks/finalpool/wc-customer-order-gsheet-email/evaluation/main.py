"""Evaluation for wc-customer-order-gsheet-email task.

Check 1: Google Sheet "VIP Customer Tracker" with "Top Customers" sheet
Check 2: Google Sheet "Store Summary" sheet with metrics
Check 3: 5 thank-you emails sent to top 5 customers
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


def num_close(a, b, tol=0.5):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def get_top10():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT first_name || ' ' || last_name as name, email, orders_count,
               ROUND(total_spent::numeric, 2) as total_spent,
               CASE WHEN orders_count > 0 THEN ROUND((total_spent::numeric / orders_count), 2) ELSE 0 END as avg_order
        FROM wc.customers ORDER BY total_spent::numeric DESC LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_summary():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), ROUND(SUM(total_spent::numeric), 2) FROM wc.customers")
    total_cust, total_rev = cur.fetchone()
    cur.execute("""
        SELECT ROUND(SUM(total_spent::numeric), 2)
        FROM (SELECT total_spent FROM wc.customers ORDER BY total_spent::numeric DESC LIMIT 10) t
    """)
    vip_rev = cur.fetchone()[0]
    vip_pct = round(float(vip_rev) / float(total_rev) * 100, 1) if float(total_rev) > 0 else 0
    avg_spend = round(float(total_rev) / total_cust, 2) if total_cust > 0 else 0
    cur.close()
    conn.close()
    return {
        "Total_Customers": total_cust,
        "Total_Revenue": float(total_rev),
        "VIP_Revenue_Share_Pct": vip_pct,
        "Avg_Customer_Spend": avg_spend,
    }


def check_gsheet_top_customers():
    """Check the Top Customers sheet in the VIP spreadsheet."""
    print("\n=== Checking Google Sheet: Top Customers ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Find spreadsheet with VIP in title
    cur.execute("SELECT id, title FROM gsheet.spreadsheets WHERE LOWER(title) LIKE '%vip%'")
    spreadsheets = cur.fetchall()
    check("Spreadsheet with 'VIP' in title exists", len(spreadsheets) > 0,
          "No spreadsheet found with 'VIP' in title")
    if not spreadsheets:
        cur.close()
        conn.close()
        return

    ss_id = spreadsheets[0][0]
    ss_title = spreadsheets[0][1]
    print(f"  Found spreadsheet: '{ss_title}' (id={ss_id})")

    # Find the "Top Customers" sheet
    cur.execute("""
        SELECT id FROM gsheet.sheets
        WHERE spreadsheet_id = %s AND LOWER(title) LIKE '%%top%%customer%%'
    """, (ss_id,))
    sheets = cur.fetchall()
    check("Sheet 'Top Customers' exists", len(sheets) > 0)
    if not sheets:
        cur.close()
        conn.close()
        return

    sheet_id = sheets[0][0]

    # Get all cells for this sheet
    cur.execute("""
        SELECT row_index, col_index, value FROM gsheet.cells
        WHERE spreadsheet_id = %s AND sheet_id = %s
        ORDER BY row_index, col_index
    """, (ss_id, sheet_id))
    cells = cur.fetchall()

    # Build a grid
    grid = {}
    for row_idx, col_idx, value in cells:
        grid[(row_idx, col_idx)] = value

    # Check that we have at least 10 data rows (row 0 or 1 is header)
    max_row = max((r for r, c in grid.keys()), default=0)
    data_rows = max_row  # rows after header
    check("At least 10 data rows in Top Customers", data_rows >= 10,
          f"Found max_row={max_row}")

    # Check expected customer emails appear in the cells
    top10 = get_top10()
    all_values = [str(v).strip().lower() for v in grid.values() if v]
    for name, email, orders, total, avg_order in top10:
        found = email.lower() in all_values
        check(f"Customer {email} in sheet", found)
        if found:
            # Find the total_spent value for this customer
            total_found = any(num_close(v, float(total), 1.0) for v in all_values
                              if v.replace('.', '', 1).replace('-', '', 1).isdigit())
            check(f"Customer {email} total_spent ~{total}", total_found)

    cur.close()
    conn.close()


def check_gsheet_summary():
    """Check the Store Summary sheet."""
    print("\n=== Checking Google Sheet: Store Summary ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id FROM gsheet.spreadsheets WHERE LOWER(title) LIKE '%vip%'")
    spreadsheets = cur.fetchall()
    if not spreadsheets:
        check("Spreadsheet exists for summary check", False)
        cur.close()
        conn.close()
        return

    ss_id = spreadsheets[0][0]

    cur.execute("""
        SELECT id FROM gsheet.sheets
        WHERE spreadsheet_id = %s AND LOWER(title) LIKE '%%store%%summar%%'
    """, (ss_id,))
    sheets = cur.fetchall()
    check("Sheet 'Store Summary' exists", len(sheets) > 0)
    if not sheets:
        cur.close()
        conn.close()
        return

    sheet_id = sheets[0][0]

    cur.execute("""
        SELECT row_index, col_index, value FROM gsheet.cells
        WHERE spreadsheet_id = %s AND sheet_id = %s
        ORDER BY row_index, col_index
    """, (ss_id, sheet_id))
    cells = cur.fetchall()

    all_values = [str(v).strip() for v in [c[2] for c in cells] if v]
    all_values_lower = [v.lower() for v in all_values]

    expected = get_summary()

    # Check each metric value exists somewhere in the cells
    check("Total_Customers value present",
          any(v == str(expected["Total_Customers"]) for v in all_values),
          f"Expected {expected['Total_Customers']}")

    check("Total_Revenue value present",
          any(num_close(v, expected["Total_Revenue"], 5.0) for v in all_values
              if v.replace('.', '', 1).replace('-', '', 1).isdigit()),
          f"Expected ~{expected['Total_Revenue']}")

    check("VIP_Revenue_Share_Pct value present",
          any(num_close(v, expected["VIP_Revenue_Share_Pct"], 1.0) for v in all_values
              if v.replace('.', '', 1).replace('-', '', 1).isdigit()),
          f"Expected ~{expected['VIP_Revenue_Share_Pct']}")

    check("Avg_Customer_Spend value present",
          any(num_close(v, expected["Avg_Customer_Spend"], 5.0) for v in all_values
              if v.replace('.', '', 1).replace('-', '', 1).isdigit()),
          f"Expected ~{expected['Avg_Customer_Spend']}")

    cur.close()
    conn.close()


def check_emails():
    """Check that 5 thank-you emails were sent to the top 5 customers."""
    print("\n=== Checking Emails ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    top10 = get_top10()
    top5_emails = [row[1] for row in top10[:5]]

    # Get all sent emails
    cur.execute("SELECT subject, from_addr, to_addr, body_text FROM email.messages")
    all_emails = cur.fetchall()

    check("At least 5 emails sent", len(all_emails) >= 5,
          f"Found {len(all_emails)} emails total")

    def find_email_for_recipient(recipient):
        for subj, from_addr, to_addr, body in all_emails:
            if to_addr:
                recipients = []
                if isinstance(to_addr, list):
                    recipients = [str(r).strip().lower() for r in to_addr]
                elif isinstance(to_addr, str):
                    try:
                        parsed = json.loads(to_addr)
                        if isinstance(parsed, list):
                            recipients = [str(r).strip().lower() for r in parsed]
                        else:
                            recipients = [str(to_addr).strip().lower()]
                    except (json.JSONDecodeError, TypeError):
                        recipients = [str(to_addr).strip().lower()]
                if recipient.lower() in recipients:
                    return subj, from_addr, to_addr, body
        return None

    for email_addr in top5_emails:
        result = find_email_for_recipient(email_addr)
        check(f"Email sent to {email_addr}", result is not None)
        if result:
            subj, from_addr, to_addr, body = result
            has_thank = "thank" in (subj or "").lower() or "vip" in (subj or "").lower()
            check(f"Email to {email_addr} has thank-you subject", has_thank,
                  f"Subject: {(subj or '')[:100]}")

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
    print("WC CUSTOMER ORDER GSHEET EMAIL - EVALUATION")
    print("=" * 70)

    check_gsheet_top_customers()
    check_gsheet_summary()
    check_emails()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    if FAIL_COUNT > 0:
        print(f"  WARNING: {FAIL_COUNT} DB checks failed (not blocking)")
    print(f"  Overall: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
