"""Preprocess: no-op for read-only data sources (Yahoo Finance)."""
import argparse


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()
    print("No preprocess needed: Yahoo Finance is read-only, PDF is pre-generated.")


if __name__ == "__main__":
    main()
