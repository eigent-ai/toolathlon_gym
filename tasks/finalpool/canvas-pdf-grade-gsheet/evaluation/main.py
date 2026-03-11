"""
Evaluation script for canvas-pdf-grade-gsheet task.

Checks:
1. Excel file (semester_grade_report.xlsx) - three sheets with correct data
2. Google Sheet in PostgreSQL - grade summary data
3. Emails sent to instructors - correct content

Usage:
    python -m evaluation.main \
        --agent_workspace /path/to/workspace \
        --groundtruth_workspace /path/to/groundtruth \
        --res_log_file /path/to/result.json \
        --launch_time "2026-03-06 10:00:00"
"""

import argparse
import json
import sys

from .check_local import check_local  # uses iter_rows, str_match, lower() for content validation
from .check_gsheet import check_gsheet
from .check_email import check_email


def run_evaluation(agent_workspace, groundtruth_workspace, launch_time, res_log_file):
    """Run all evaluation checks."""

    total_passed = 0
    total_failed = 0
    all_errors = []

    # 1. Check Excel
    print("\n=== Checking Excel Output ===")
    p, f, errs = check_local(agent_workspace, groundtruth_workspace)
    total_passed += p
    total_failed += f
    all_errors.extend(errs)
    print(f"  Excel: {p} passed, {f} failed")
    for e in errs:
        print(f"    [FAIL] {e[:200]}")

    # 2. Check Google Sheet
    print("\n=== Checking Google Sheet ===")
    p, f, errs = check_gsheet()
    total_passed += p
    total_failed += f
    all_errors.extend(errs)
    print(f"  Google Sheet: {p} passed, {f} failed")
    for e in errs:
        print(f"    [FAIL] {e[:200]}")

    # 3. Check Emails
    print("\n=== Checking Emails ===")
    p, f, errs = check_email()
    total_passed += p
    total_failed += f
    all_errors.extend(errs)
    print(f"  Emails: {p} passed, {f} failed")
    for e in errs:
        print(f"    [FAIL] {e[:200]}")

    # Overall
    total = total_passed + total_failed
    all_passed = total_failed == 0 and total_passed > 0

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Overall: {'PASS' if all_passed else 'FAIL'}")

    if res_log_file:
        result = {
            "passed": total_passed,
            "failed": total_failed,
            "total": total,
            "success": all_passed,
            "errors": all_errors[:20],
        }
        with open(res_log_file, "w") as fh:
            json.dump(result, fh, indent=2)

    return all_passed, f"Passed: {total_passed}, Failed: {total_failed}"


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
