"""
Evaluation script for canvas-exam-calendar-report task.

Checks:
1. Excel file (exam_review_plan.xlsx) - correct course data from Canvas
2. Google Calendar events - study sessions created correctly
3. Email sent with summary of all exams

Usage:
    python evaluation/main.py \
        --agent_workspace /path/to/workspace \
        --groundtruth_workspace /path/to/groundtruth \
        --res_log_file /path/to/result.json \
        --launch_time "2026-03-06 10:00:00"
"""

import argparse
import json
import sys

from .check_local import check_local  # uses iter_rows, str_match, lower() for content validation
from .check_gcal import check_gcal
from .check_email import check_email


PASS_COUNT = 0
FAIL_COUNT = 0


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def run_evaluation(agent_workspace, groundtruth_workspace, launch_time, res_log_file):
    """Run all evaluation checks."""

    # 1. Check Excel
    print("\n=== Checking Excel Output ===")
    local_pass, local_err = check_local(agent_workspace, groundtruth_workspace)
    record("Excel exam_review_plan.xlsx", local_pass, local_err or "")

    # 2. Check Google Calendar
    print("\n=== Checking Google Calendar ===")
    gcal_pass, gcal_err = check_gcal()
    record("Google Calendar study sessions", gcal_pass, gcal_err or "")

    # 3. Check Email
    print("\n=== Checking Email ===")
    email_pass, email_err = check_email()
    record("Summary email", email_pass, email_err or "")

    all_passed = local_pass and gcal_pass and email_pass

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    print(f"  Overall: {'PASS' if all_passed else 'FAIL'}")

    if res_log_file:
        result = {
            "passed": PASS_COUNT,
            "failed": FAIL_COUNT,
            "success": all_passed,
            "details": {
                "excel": local_pass,
                "gcal": gcal_pass,
                "email": email_pass,
            },
        }
        with open(res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    return all_passed, f"Passed: {PASS_COUNT}, Failed: {FAIL_COUNT}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    success, message = run_evaluation(
        args.agent_workspace,
        args.groundtruth_workspace,
        args.launch_time,
        args.res_log_file,
    )
    print(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
