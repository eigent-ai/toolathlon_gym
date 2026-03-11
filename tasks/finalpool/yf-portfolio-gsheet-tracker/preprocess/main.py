"""
Preprocess for yf-portfolio-gsheet-tracker task.
- Clears gsheet schema tables
- Injects spreadsheet, sheet, and header cells into gsheet schema
- Extracts mock_pages.tar.gz and starts HTTP server on port 30155
"""
import argparse
import asyncio
import os
import shutil
import tarfile
import psycopg2


DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

SPREADSHEET_ID = "sp_portfolio_tracker_q1_2026"
SPREADSHEET_TITLE = "Portfolio Tracker Q1 2026"
SHEET_ID = 1
SHEET_TITLE = "Holdings"
PORT = 30155

HEADERS = [
    "Symbol", "Shares", "Purchase_Price", "Current_Price", "Market_Value",
    "Gain_Loss", "Gain_Loss_Pct", "Allocation_Pct", "Risk_Rating", "Compliance_Status",
]

# Pre-filled data (first 3 columns for rows 2-6)
PREFILLED_DATA = [
    ("AMZN", "50", "178.25"),
    ("GOOGL", "80", "175.50"),
    ("JNJ", "120", "148.30"),
    ("JPM", "60", "198.75"),
    ("XOM", "100", "112.40"),
]


def setup_gsheet():
    """Clear gsheet tables and inject spreadsheet data."""
    conn = psycopg2.connect(**DB_CONN)
    conn.autocommit = True
    cur = conn.cursor()

    # Clear tables in dependency order
    print("Clearing gsheet tables ...")
    cur.execute("DELETE FROM gsheet.cells;")
    cur.execute("DELETE FROM gsheet.permissions;")
    cur.execute("DELETE FROM gsheet.sheets;")
    cur.execute("DELETE FROM gsheet.spreadsheets;")
    cur.execute("DELETE FROM gsheet.folders;")
    print("  -> All gsheet tables cleared.")

    # Insert spreadsheet
    cur.execute(
        "INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s);",
        (SPREADSHEET_ID, SPREADSHEET_TITLE),
    )
    print(f"  -> Spreadsheet inserted: {SPREADSHEET_TITLE}")

    # Insert sheet
    cur.execute(
        "INSERT INTO gsheet.sheets (id, spreadsheet_id, title, index, row_count, column_count) "
        "VALUES (%s, %s, %s, 0, 1000, 26);",
        (SHEET_ID, SPREADSHEET_ID, SHEET_TITLE),
    )
    print(f"  -> Sheet inserted: {SHEET_TITLE}")

    # Insert header row (row_index=0)
    for col_idx, header in enumerate(HEADERS):
        cur.execute(
            "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value, formatted_value) "
            "VALUES (%s, %s, %s, %s, %s, %s);",
            (SPREADSHEET_ID, SHEET_ID, 0, col_idx, header, header),
        )

    # Insert pre-filled data rows (row_index 1-5, col_index 0-2)
    for row_offset, (symbol, shares, price) in enumerate(PREFILLED_DATA):
        row_idx = row_offset + 1
        for col_idx, val in enumerate([symbol, shares, price]):
            cur.execute(
                "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value, formatted_value) "
                "VALUES (%s, %s, %s, %s, %s, %s);",
                (SPREADSHEET_ID, SHEET_ID, row_idx, col_idx, val, val),
            )

    print(f"  -> Header and pre-filled data cells inserted ({len(HEADERS)} headers + {len(PREFILLED_DATA) * 3} data cells).")

    cur.close()
    conn.close()


async def run_command(cmd: str):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc.wait()


async def setup_mock_server():
    """Extract mock pages and start HTTP server."""
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")

    print("Setting up mock compliance portal ...")
    tmp_dir = os.path.join(task_root, "tmp")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)
    print(f"  -> Extracted {tar_path} to {tmp_dir}")

    mock_dir = os.path.join(tmp_dir, "mock_pages")
    await run_command(f"kill -9 $(lsof -ti:{PORT}) 2>/dev/null")
    await asyncio.sleep(0.5)
    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {PORT} --directory {mock_dir} "
        f"> {mock_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"  -> Mock compliance portal running at http://localhost:{PORT}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    # 1. Set up Google Sheet data in database
    setup_gsheet()

    # 2. Set up mock HTTP server
    await setup_mock_server()

    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
