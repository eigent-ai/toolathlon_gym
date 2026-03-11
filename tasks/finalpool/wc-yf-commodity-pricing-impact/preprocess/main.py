"""Preprocess for wc-yf-commodity-pricing-impact.
Starts mock HTTP server for commodity indices on port 30236.
WC and YF are read-only, no DB modifications needed.
"""
import argparse
import asyncio
import os
import shutil


async def setup_mock_server():
    """Start HTTP server on port 30236 serving mock_pages."""
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files", "mock_pages")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    shutil.copytree(files_dir, tmp_dir)
    print(f"[preprocess] Copied mock_pages to {tmp_dir}")

    port = 30236
    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{port}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {port} --directory {tmp_dir} "
        f"> {tmp_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server running at http://localhost:{port}")


async def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    await setup_mock_server()

    if args.agent_workspace:
        initial_ws = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "initial_workspace")
        for f in os.listdir(initial_ws):
            src = os.path.join(initial_ws, f)
            if os.path.isfile(src) and not f.startswith("."):
                shutil.copy2(src, os.path.join(args.agent_workspace, f))
        print(f"[preprocess] Copied initial_workspace files to {args.agent_workspace}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
