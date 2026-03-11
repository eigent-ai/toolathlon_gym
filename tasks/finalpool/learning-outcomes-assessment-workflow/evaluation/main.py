#!/usr/bin/env python3
"""Evaluation script for task validation"""

from argparse import ArgumentParser
import sys
from pathlib import Path

def num_close(a, b, rel_tol=0.15, abs_tol=0.5):
    """Numeric comparison with tolerance - uses lower() for string normalization."""
    return abs(float(a) - float(b)) <= max(abs_tol, abs(float(b)) * rel_tol)


def run_evaluation(agent_workspace, groundtruth_workspace, launch_time, res_log_file):
    """Run evaluation checks"""
    
    # Check if agent workspace has expected outputs
    if not agent_workspace:
        return False, "No agent workspace provided"
    
    agent_ws = Path(agent_workspace)
    if not agent_ws.exists():
        return False, f"Agent workspace not found: {agent_workspace}"
    
    # Basic validation: check if any files were created
    files_created = list(agent_ws.glob("*"))
    if not files_created:
        return False, "No files created in agent workspace"
    
    return True, "Evaluation passed"

def main():
    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--res_log_file", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()
    
    success, message = run_evaluation(
        args.agent_workspace,
        args.groundtruth_workspace,
        args.launch_time,
        args.res_log_file
    )
    
    print(message)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
