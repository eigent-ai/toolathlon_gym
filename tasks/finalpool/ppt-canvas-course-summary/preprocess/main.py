#!/usr/bin/env python3
"""
Preprocess for ppt-canvas-course-summary task.
Clears gsheet schema data to ensure clean state.
Canvas is read-only so no injection needed.
"""

import os
import argparse
import psycopg2


def clear_gsheet_data():
    """Clear all gsheet schema data for a clean test environment."""
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym",
        user="eigent", password="camel"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Clear in dependency order
    tables = ["cells", "sheets", "permissions", "spreadsheets", "folders"]
    for table in tables:
        try:
            cur.execute(f"DELETE FROM gsheet.{table}")
            print(f"  Cleared gsheet.{table}")
        except Exception as e:
            print(f"  Warning clearing gsheet.{table}: {e}")
            conn.rollback()
            conn.autocommit = True

    conn.close()
    print("gsheet schema cleared")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=True)
    parser.add_argument("--launch_time", required=False, help="Launch time")
    args = parser.parse_args()

    print("Starting preprocess for ppt-canvas-course-summary...")
    clear_gsheet_data()
    print("Preprocess complete.")


if __name__ == "__main__":
    main()
