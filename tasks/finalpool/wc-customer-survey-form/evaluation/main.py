"""Evaluation for wc-customer-survey-form."""
import argparse
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

# Expected customers with completed orders (from WC data)
EXPECTED_EMAILS = {
    "emily.johnson@x.dummyjson.com",
    "michael.williams@x.dummyjson.com",
    "sophia.brown@x.dummyjson.com",
    "olivia.wilson@x.dummyjson.com",
    "ava.taylor@x.dummyjson.com",
    "ethan.martinez@x.dummyjson.com",
    "liam.garcia@x.dummyjson.com",
    "mia.rodriguez@x.dummyjson.com",
    "noah.hernandez@x.dummyjson.com",
    "charlotte.lopez@x.dummyjson.com",
    "william.gonzalez@x.dummyjson.com",
    "evelyn.sanchez@x.dummyjson.com",
    "abigail.rivera@x.dummyjson.com",
    "chloe.morales@x.dummyjson.com",
    "mateo.nguyen@x.dummyjson.com",
    "evelyn.gonzalez@x.dummyjson.com",
    "daniel.cook@x.dummyjson.com",
    "lily.lee@x.dummyjson.com",
    "henry.hill@x.dummyjson.com",
    "addison.wright@x.dummyjson.com",
    "gabriel.adams@x.dummyjson.com",
    "natalie.harris@x.dummyjson.com",
    "carter.baker@x.dummyjson.com",
    "harper.turner@x.dummyjson.com",
    "mason.parker@x.dummyjson.com",
    "lucas.gray@x.dummyjson.com",
    "ella.adams@x.dummyjson.com",
    "evan.reed@x.dummyjson.com",
    "avery.carter@x.dummyjson.com",
    "benjamin.foster@x.dummyjson.com",
    "scarlett.wright@x.dummyjson.com",
    "lincoln.kelly@x.dummyjson.com",
    "hannah.robinson@x.dummyjson.com",
    "nicholas.bailey@x.dummyjson.com",
    "luna.russell@x.dummyjson.com",
    "stella.hughes@x.dummyjson.com",
}

EXPECTED_QUESTIONS = [
    "how would you rate your overall shopping experience",
    "how satisfied are you with the product quality",
    "how likely are you to recommend our store",
    "what did you like most about your purchase",
    "any suggestions for improvement",
]


def str_contains(haystack, needle):
    if haystack is None:
        return False
    return needle.lower() in str(haystack).lower()


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

    # ---- Check Google Form ----
    print("  Checking Google Form...")
    cur.execute("SELECT id, title, description FROM gform.forms")
    forms = cur.fetchall()
    if len(forms) == 0:
        all_errors.append("No Google Form created")
    else:
        form = forms[0]
        form_id = form[0]
        if not str_contains(form[1], "customer satisfaction"):
            all_errors.append(f"Form title mismatch: {form[1]}")
        if not str_contains(form[2], "value your feedback"):
            all_errors.append(f"Form description mismatch: {form[2]}")

        # Check questions
        cur.execute("SELECT title, question_type, required, position FROM gform.questions WHERE form_id=%s ORDER BY position", (form_id,))
        questions = cur.fetchall()
        if len(questions) < 5:
            all_errors.append(f"Expected 5 questions, found {len(questions)}")
        else:
            for i, expected in enumerate(EXPECTED_QUESTIONS):
                if i < len(questions):
                    q = questions[i]
                    if not str_contains(q[0], expected.split()[-2]):
                        all_errors.append(f"Question {i+1} title mismatch: '{q[0]}' does not match expected")
            # Check last question is not required
            if len(questions) >= 5:
                last_q = questions[4]
                if last_q[2] is True:
                    all_errors.append("Last question (suggestions) should not be required")
        if not all_errors:
            print("    PASS")

    # ---- Check Emails ----
    print("  Checking emails sent...")
    cur.execute("SELECT to_addr, subject, body_text FROM email.messages")
    messages = cur.fetchall()
    sent_to = set()
    survey_messages = []
    for msg in messages:
        to_addr = msg[0]
        if to_addr:
            to_str = str(to_addr).strip()
            # Handle JSON array, comma-separated, or plain email
            import re
            found_addrs = re.findall(r'[\w.+-]+@[\w.-]+', to_str.lower())
            for addr in found_addrs:
                sent_to.add(addr)
                if addr in EXPECTED_EMAILS:
                    survey_messages.append(msg)

    missing = EXPECTED_EMAILS - sent_to

    if len(missing) > 5:
        all_errors.append(f"Missing {len(missing)} expected email recipients (first 5: {list(missing)[:5]})")
    elif len(missing) > 0:
        all_errors.append(f"Missing {len(missing)} email recipients: {list(missing)}")

    # Check subject only on survey-related emails
    if survey_messages:
        subj = str(survey_messages[0][1] or "").lower()
        if "feedback" not in subj and "survey" not in subj and "satisfaction" not in subj:
            all_errors.append(f"Email subject should contain 'feedback'/'survey'/'satisfaction': {survey_messages[0][1]}")

    # Check email body mentions customer name
    has_personalized = False
    for msg in survey_messages:
        if msg[2] and "dear" in str(msg[2]).lower():
            has_personalized = True
            break
    if not has_personalized and len(survey_messages) > 0:
        all_errors.append("Emails don't appear to be personalized with customer name")

    if not any("email" in e.lower() for e in all_errors):
        print(f"    PASS ({len(sent_to)} emails sent)")

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
