"""
Preprocess script for sf-customer-health-dashboard task.

1. Clears notion and gcal data.
2. Injects a parent Notion page.
3. Extracts mock_pages.tar.gz and starts HTTP server on port 30215.
4. Snowflake data is read-only.
"""
import argparse
import glob as globmod
import json
import os
import shutil
import subprocess
import tarfile
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

PORT = 30215


def clear_schemas(cur):
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")

    print("[preprocess] Clearing GCal events...")
    cur.execute("DELETE FROM gcal.events")

    print("[preprocess] Schemas cleared.")


def inject_notion_parent(cur):
    """Inject a parent page so the agent can create child pages."""
    print("[preprocess] Injecting Notion parent page...")
    page_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO notion.pages (id, object, parent, properties, archived, in_trash)
        VALUES (%s, 'page', %s, %s, false, false)
    """, (
        page_id,
        json.dumps({"type": "workspace", "workspace": True}),
        json.dumps({"title": {"title": [{"text": {"content": "Customer Success"}}]}}),
    ))
    print(f"[preprocess] Injected parent page: {page_id}")
    return page_id


def setup_mock_server():
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)
        print(f"[preprocess] Extracted mock_pages.tar.gz to {tmp_dir}")
    else:
        print(f"[preprocess] WARNING: {tar_path} not found")
        return

    serve_dir = os.path.join(tmp_dir, "mock_pages")
    if not os.path.exists(serve_dir):
        serve_dir = tmp_dir

    try:
        subprocess.run(
            f"kill -9 $(lsof -ti:{PORT}) 2>/dev/null",
            shell=True, capture_output=True,
        )
    except Exception:
        pass

    log_file = os.path.join(tmp_dir, "http.log")
    cmd = f"nohup python3 -m http.server {PORT} --directory {serve_dir} > {log_file} 2>&1 &"
    subprocess.Popen(cmd, shell=True)
    print(f"[preprocess] Started HTTP server on port {PORT} serving {serve_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        clear_schemas(cur)
        inject_notion_parent(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    setup_mock_server()

    if args.agent_workspace:
        for pattern in ["Customer_Health.xlsx"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
