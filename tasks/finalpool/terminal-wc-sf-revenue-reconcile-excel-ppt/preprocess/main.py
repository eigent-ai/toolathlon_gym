"""Preprocess for terminal-wc-sf-revenue-reconcile-excel-ppt.
WC and SF data are read-only. Just clean up agent workspace."""
import argparse
import glob
import os

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    print("[preprocess] WC and SF data are read-only, no DB injection needed.")

    if args.agent_workspace:
        for pattern in ["Revenue_Reconciliation.xlsx", "Reconciliation_Presentation.pptx",
                        "reconciliation_*.py", "reconciliation_*.json",
                        "wc_*.json", "sf_*.json"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
