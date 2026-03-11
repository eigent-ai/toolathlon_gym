"""Preprocess for wc-review-competitor-study. Sets up mock server and clears notion."""
import argparse
import asyncio
import os
import shutil
import tarfile

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}
PORT = 30203


def clear_notion(cur):
    """Clear Notion data and inject parent page."""
    print("[preprocess] Clearing Notion data...")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")

    # Inject noise data - a few unrelated pages
    cur.execute("""INSERT INTO notion.pages (id, object, properties, url, archived, in_trash)
        VALUES ('page-kb-root', 'page',
        '{"title": {"title": [{"text": {"content": "Knowledge Base"}}]}}',
        'https://notion.so/kb-root', false, false)""")
    cur.execute("""INSERT INTO notion.pages (id, object, properties, url, archived, in_trash,
        parent)
        VALUES ('page-old-analysis', 'page',
        '{"title": {"title": [{"text": {"content": "Old Q4 2025 Analysis"}}]}}',
        'https://notion.so/old-analysis', false, false,
        '{"type": "page_id", "page_id": "page-kb-root"}')""")
    print("[preprocess] Notion data cleared and parent pages injected.")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server."""
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)

    serve_dir = os.path.join(tmp_dir, "mock_pages")

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{PORT}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {PORT} --directory {serve_dir} "
        f"> {tmp_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server running at http://localhost:{PORT}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        clear_notion(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
