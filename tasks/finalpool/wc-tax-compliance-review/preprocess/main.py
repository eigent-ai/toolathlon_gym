"""
Preprocess script for wc-tax-compliance-review task.

1. Extracts mock_pages.tar.gz and starts HTTP server on port 30205.
2. WC schema is read-only -- do NOT modify.
"""

import argparse
import asyncio
import os
import shutil
import tarfile

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30205."""
    print("[preprocess] Setting up mock tax authority website...")

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
    print(f"[preprocess] Mock tax authority website running at http://localhost:{port}")


async def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    await setup_mock_server()

    if args.agent_workspace:
        for fname in ["Tax_Compliance.xlsx", "Tax_Compliance_Report.docx"]:
            fpath = os.path.join(args.agent_workspace, fname)
            if os.path.exists(fpath):
                os.remove(fpath)
                print(f"[preprocess] Removed {fpath}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
