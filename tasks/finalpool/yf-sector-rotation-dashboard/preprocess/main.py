"""Preprocess for yf-sector-rotation-dashboard.
Extracts mock HTML pages and starts HTTP server on port 30145.
"""
from argparse import ArgumentParser
import os
import tarfile
import shutil
import subprocess
import time


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    task_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    # Clean up tmp_dir
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    # Extract mock_pages.tar.gz
    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    if not os.path.exists(tar_path):
        print(f"ERROR: {tar_path} not found")
        return
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)
    print(f"Extracted mock_pages.tar.gz to {tmp_dir}")

    serve_dir = os.path.join(tmp_dir, "mock_pages")
    if not os.path.isdir(serve_dir):
        # If tar extracts directly without mock_pages/ wrapper
        serve_dir = tmp_dir

    # Kill any existing process on port 30145
    subprocess.run("kill -9 $(lsof -ti:30145) 2>/dev/null", shell=True,
                   capture_output=True)
    time.sleep(0.5)

    # Start HTTP server on port 30145
    log_path = os.path.join(tmp_dir, "http.log")
    subprocess.Popen(
        ["python", "-m", "http.server", "30145", "--directory", serve_dir],
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    time.sleep(1)

    # Verify server started
    import urllib.request
    try:
        resp = urllib.request.urlopen("http://localhost:30145", timeout=5)
        print(f"Mock research portal running at http://localhost:30145 (status {resp.status})")
    except Exception as e:
        print(f"WARNING: Could not verify server: {e}")

    print("Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
