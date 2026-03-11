#!/usr/bin/env python3
"""
Preprocess script for ecommerce-commodity-impact task.

This task uses WooCommerce and Yahoo Finance data which are both read-only,
so no database modifications are needed. The only setup required is ensuring
the initial workspace structure exists with the empty memory.json file.
"""

import os
import sys
import json
import shutil
from argparse import ArgumentParser
from pathlib import Path


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = ArgumentParser(description="Ecommerce Commodity Impact Task Preprocess")
    parser.add_argument("--agent_workspace", required=False, default=None,
                        help="Agent workspace directory")
    parser.add_argument("--launch_time", required=False, help="Task launch time")
    args = parser.parse_args()

    print("=" * 60)
    print("ECOMMERCE COMMODITY IMPACT TASK PREPROCESS")
    print("=" * 60)

    task_dir = Path(__file__).parent.parent
    initial_workspace = task_dir / "initial_workspace"

    # Determine agent workspace
    if args.agent_workspace:
        agent_workspace = Path(args.agent_workspace)
    else:
        agent_workspace = initial_workspace
        print(f"No agent_workspace specified, using initial_workspace: {initial_workspace}")

    # Ensure memory directory exists in agent workspace
    memory_dir = agent_workspace / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    memory_file = memory_dir / "memory.json"
    if not memory_file.exists():
        initial_memory = {"entities": [], "relations": []}
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(initial_memory, f, indent=2)
        print(f"Created initial memory.json at {memory_file}")
    else:
        print(f"memory.json already exists at {memory_file}")

    # Copy initial workspace files to agent workspace if they are different dirs
    if args.agent_workspace and agent_workspace != initial_workspace:
        for item in initial_workspace.rglob("*"):
            if item.is_file():
                rel = item.relative_to(initial_workspace)
                dest = agent_workspace / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.copy2(item, dest)
                    print(f"Copied {rel} to agent workspace")

    print("\nPreprocess completed successfully.")
    print("Note: WooCommerce and Yahoo Finance data are read-only and require no setup.")
    return True


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
