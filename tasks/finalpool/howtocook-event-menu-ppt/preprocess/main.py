"""
Preprocess script for howtocook-event-menu-ppt task.
No DB injection needed - HowToCook is a standalone MCP server.
Just ensure the workspace is clean.
"""

import argparse
import os
import glob


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    workspace = args.agent_workspace
    if workspace:
        # Remove any leftover output files
        for pattern in ["Event_Menu_Presentation.pptx", "Menu_Budget.xlsx"]:
            for f in glob.glob(os.path.join(workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
