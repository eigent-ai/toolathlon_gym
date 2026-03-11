"""
Preprocess script for canvas-course-feedback task.

Canvas is read-only, so no changes there.
This script clears Google Forms data (responses, questions, forms) to ensure
a clean environment for the agent to create a new feedback form.
"""

import os
import argparse
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def clear_gform(cur):
    """Clear all Google Forms data, respecting FK constraints."""
    print("[preprocess] Clearing Google Forms data...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    print("[preprocess] Cleared Google Forms data.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=True)
    parser.add_argument("--launch_time", required=False, help="Launch time")
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        clear_gform(cur)
        print("[preprocess] Done.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
