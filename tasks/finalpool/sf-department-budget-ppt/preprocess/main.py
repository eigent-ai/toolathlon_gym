"""
Preprocess for sf-department-budget-ppt task.

Snowflake is read-only. PDF is pre-generated in initial_workspace.
No writable schemas used - nothing to clean.
"""

import argparse


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()
    print("[preprocess] No preprocess needed for this task.")


if __name__ == "__main__":
    main()
