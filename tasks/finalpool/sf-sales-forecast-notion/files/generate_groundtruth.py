"""Generate groundtruth Excel file for sf-sales-forecast-notion task."""
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

    # Monthly revenue
    cur.execute("""
        SELECT TO_CHAR("ORDER_DATE"::timestamp, 'YYYY-MM') as month,
               COUNT(*) as orders,
               ROUND(SUM("TOTAL_AMOUNT")::numeric, 2) as revenue
        FROM sf_data."SALES_DW__PUBLIC__ORDERS"
        GROUP BY TO_CHAR("ORDER_DATE"::timestamp, 'YYYY-MM')
        ORDER BY month
    """)
    monthly_rows = cur.fetchall()

    # Exclude partial months: current month (2026-03) has far fewer orders
    # Average is ~800+ orders/month; exclude any month with < 500 orders
    complete_months = [(m, int(o), float(r)) for m, o, r in monthly_rows if int(o) >= 500]

    # Regional performance
    cur.execute("""
        SELECT c."REGION",
               COUNT(o."ORDER_ID") as order_count,
               ROUND(SUM(o."TOTAL_AMOUNT")::numeric, 2) as total_revenue
        FROM sf_data."SALES_DW__PUBLIC__ORDERS" o
        JOIN sf_data."SALES_DW__PUBLIC__CUSTOMERS" c ON o."CUSTOMER_ID" = c."CUSTOMER_ID"
        GROUP BY c."REGION"
        ORDER BY c."REGION"
    """)
    region_rows = cur.fetchall()

    cur.close()
    conn.close()

    wb = Workbook()

    # Sheet 1: Monthly Revenue
    ws1 = wb.active
    ws1.title = "Monthly Revenue"
    ws1.append(["Month", "Order Count", "Revenue"])
    for month, orders, revenue in complete_months:
        ws1.append([month, orders, revenue])

    # Sheet 2: Regional Performance
    ws2 = wb.create_sheet("Regional Performance")
    ws2.append(["Region", "Order Count", "Revenue"])
    for region, orders, revenue in region_rows:
        ws2.append([region, int(orders), float(revenue)])

    out_path = os.path.join(OUTPUT_DIR, "Sales_Dashboard_Backup.xlsx")
    wb.save(out_path)
    print(f"Generated: {out_path}")
    print(f"  Complete months: {len(complete_months)}")
    print(f"  Regions: {len(region_rows)}")
    for m, o, r in complete_months:
        print(f"    {m}: {o} orders, ${r}")
    for region, orders, revenue in region_rows:
        print(f"    {region}: {int(orders)} orders, ${float(revenue)}")


if __name__ == "__main__":
    main()
