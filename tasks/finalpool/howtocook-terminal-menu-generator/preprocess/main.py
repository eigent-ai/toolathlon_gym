"""
Preprocess for howtocook-terminal-menu-generator task.

Ensures the memory directory exists in the agent workspace.
No writable DB schemas are needed since HowToCook is read-only.
"""
import argparse
import json
import os


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=True)
    parser.add_argument("--launch_time", required=False, help="Launch time")
    args = parser.parse_args()

    os.makedirs(args.agent_workspace, exist_ok=True)
    print(f"[preprocess] Workspace ensured at {args.agent_workspace}")

    mem_dir = os.path.join(args.agent_workspace, "memory")
    os.makedirs(mem_dir, exist_ok=True)
    mem_file = os.path.join(mem_dir, "memory.json")
    with open(mem_file, "w") as f:
        json.dump({"entities": [], "relations": []}, f)
    print(f"[preprocess] Memory file initialized at {mem_file}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
