"""Preprocess: no data injection needed (read-only WC data + static PDF)."""
import argparse

def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()
    print("No data injection needed - using read-only WC data and static PDF")

if __name__ == "__main__":
    main()
