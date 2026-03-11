"""Evaluation for canvas-enrollment-notion."""
import argparse
import json
import os
import sys

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")
PASS_COUNT = 0
FAIL_COUNT = 0


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1; print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1; print(f"  [FAIL] {name}: {str(detail)[:300]}")


def num_close(a, b, tol=1.0):
    try: return abs(float(a) - float(b)) <= tol
    except: return False


def get_expected():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""SELECT e.course_id, c.name, e.type, COUNT(*)
        FROM canvas.enrollments e JOIN canvas.courses c ON c.id=e.course_id
        GROUP BY e.course_id, c.name, e.type ORDER BY e.course_id""")
    courses = {}
    for cid, name, etype, cnt in cur.fetchall():
        if cid not in courses:
            courses[cid] = {"name": name, "students": 0, "teachers": 0, "tas": 0}
        if "Student" in etype: courses[cid]["students"] = cnt
        elif "Teacher" in etype: courses[cid]["teachers"] = cnt
        elif "Ta" in etype: courses[cid]["tas"] = cnt
    for c in courses.values():
        c["total"] = c["students"] + c["teachers"] + c["tas"]
    conn.close()
    return courses


def check_notion(expected):
    print("\n=== Checking Notion Database ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM notion.databases WHERE archived=false")
    dbs = cur.fetchall()
    record("Notion database created", len(dbs) >= 1, f"Found {len(dbs)}")

    target_db = None
    for did, title_json in dbs:
        title_str = json.dumps(title_json).lower() if title_json else ""
        if "enrollment" in title_str or "course" in title_str:
            target_db = did
            break
    if target_db is None and dbs:
        target_db = dbs[0][0]

    if target_db is None:
        conn.close()
        return

    record("Database titled with enrollment/course", target_db is not None)

    # Check pages (entries) in the database
    cur.execute("""SELECT id, properties FROM notion.pages
        WHERE parent->>'database_id' = %s AND archived=false""", (target_db,))
    pages = cur.fetchall()
    record("Database has course entries", len(pages) >= 20,
           f"Found {len(pages)}, expected ~{len(expected)}")

    # Check that some course names appear in page properties
    course_names_lower = {c["name"].lower() for c in expected.values()}
    found_names = 0
    for pid, props in pages:
        if props:
            props_str = json.dumps(props).lower()
            for cn in course_names_lower:
                # Check if any part of course name appears
                short_name = cn.split("(")[0].strip()
                if short_name in props_str:
                    found_names += 1
                    break

    record("Course names in entries", found_names >= 15,
           f"Found {found_names} matching names out of {len(pages)}")

    cur.close()
    conn.close()


def check_email(expected):
    print("\n=== Checking Email ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT subject, to_addr, body_text FROM email.messages")
    emails = cur.fetchall()
    record("At least 1 email sent", len(emails) >= 1, f"Found {len(emails)}")

    # Find the summary email
    summary_email = None
    for subj, to, body in emails:
        if subj and "enrollment" in subj.lower() and "summary" in subj.lower():
            summary_email = (subj, to, body)
            break
    if summary_email is None and emails:
        summary_email = emails[0]

    if summary_email:
        subj, to, body = summary_email
        record("Email subject matches", "enrollment" in (subj or "").lower(),
               f"Subject: {subj}")

        to_str = json.dumps(to).lower() if isinstance(to, list) else str(to).lower()
        record("Email to admin@university.example.com",
               "admin@university.example.com" in to_str, f"To: {to}")

        body_lower = (body or "").lower()
        total_courses = len(expected)
        record("Email mentions course count",
               str(total_courses) in (body or ""),
               f"Expected {total_courses} in body")

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", default=".")
    parser.add_argument("--groundtruth_workspace", default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()
    expected = get_expected()
    check_notion(expected)
    check_email(expected)
    print(f"\n=== SUMMARY: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    if args.res_log_file:
        with open(args.res_log_file, "w") as f:
            json.dump({"passed": PASS_COUNT, "failed": FAIL_COUNT, "success": FAIL_COUNT == 0}, f)
    sys.exit(0 if FAIL_COUNT == 0 else 1)

if __name__ == "__main__":
    main()
