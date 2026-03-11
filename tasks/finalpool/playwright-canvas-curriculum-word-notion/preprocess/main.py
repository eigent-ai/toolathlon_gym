"""
Preprocess script for playwright-canvas-curriculum-word-notion task.

This script:
1. Clears notion, email data
2. Injects noise data
3. Extracts mock_pages.tar.gz and starts HTTP server on port 30210
NOTE: Does NOT modify Canvas data (read-only).
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


def clear_notion(cur):
    """Clear all Notion data."""
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM notion.users")
    print("[preprocess] Notion data cleared.")


def clear_emails(cur):
    """Clear all email data."""
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    try:
        cur.execute("DELETE FROM email.sent_log")
    except Exception:
        pass
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    print("[preprocess] Email data cleared.")


def inject_noise_notion(cur):
    """Inject noise Notion data."""
    print("[preprocess] Injecting noise Notion data...")
    page_id = f"noise-page-{uuid.uuid4()}"
    cur.execute(
        "INSERT INTO notion.pages (id, parent, properties) VALUES (%s, %s, %s)",
        (
            page_id,
            json.dumps({"type": "workspace", "workspace": True}),
            json.dumps({
                "title": {
                    "id": "title",
                    "type": "title",
                    "title": [{"type": "text", "plain_text": "Meeting Notes - February"}],
                }
            }),
        ),
    )
    print("[preprocess] Noise Notion data injected.")


def inject_noise_email(cur):
    """Inject noise email data."""
    print("[preprocess] Injecting noise email data...")
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    row = cur.fetchone()
    if not row:
        return
    folder_id = row[0]
    cur.execute(
        """INSERT INTO email.messages
            (folder_id, message_id, subject, from_addr, to_addr, body_text)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            folder_id,
            f"<noise-{uuid.uuid4()}@university.edu>",
            "Campus Facilities Update",
            "facilities@university.edu",
            json.dumps(["all-staff@university.edu"]),
            "The library renovation will be completed by March 15.",
        ),
    )
    print("[preprocess] Noise email data injected.")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30210."""
    print("[preprocess] Setting up mock accreditation standards server...")

    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)

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
    print(f"[preprocess] Mock server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_notion(cur)
        clear_emails(cur)
        inject_noise_notion(cur)
        inject_noise_email(cur)
        conn.commit()
        print("[preprocess] Database operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Database error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
