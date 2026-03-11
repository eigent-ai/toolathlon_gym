"""Generate groundtruth Excel file for wc-sales-tax-summary task."""
import os
import psycopg2
from openpyxl import Workbook

TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(TASK_ROOT, "groundtruth_workspace")

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # By state
    cur.execute("""
        SELECT billing->>'state' as state,
               COUNT(*) as order_count,
               ROUND(SUM(total::numeric), 2) as total_sales,
               ROUND(SUM(total_tax::numeric), 2) as total_tax
        FROM wc.orders
        WHERE status IN ('completed', 'processing')
        AND billing->>'state' IS NOT NULL
        AND billing->>'state' != ''
        GROUP BY billing->>'state'
        ORDER BY SUM(total_tax::numeric) DESC
    """)
    state_rows = cur.fetchall()

    # Overall
    cur.execute("""
        SELECT COUNT(*) as total_orders,
               ROUND(SUM(total::numeric), 2) as total_sales,
               ROUND(SUM(total_tax::numeric), 2) as total_tax
        FROM wc.orders
        WHERE status IN ('completed', 'processing')
    """)
    overall = cur.fetchone()
    total_orders = int(overall[0])
    total_sales = float(overall[1])
    total_tax = float(overall[2])
    effective_rate = round(total_tax / total_sales * 100, 2) if total_sales > 0 else 0.0

    cur.close()
    conn.close()

    wb = Workbook()

    # Sheet 1: By State
    ws1 = wb.active
    ws1.title = "By State"
    ws1.append(["State", "Order Count", "Total Sales", "Total Tax"])
    for row in state_rows:
        ws1.append([row[0], int(row[1]), float(row[2]), float(row[3])])

    # Sheet 2: Overall
    ws2 = wb.create_sheet("Overall")
    ws2.append(["Metric", "Value"])
    ws2.append(["Total Orders", total_orders])
    ws2.append(["Total Sales", total_sales])
    ws2.append(["Total Tax", total_tax])
    ws2.append(["Effective Tax Rate", effective_rate])

    out_path = os.path.join(OUTPUT_DIR, "Tax_Summary_Report.xlsx")
    wb.save(out_path)
    print(f"Generated: {out_path}")
    print(f"  Total Orders: {total_orders}")
    print(f"  Total Sales: {total_sales}")
    print(f"  Total Tax: {total_tax}")
    print(f"  Effective Tax Rate: {effective_rate}%")
    print(f"  States: {len(state_rows)}")


if __name__ == "__main__":
    main()
