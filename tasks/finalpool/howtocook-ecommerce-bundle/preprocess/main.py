"""
Preprocess script for howtocook-ecommerce-bundle task.

WooCommerce, Yahoo Finance, and HowToCook are all read-only data sources.
No writable schemas are used in this task, so preprocessing is minimal.
"""

import argparse
import os


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    workspace = args.agent_workspace
    os.makedirs(workspace, exist_ok=True)

    print("[preprocess] No writable schemas to inject. Workspace ready.")
    print(f"[preprocess] Agent workspace: {workspace}")
    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
