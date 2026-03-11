"""Preprocess: no data injection needed (all read-only databases)."""
import argparse

def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()
    print("[preprocess] No data injection needed - using read-only Snowflake data.")
    print("[preprocess] Done.")

if __name__ == "__main__":
    main()
