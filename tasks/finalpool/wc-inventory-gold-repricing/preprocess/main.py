"""
Preprocess script for wc-inventory-gold-repricing task.

This script:
1. Extracts mock_pages.tar.gz to serve the supplier pricing portal
2. Kills any existing process on port 30148
3. Starts an HTTP server on port 30148

WooCommerce and Yahoo Finance are read-only; no data injection needed.
"""

import argparse
import os
import signal
import subprocess
import sys
import tarfile
import time


TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
    if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == "preprocess" \
    else os.path.dirname(os.path.abspath(__file__))
PORT = 30148


def kill_port(port):
    """Kill any process listening on the given port."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split("\n")
        for pid in pids:
            if pid.strip():
                try:
                    os.kill(int(pid.strip()), signal.SIGKILL)
                    print(f"[preprocess] Killed PID {pid.strip()} on port {port}")
                except (ProcessLookupError, ValueError):
                    pass
    except Exception as e:
        print(f"[preprocess] Note: could not check port {port}: {e}")


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    # Determine paths
    # TASK_ROOT should be the task directory (parent of preprocess/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(script_dir) == "preprocess":
        task_root = os.path.dirname(script_dir)
    else:
        task_root = script_dir

    tar_path = os.path.join(task_root, "files", "mock_pages.tar.gz")
    extract_dir = os.path.join(task_root, "files")
    serve_dir = os.path.join(extract_dir, "mock_pages")

    # Extract mock pages
    if not os.path.exists(serve_dir):
        print(f"[preprocess] Extracting {tar_path} ...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)
        print(f"[preprocess] Extracted to {serve_dir}")
    else:
        print(f"[preprocess] {serve_dir} already exists, skipping extraction")

    # Kill existing process on port
    kill_port(PORT)
    time.sleep(0.5)

    # Start HTTP server
    print(f"[preprocess] Starting HTTP server on port {PORT} serving {serve_dir}")
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=serve_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)

    # Verify server is running
    if proc.poll() is None:
        print(f"[preprocess] HTTP server started (PID {proc.pid}) on port {PORT}")
    else:
        print(f"[preprocess] ERROR: HTTP server failed to start")
        sys.exit(1)

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
