"""
Preprocess for q4-sales-reconciliation task.
Snowflake is read-only, so no data injection is needed.
"""
import argparse


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    print("No data injection needed - Snowflake is read-only")


if __name__ == "__main__":
    main()
