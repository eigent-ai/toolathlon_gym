"""
Data cleaning script for sales and inventory API response data.

Reads sales_api_response.json and inventory_api_response.json,
removes duplicates, normalizes product names to title case,
and outputs cleaned_sales.json and cleaned_inventory.json.
"""

import json
import os


def main():
    workspace = os.path.dirname(os.path.abspath(__file__))

    # Load raw data
    with open(os.path.join(workspace, "sales_api_response.json")) as f:
        sales_raw = json.load(f)
    with open(os.path.join(workspace, "inventory_api_response.json")) as f:
        inv_raw = json.load(f)

    # Clean sales: deduplicate by order_id, normalize product_name
    seen_oids = set()
    cleaned_sales = []
    for rec in sales_raw.get("data", []):
        oid = rec.get("order_id", "")
        if oid and oid not in seen_oids:
            seen_oids.add(oid)
            rec["product_name"] = rec.get("product_name", "").strip().title()
            cleaned_sales.append(rec)

    # Clean inventory: deduplicate by product_id, normalize product_name
    seen_pids = set()
    cleaned_inv = []
    for rec in inv_raw.get("data", []):
        pid = rec.get("product_id", "")
        if pid and pid not in seen_pids:
            seen_pids.add(pid)
            rec["product_name"] = rec.get("product_name", "").strip().title()
            cleaned_inv.append(rec)

    # Write cleaned data
    with open(os.path.join(workspace, "cleaned_sales.json"), "w") as f:
        json.dump({"sales": cleaned_sales, "count": len(cleaned_sales)}, f, indent=2)

    with open(os.path.join(workspace, "cleaned_inventory.json"), "w") as f:
        json.dump({"inventory": cleaned_inv, "count": len(cleaned_inv)}, f, indent=2)

    print(f"Cleaned {len(cleaned_sales)} sales records")
    print(f"Cleaned {len(cleaned_inv)} inventory records")


if __name__ == "__main__":
    main()
