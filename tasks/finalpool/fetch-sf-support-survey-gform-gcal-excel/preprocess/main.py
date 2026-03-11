"""
Preprocess script for fetch-sf-support-survey-gform-gcal-excel task.

1. Clears gcal, gform data (writable schemas).
2. Extracts mock_pages.tar.gz and starts HTTP server on port 30205.
3. sf_data is read-only -- do NOT modify.
"""

import argparse
import asyncio
import glob as globmod
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


def clear_gcal(cur):
    print("[preprocess] Clearing Google Calendar events...")
    cur.execute("DELETE FROM gcal.events")
    print("[preprocess] Google Calendar events cleared.")


def clear_gform(cur):
    print("[preprocess] Clearing Google Forms data...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    print("[preprocess] Google Forms data cleared.")


def inject_noise_data(cur):
    """Insert noise data so the agent must filter correctly."""
    print("[preprocess] Injecting noise data...")
    # Noise calendar events
    noise_events = [
        ("All-Hands Meeting", "Company all-hands", "2026-03-20 14:00:00+00", "2026-03-20 15:00:00+00"),
        ("Product Launch Sync", "Sync on upcoming launch", "2026-03-22 10:00:00+00", "2026-03-22 11:00:00+00"),
    ]
    for i, (summary, desc, start, end) in enumerate(noise_events):
        cur.execute("""
            INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime)
            VALUES (%s, %s, %s, %s, %s)
        """, (f"noise-support-event-{i}", summary, desc, start, end))

    # Noise Google Form
    cur.execute("""
        INSERT INTO gform.forms (id, title, document_title, description)
        VALUES (%s, %s, %s, %s)
    """, ("noise-form-001", "Employee Satisfaction Survey", "Employee Satisfaction Survey",
          "Internal employee feedback form"))
    print("[preprocess] Noise data injected.")


async def setup_mock_server():
    print("[preprocess] Setting up mock survey API server...")

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
    port = 30205

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
        clear_gform(cur)
        inject_noise_data(cur)
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

    if args.agent_workspace:
        for pattern in ["Support_Satisfaction_Analysis.xlsx"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
