"""Preprocess: Snowflake is read-only. Clear Google Calendar events."""
import os
import argparse
import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM gcal.events")
    conn.commit()
    cur.close()
    conn.close()
    print("Google Calendar events cleared for clean state.")


if __name__ == "__main__":
    main()
