"""
Preprocess for howtocook-workshop-materials task.

This task does not use any writable DB schemas.
The agent retrieves recipes from the HowToCook MCP server at runtime.
Preprocess simply ensures the agent workspace directory exists.
"""
import argparse
import os


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False, help="Launch time")
    args = parser.parse_args()

    if args.agent_workspace:
        os.makedirs(args.agent_workspace, exist_ok=True)
        print(f"Agent workspace ready: {args.agent_workspace}")

    print("Preprocessing completed - no database setup needed for this task.")


if __name__ == "__main__":
    main()
