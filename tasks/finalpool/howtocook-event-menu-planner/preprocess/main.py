"""
Preprocess for howtocook-event-menu-planner task.
- Clears email schema.
- Starts mock HTTP server on port 30234.
"""
import argparse
import asyncio
import json
import os
import shutil
import tarfile

import psycopg2

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

MOCK_PORT = 30234


def clear_email(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM email.drafts")
        cur.execute("DELETE FROM email.folders")
        cur.execute("DELETE FROM email.account_config")
        # Set up email account
        cur.execute("INSERT INTO email.account_config (email, name) VALUES (%s, %s)",
                    ("events@company.com", "Event Planning Team"))
        cur.execute("INSERT INTO email.folders (name, delimiter, flags) VALUES (%s, %s, %s)",
                    ("INBOX", "/", '["\\\\Inbox"]'))
        cur.execute("INSERT INTO email.folders (name, delimiter, flags) VALUES (%s, %s, %s)",
                    ("Sent", "/", '["\\\\Sent"]'))
    conn.commit()
    print("[preprocess] Cleared and configured email")


async def setup_mock_server():
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    mock_src = os.path.join(files_dir, "mock_pages")
    if not os.path.exists(tar_path) and os.path.exists(mock_src):
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(mock_src, arcname="mock_pages")

    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)
        serve_dir = os.path.join(tmp_dir, "mock_pages")
    else:
        serve_dir = tmp_dir
        if os.path.exists(mock_src):
            shutil.copytree(mock_src, os.path.join(tmp_dir, "mock_pages"))
            serve_dir = os.path.join(tmp_dir, "mock_pages")

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{MOCK_PORT}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {MOCK_PORT} --directory {serve_dir} "
        f"> {serve_dir}/server.log 2>&1 &")
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server at http://localhost:{MOCK_PORT}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_email(conn)
    finally:
        conn.close()

    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
