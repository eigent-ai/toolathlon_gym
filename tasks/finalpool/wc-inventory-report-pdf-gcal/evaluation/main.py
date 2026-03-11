"""
Evaluation for wc-inventory-report-pdf-gcal task.

Checks:
1. PDF file Inventory_Audit.pdf exists and contains expected data
2. Google Calendar event created (non-blocking)
"""

import argparse
import json
import os
import sys

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

# Known out-of-stock product IDs
OOS_IDS = [20, 39, 45, 71, 79]
# Known low-stock product IDs (qty 1-5)
LOW_IDS = [5, 7, 15, 19, 21, 22, 27, 28, 30, 31, 32, 50, 52, 53, 54, 61, 63, 70, 77, 82]


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def check_pdf(agent_workspace):
    """Check the PDF file exists and has key content."""
    print("\n=== Checking Inventory_Audit.pdf ===")

    pdf_path = os.path.join(agent_workspace, "Inventory_Audit.pdf")
    if not os.path.isfile(pdf_path):
        record("PDF file exists", False, f"Not found: {pdf_path}")
        return False
    record("PDF file exists", True)

    # Check file size is reasonable (at least 1KB)
    size = os.path.getsize(pdf_path)
    record("PDF file size reasonable", size > 1024, f"Size: {size} bytes")

    # Try to extract text
    try:
        import PyPDF2
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
    except ImportError:
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as p:
                text = ""
                for page in p.pages:
                    text += page.extract_text() or ""
        except ImportError:
            print("  [WARN] No PDF reader available (PyPDF2 or pdfplumber). Checking file existence only.")
            return True

    text_lower = text.lower()

    # Check title
    record("PDF contains title", "inventory" in text_lower and "audit" in text_lower,
           "Expected 'Inventory Audit' in PDF")

    # Check summary section
    record("PDF contains total products count",
           "82" in text or "total products" in text_lower,
           "Expected total products count")

    record("PDF mentions out of stock",
           "out of stock" in text_lower,
           "Expected 'out of stock' text")

    # Check some product IDs appear
    found_oos = 0
    for pid in OOS_IDS:
        if str(pid) in text:
            found_oos += 1
    record("PDF lists out-of-stock product IDs",
           found_oos >= 3, f"Found {found_oos}/5 OOS product IDs")

    found_low = 0
    for pid in LOW_IDS[:10]:
        if str(pid) in text:
            found_low += 1
    record("PDF lists low-stock product IDs",
           found_low >= 5, f"Found {found_low}/10 sampled low-stock product IDs")

    return True


def check_gcal():
    """Check Google Calendar event - NON-BLOCKING."""
    print("\n=== Checking Google Calendar (non-blocking) ===")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            SELECT summary, description, start_datetime
            FROM gcal.events
            ORDER BY summary
        """)
        events = cur.fetchall()
        cur.close()
        conn.close()

        if len(events) == 0:
            print("  [WARN] No calendar events found (non-blocking)")
            return

        restock_events = [e for e in events if "restock" in (e[0] or "").lower()]
        if restock_events:
            print(f"  [INFO] Found {len(restock_events)} restock-related calendar event(s)")
            for ev in restock_events:
                desc = (ev[1] or "")[:100]
                print(f"    Title: {ev[0]}, Date: {ev[2]}, Desc: {desc}")

                # Check description mentions counts
                if "5" in desc or "out of stock" in desc.lower():
                    print("  [INFO] Event description mentions stock counts")
        else:
            print("  [WARN] No restock-related calendar events found (non-blocking)")

    except Exception as e:
        print(f"  [WARN] Calendar check error (non-blocking): {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    pdf_ok = check_pdf(args.agent_workspace)
    check_gcal()  # Non-blocking

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")

    overall = FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")

    if args.res_log_file:
        result = {"passed": PASS_COUNT, "failed": FAIL_COUNT, "success": overall}
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
