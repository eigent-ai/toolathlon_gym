"""Preprocess for terminal-sf-wc-order-audit-excel-word.
No writable schemas used. Snowflake and WooCommerce are read-only.
Just clears any leftover files from previous runs."""
import argparse
import os
import glob as globmod


def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    if args.agent_workspace:
        for pattern in ["Order_Audit_Report.xlsx", "Audit_Findings.docx", "audit_analysis.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done. No DB injection needed (read-only sources).")


if __name__ == "__main__":
    main()
