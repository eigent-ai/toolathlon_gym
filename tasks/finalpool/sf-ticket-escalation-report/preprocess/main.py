"""
Preprocess script for sf-ticket-escalation-report task.

1. Clears email and notion data (writable schemas).
2. Injects a notion parent page for the agent to create under.
3. Extracts mock_pages.tar.gz and starts HTTP server on port 30210.
4. sf_data is read-only -- do NOT modify.
"""
import argparse
import asyncio
import json
import os
import shutil
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


def clear_emails(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    print("[preprocess] Email data cleared.")


def clear_notion(cur):
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    print("[preprocess] Notion data cleared.")


def inject_notion_parent(cur):
    """Inject a parent page for the agent to create the escalation page under."""
    print("[preprocess] Injecting Notion parent page...")
    page_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO notion.pages (id, object, parent, properties, archived, in_trash)
        VALUES (%s, 'page', %s, %s, false, false)
    """, (
        page_id,
        json.dumps({"type": "workspace", "workspace": True}),
        json.dumps({"title": {"title": [{"text": {"content": "Support Team"}}]}}),
    ))
    print(f"[preprocess] Notion parent page created: {page_id}")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30210."""
    print("[preprocess] Setting up mock escalation rules API...")

    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)
    print(f"[preprocess] Extracted {tar_path} to {tmp_dir}")

    mock_dir = os.path.join(tmp_dir, "mock_pages")
    port = 30210

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{port}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {port} --directory {mock_dir} "
        f"> {mock_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock API server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_emails(cur)
        clear_notion(cur)
        inject_notion_parent(cur)
        conn.commit()
        print("[preprocess] DB operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()
    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
