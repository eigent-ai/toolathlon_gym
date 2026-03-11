"""
Preprocess for sf-sales-trend-word-pdf task.

Snowflake is read-only. No writable schemas used. Nothing to clear.
"""

import argparse


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    print("[preprocess] No writable schemas to clear for this task.")
    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
