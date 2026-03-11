"""
Preprocess for howtocook-notion-recipe-kb task.
- Clears Notion schema (comments, blocks, pages, databases)
- Ensures memory directory and file exist in agent workspace

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
import json
import os

import psycopg2

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    # Clear Notion tables
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    conn.commit()
    cur.close()
    conn.close()
    print("Cleared Notion schema (comments, blocks, pages, databases)")

    # Ensure memory directory and file exist
    if args.agent_workspace:
        mem_dir = os.path.join(args.agent_workspace, "memory")
        os.makedirs(mem_dir, exist_ok=True)
        mem_file = os.path.join(mem_dir, "memory.json")
        if not os.path.exists(mem_file):
            with open(mem_file, "w") as f:
                json.dump({"entities": [], "relations": []}, f)
        print(f"Memory file ensured at {mem_file}")

    print("Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
