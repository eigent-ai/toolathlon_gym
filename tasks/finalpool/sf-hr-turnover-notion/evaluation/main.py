"""Evaluation for sf-hr-turnover-notion."""
import argparse
import os
import sys
import json
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

# Expected department data from Snowflake
EXPECTED_DEPTS = {
    "engineering": {"count": 7096, "avg": 58991.61, "min": 15360, "max": 695267, "range": 679907},
    "finance": {"count": 7148, "avg": 57878.19, "min": 15760, "max": 638897, "range": 623137},
    "hr": {"count": 7077, "avg": 58920.45, "min": 18307, "max": 692232, "range": 673925},
    "operations": {"count": 7120, "avg": 57808.74, "min": 17168, "max": 656505, "range": 639337},
    "r&d": {"count": 7083, "avg": 57905.93, "min": 15128, "max": 680490, "range": 665362},
    "sales": {"count": 7232, "avg": 58864.79, "min": 15885, "max": 652806, "range": 636921},
    "support": {"count": 7244, "avg": 58400.48, "min": 15916, "max": 608157, "range": 592241},
}


def num_close(a, b, tol=10.0):
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

    all_errors = []
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ---- Check Notion Page ----
    print("  Checking Notion page...")
    cur.execute("SELECT id, properties FROM notion.pages")
    pages = cur.fetchall()
    found_page = False
    for page in pages:
        props = page[1] if isinstance(page[1], dict) else json.loads(page[1]) if page[1] else {}
        title_text = ""
        if "title" in props:
            t = props["title"]
            if isinstance(t, dict) and "title" in t:
                for item in t["title"]:
                    if isinstance(item, dict) and "text" in item:
                        title_text += item["text"].get("content", "")
                    elif isinstance(item, dict) and "plain_text" in item:
                        title_text += item["plain_text"]
        if "hr" in title_text.lower() and "workforce" in title_text.lower():
            found_page = True
            break
    if not found_page:
        all_errors.append("Notion page with 'HR' and 'Workforce' in title not found")
    else:
        print("    Page found")

    # ---- Check Notion Database ----
    print("  Checking Notion database...")
    cur.execute("SELECT id, title, properties FROM notion.databases")
    databases = cur.fetchall()
    found_db = False
    db_id = None
    for db in databases:
        title_text = ""
        if db[1]:
            title_data = db[1] if isinstance(db[1], list) else json.loads(db[1]) if isinstance(db[1], str) else []
            for item in title_data:
                if isinstance(item, dict):
                    title_text += item.get("plain_text", "") or item.get("text", {}).get("content", "")
        if "department" in title_text.lower() and "metric" in title_text.lower():
            found_db = True
            db_id = db[0]
            break
    if not found_db:
        all_errors.append("Notion database 'Department Metrics' not found")
    else:
        print("    Database found")
        # Check database entries (pages with parent db)
        cur.execute("SELECT properties FROM notion.pages WHERE parent->>'database_id' = %s", (str(db_id),))
        db_pages = cur.fetchall()
        if len(db_pages) < 7:
            all_errors.append(f"Expected 7 department entries, found {len(db_pages)}")
        else:
            print(f"    {len(db_pages)} entries found")

    # ---- Check Email ----
    print("  Checking email sent...")
    cur.execute("SELECT to_addr, subject, body_text FROM email.messages")
    messages = cur.fetchall()
    found_email = False
    for msg in messages:
        to = str(msg[0]).lower() if msg[0] else ""
        subj = str(msg[1]).lower() if msg[1] else ""
        body = str(msg[2]).lower() if msg[2] else ""
        if "hr-director" in to and "workforce" in subj.lower():
            found_email = True
            if "50000" not in body and "50,000" not in body:
                all_errors.append("Email body should mention total of 50000 employees")
            if "engineering" not in body:
                all_errors.append("Email body should mention Engineering as highest avg salary dept")
            break
    if not found_email:
        all_errors.append("Email to hr-director with workforce analysis subject not found")
    else:
        print("    PASS")

    cur.close()
    conn.close()

    if all_errors:
        print(f"\n=== RESULT: FAIL ({len(all_errors)} errors) ===")
        for e in all_errors[:15]:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("\n=== RESULT: PASS ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
