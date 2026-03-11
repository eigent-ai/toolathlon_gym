"""
Preprocess script for fetch-howtocook-catering-budget-excel-gcal-word task.

1. Clears gcal events (writable schema).
2. Injects noise gcal events.
3. Extracts mock_pages.tar.gz and starts HTTP server on port 30217.
"""
import argparse
import asyncio
import glob as globmod
import os
import shutil
import tarfile
from datetime import datetime, timedelta

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_gcal(cur):
    print("[preprocess] Clearing GCal events...")
    cur.execute("DELETE FROM gcal.events")
    print("[preprocess] GCal events cleared.")


def inject_noise_gcal(cur, launch_dt):
    """Inject noise calendar events."""
    print("[preprocess] Injecting noise GCal events...")
    dt1 = (launch_dt + timedelta(days=37)).strftime('%Y-%m-%d')
    dt2 = (launch_dt + timedelta(days=38)).strftime('%Y-%m-%d')
    cur.execute(f"""
        INSERT INTO gcal.events (summary, description, start_datetime, end_datetime)
        VALUES ('Weekly Team Meeting', 'Regular team sync', '{dt1} 09:00:00+00', '{dt1} 10:00:00+00')
    """)
    cur.execute(f"""
        INSERT INTO gcal.events (summary, description, start_datetime, end_datetime)
        VALUES ('Vendor Call', 'Quarterly vendor review', '{dt2} 14:00:00+00', '{dt2} 15:00:00+00')
    """)
    print("[preprocess] Noise GCal events injected.")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30217."""
    print("[preprocess] Setting up mock supplier API server...")

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
    port = 30217

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

    launch_dt = datetime.strptime(args.launch_time, "%Y-%m-%d %H:%M:%S") if args.launch_time else datetime(2026, 3, 7)

    try:
        clear_gcal(cur)
        inject_noise_gcal(cur, launch_dt)
        conn.commit()
        print("[preprocess] Database operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()

    if args.agent_workspace:
        for pattern in ["Catering_Budget.xlsx", "Catering_Proposal.docx"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
