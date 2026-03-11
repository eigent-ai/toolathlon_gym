"""Evaluation for terminal-sf-canvas-word-gform-email.
Checks:
1. Training_Effectiveness_Report.docx content
2. Google Form "Training Feedback Survey" with 5 questions
3. Emails to hr_director and training_team
4. Script files exist (training_matches.py, effectiveness_analysis.py, survey_analysis.py)
5. JSON output files exist
"""
import argparse
import json
import os
import sys

import psycopg2
from docx import Document

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432,
          dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
          user="eigent", password="camel")

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name}: {str(detail)[:200]}")


def num_close(a, b, tol=2.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def get_expected_values():
    """Query DB for expected values."""
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Course avg scores
    cur.execute("""
        SELECT a.course_id, ROUND(AVG(s.score)::numeric, 2)
        FROM canvas.assignments a
        JOIN canvas.submissions s ON s.assignment_id = a.id
        WHERE a.course_id IN (9, 10) AND s.score IS NOT NULL
        GROUP BY a.course_id
    """)
    course_avgs = {int(r[0]): float(r[1]) for r in cur.fetchall()}

    # Enrollment counts
    cur.execute("""
        SELECT course_id, COUNT(DISTINCT user_id)
        FROM canvas.enrollments
        WHERE course_id IN (9, 10) AND type='StudentEnrollment'
        GROUP BY course_id
    """)
    enrollments = {int(r[0]): r[1] for r in cur.fetchall()}

    # SF dept ratings
    cur.execute("""
        SELECT "DEPARTMENT", ROUND(AVG("PERFORMANCE_RATING")::numeric, 2)
        FROM sf_data."HR_ANALYTICS__PUBLIC__EMPLOYEES"
        WHERE "DEPARTMENT" IN ('Engineering', 'R&D')
        GROUP BY "DEPARTMENT"
    """)
    dept_ratings = {r[0]: float(r[1]) for r in cur.fetchall()}

    cur.close()
    conn.close()

    c9_avg = course_avgs.get(9, 69.59)
    c10_avg = course_avgs.get(10, 71.53)
    eng_rating = dept_ratings.get("Engineering", 3.21)
    rnd_rating = dept_ratings.get("R&D", 3.20)
    eng_impr = eng_rating - 3.00
    rnd_impr = rnd_rating - 2.95
    avg_impr = (eng_impr + rnd_impr) / 2
    overall_avg_score = (c9_avg + c10_avg) / 2

    return {
        "c9_avg": c9_avg, "c10_avg": c10_avg,
        "eng_enrolled": enrollments.get(9, 1938),
        "rnd_enrolled": enrollments.get(10, 1803),
        "eng_rating": eng_rating, "rnd_rating": rnd_rating,
        "eng_impr": eng_impr, "rnd_impr": rnd_impr,
        "avg_impr": avg_impr,
        "overall_avg_score": overall_avg_score,
    }


def check_word(workspace):
    """Check Training_Effectiveness_Report.docx."""
    print("\n=== Check 1: Word Document ===")
    path = os.path.join(workspace, "Training_Effectiveness_Report.docx")
    if not os.path.exists(path):
        check("Word document exists", False, f"Not found: {path}")
        return
    check("Word document exists", True)

    doc = Document(path)
    full_text = " ".join(p.text for p in doc.paragraphs).lower()

    check("Has Executive Summary section",
          "executive summary" in full_text)
    check("Has Methodology section",
          "methodology" in full_text)
    check("Has Performance Impact section",
          "performance impact" in full_text or "impact analysis" in full_text)
    check("Has Survey Findings section",
          "survey findings" in full_text or "survey" in full_text)
    check("Has ROI section",
          "roi" in full_text or "return on investment" in full_text)
    check("Has Recommendations section",
          "recommendation" in full_text)
    check("Mentions Engineering department",
          "engineering" in full_text)
    check("Mentions R&D department",
          "r&d" in full_text or "r & d" in full_text)
    check("Mentions Data-Driven Design",
          "data-driven design" in full_text or "data driven design" in full_text)
    check("Has substantial content", len(full_text) > 500, f"Length: {len(full_text)}")

    ev = get_expected_values()

    # Check that key numbers appear in text
    check("Mentions course 9 avg score",
          str(round(ev["c9_avg"], 1)) in full_text or str(round(ev["c9_avg"], 2)) in full_text
          or str(int(round(ev["c9_avg"]))) in full_text,
          f"Expected ~{ev['c9_avg']:.2f}")
    check("Mentions course 10 avg score",
          str(round(ev["c10_avg"], 1)) in full_text or str(round(ev["c10_avg"], 2)) in full_text
          or str(int(round(ev["c10_avg"]))) in full_text,
          f"Expected ~{ev['c10_avg']:.2f}")

    # Check conditional recommendation
    if ev["avg_impr"] < 0.15:
        check("Recommends restructuring (improvement < 0.15)",
              "restructur" in full_text,
              f"Avg improvement: {ev['avg_impr']:.2f}")
    else:
        check("Recommends expanding (improvement >= 0.15)",
              "expand" in full_text,
              f"Avg improvement: {ev['avg_impr']:.2f}")


def check_gform():
    """Check Google Form creation."""
    print("\n=== Check 2: Google Form ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM gform.forms")
    forms = cur.fetchall()

    form_id = None
    for fid, title in forms:
        t = (title or "").lower()
        if "training" in t and ("feedback" in t or "survey" in t):
            form_id = fid
            break

    check("Training Feedback Survey form exists", form_id is not None,
          f"Forms: {[f[1] for f in forms]}")

    if form_id:
        cur.execute("SELECT title, question_type FROM gform.questions WHERE form_id = %s ORDER BY position",
                    (form_id,))
        questions = cur.fetchall()
        check("Form has exactly 5 questions", len(questions) == 5,
              f"Found {len(questions)}")

        if len(questions) >= 5:
            q_titles = [q[0].lower() for q in questions]
            check("Q1 about satisfaction",
                  any("satisfaction" in t or "rating" in t for t in q_titles[:2]),
                  f"Q titles: {q_titles}")
            check("Q4 about recommendation",
                  any("recommend" in t for t in q_titles),
                  f"Q titles: {q_titles}")
            check("Q5 about format",
                  any("format" in t for t in q_titles),
                  f"Q titles: {q_titles}")

        # Check responses exist
        cur.execute("SELECT COUNT(*) FROM gform.responses WHERE form_id = %s", (form_id,))
        resp_count = cur.fetchone()[0]
        check("Form has responses", resp_count >= 15,
              f"Found {resp_count} responses")

    cur.close()
    conn.close()


def check_emails():
    """Check emails to hr_director and training_team."""
    print("\n=== Check 3: Emails ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT subject, from_addr, to_addr, body_text FROM email.messages")
    all_emails = cur.fetchall()

    # Check email to hr_director
    hr_email = None
    training_email = None
    for subj, from_addr, to_addr, body in all_emails:
        to_str = str(to_addr).lower() if to_addr else ""
        if "hr_director" in to_str:
            hr_email = (subj, from_addr, to_addr, body)
        if "training_team" in to_str:
            training_email = (subj, from_addr, to_addr, body)

    check("Email sent to hr_director@company.com", hr_email is not None,
          f"Total emails: {len(all_emails)}")
    if hr_email:
        subj, from_addr, to_addr, body = hr_email
        check("HR email subject mentions training/effectiveness",
              "training" in (subj or "").lower() or "effectiveness" in (subj or "").lower(),
              f"Subject: {subj}")
        check("HR email from training_analytics@company.com",
              "training_analytics" in (from_addr or "").lower(),
              f"From: {from_addr}")
        body_lower = (body or "").lower()
        check("HR email mentions performance",
              "performance" in body_lower or "rating" in body_lower,
              "Expected performance/rating in body")
        check("HR email mentions improvement or baseline",
              "improvement" in body_lower or "baseline" in body_lower or "improv" in body_lower,
              "Expected improvement mention")

    check("Email sent to training_team@company.com", training_email is not None,
          f"Total emails: {len(all_emails)}")
    if training_email:
        subj, from_addr, to_addr, body = training_email
        check("Training email subject mentions survey/feedback",
              "survey" in (subj or "").lower() or "feedback" in (subj or "").lower(),
              f"Subject: {subj}")
        body_lower = (body or "").lower()
        check("Training email mentions satisfaction",
              "satisfaction" in body_lower or "rating" in body_lower,
              "Expected satisfaction mention")
        check("Training email mentions format or recommend",
              "format" in body_lower or "recommend" in body_lower,
              "Expected format/recommend mention")

    cur.close()
    conn.close()


def check_scripts(workspace):
    """Check that required scripts exist."""
    print("\n=== Check 4: Scripts ===")
    for script in ["training_matches.py", "effectiveness_analysis.py", "survey_analysis.py"]:
        path = os.path.join(workspace, script)
        check(f"{script} exists", os.path.exists(path), f"Not found: {path}")


def check_json_outputs(workspace):
    """Check JSON output files."""
    print("\n=== Check 5: JSON Outputs ===")
    for jfile in ["training_matches.json", "effectiveness_analysis.json", "survey_results.json"]:
        path = os.path.join(workspace, jfile)
        if not os.path.exists(path):
            check(f"{jfile} exists", False, f"Not found: {path}")
            continue
        check(f"{jfile} exists", True)
        try:
            with open(path) as f:
                data = json.load(f)
            check(f"{jfile} is valid JSON", True)
            check(f"{jfile} is non-empty", len(data) > 0, "Empty JSON")
        except json.JSONDecodeError as e:
            check(f"{jfile} is valid JSON", False, str(e))

    # Check effectiveness_analysis.json content
    ea_path = os.path.join(workspace, "effectiveness_analysis.json")
    if os.path.exists(ea_path):
        try:
            with open(ea_path) as f:
                ea = json.load(f)
            ea_str = json.dumps(ea).lower()
            check("effectiveness_analysis mentions Engineering or R&D",
                  "engineering" in ea_str or "r&d" in ea_str or "r_d" in ea_str,
                  "Expected department names")
        except Exception:
            pass


def check_reverse_validation():
    """Verify noise data not misused."""
    print("\n=== Reverse Validation ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # No emails to noise recipients
    cur.execute("""
        SELECT to_addr FROM email.messages
        WHERE from_addr ILIKE '%%training_analytics%%'
    """)
    sent = cur.fetchall()
    noise_addrs = ["all@company.com", "managers@company.com", "leadership@company.com"]
    for row in sent:
        to_str = str(row[0]).lower()
        for noise in noise_addrs:
            if noise in to_str:
                check("No emails sent to noise recipients", False, f"Sent to {noise}")
                cur.close()
                conn.close()
                return
    check("No emails sent to noise recipients", True)

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    print("=" * 70)
    print("TERMINAL-SF-CANVAS-WORD-GFORM-EMAIL - EVALUATION")
    print("=" * 70)

    check_word(args.agent_workspace)
    check_gform()
    check_emails()
    check_scripts(args.agent_workspace)
    check_json_outputs(args.agent_workspace)
    check_reverse_validation()

    total = PASS_COUNT + FAIL_COUNT
    accuracy = PASS_COUNT / total * 100 if total > 0 else 0
    print(f"\nOverall: {PASS_COUNT}/{total} ({accuracy:.1f}%)")

    result = {"total_passed": PASS_COUNT, "total_checks": total, "accuracy": accuracy}
    if args.res_log_file:
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    sys.exit(0 if accuracy >= 70 else 1)


if __name__ == "__main__":
    main()
