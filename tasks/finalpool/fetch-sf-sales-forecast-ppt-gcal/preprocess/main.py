"""
Preprocess script for fetch-sf-sales-forecast-ppt-gcal task.

This script:
1. Clears gcal data
2. Injects noise calendar event
3. Extracts mock_pages.tar.gz and starts HTTP server on port 30209
NOTE: Does NOT modify Snowflake data (read-only).
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


def clear_gcal(cur):
    """Clear all Google Calendar events."""
    print("[preprocess] Clearing Google Calendar events...")
    cur.execute("DELETE FROM gcal.events")
    print("[preprocess] Google Calendar events cleared.")


def inject_noise_gcal(cur):
    """Inject noise calendar event."""
    print("[preprocess] Injecting noise calendar event...")
    cur.execute(
        "INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime) "
        "VALUES (%s, %s, %s, %s, %s)",
        (
            f"noise-{uuid.uuid4()}",
            "Weekly Team Standup",
            "Regular weekly team standup meeting",
            "2026-03-10T09:00:00+00:00",
            "2026-03-10T09:30:00+00:00",
        ),
    )
    print("[preprocess] Noise calendar event injected.")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30209."""
    print("[preprocess] Setting up mock market research API...")

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
    port = 30209

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
        clear_gcal(cur)
        inject_noise_gcal(cur)
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
