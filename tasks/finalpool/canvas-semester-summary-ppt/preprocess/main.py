"""Preprocess: no writable schemas used for this task."""
import argparse


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()
    print("No writable schemas to clear for this task.")


if __name__ == "__main__":
    main()
