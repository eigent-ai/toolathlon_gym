"""
PostgreSQL-backed mock Google API service objects.

Provides PgSheetsService and PgDriveService that mimic the Google API
discovery client chain-call pattern (e.g.
service.spreadsheets().values().get(...).execute()) but store/retrieve
all data from a PostgreSQL database.
"""

import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras
import psycopg2.pool

# ---------------------------------------------------------------------------
# A1-notation helpers
# ---------------------------------------------------------------------------

def _col_letter_to_index(letters: str) -> int:
    """Convert column letters to 0-based index: A->0, B->1, Z->25, AA->26."""
    result = 0
    for ch in letters.upper():
        result = result * 26 + (ord(ch) - ord('A') + 1)
    return result - 1


def _col_index_to_letter(index: int) -> str:
    """Convert 0-based column index to letter(s): 0->A, 25->Z, 26->AA."""
    result = ""
    idx = index
    while idx >= 0:
        result = chr(idx % 26 + ord('A')) + result
        idx = idx // 26 - 1
    return result


def _parse_a1_range(range_str: str):
    """Parse A1 notation into components.

    Supports:
      "Sheet1!A1:C10"  -> (sheet_title, 0, 0, 9, 2)
      "Sheet1!A1"      -> (sheet_title, 0, 0, None, None)  (single cell / open)
      "A1:C10"         -> (None, 0, 0, 9, 2)
      "Sheet1"         -> (sheet_title, None, None, None, None)  (whole sheet)
      "Sheet1!A1:5"    -> (sheet_title, 0, 0, 4, None) - row-only end
      "'Sheet Name'!A1:C10" -> handle quoted sheet names

    Returns (sheet_title, start_row, start_col, end_row, end_col)
    where row/col are 0-based integers or None.
    """
    sheet_title = None
    cell_part = range_str

    # Handle sheet name
    if '!' in range_str:
        sheet_title, cell_part = range_str.split('!', 1)
        # Remove surrounding quotes from sheet name
        sheet_title = sheet_title.strip("'").strip('"')

    # If no cell reference at all (just sheet name)
    if not cell_part or cell_part == sheet_title:
        if '!' not in range_str:
            # The whole string is a sheet name
            return (range_str.strip("'").strip('"'), None, None, None, None)
        return (sheet_title, None, None, None, None)

    # Parse cell references
    parts = cell_part.split(':')

    def _parse_cell_ref(ref: str):
        """Parse a single cell reference like 'A1' or 'C10' or just '5' (row only)."""
        ref = ref.strip()
        m = re.match(r'^([A-Za-z]*)(\d*)$', ref)
        if not m:
            return None, None
        col_str, row_str = m.group(1), m.group(2)
        col = _col_letter_to_index(col_str) if col_str else None
        row = int(row_str) - 1 if row_str else None
        return row, col

    start_row, start_col = _parse_cell_ref(parts[0])

    if len(parts) > 1:
        end_row, end_col = _parse_cell_ref(parts[1])
    else:
        end_row, end_col = start_row, start_col

    return (sheet_title, start_row, start_col, end_row, end_col)


def _get_conn(pool):
    """Get a connection from pool."""
    return pool.getconn()


def _put_conn(pool, conn):
    """Return a connection to pool."""
    pool.putconn(conn)


# ---------------------------------------------------------------------------
# Helper: get sheet_id (int) from spreadsheet_id + sheet title
# ---------------------------------------------------------------------------

def _resolve_sheet_id(conn, spreadsheet_id: str, sheet_title: str) -> Optional[int]:
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id FROM gsheet.sheets WHERE spreadsheet_id = %s AND title = %s',
            (spreadsheet_id, sheet_title),
        )
        row = cur.fetchone()
        return row[0] if row else None


def _resolve_default_sheet(conn, spreadsheet_id: str):
    """Return (id, title) of the first sheet (by index) in the spreadsheet."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s ORDER BY "index" LIMIT 1',
            (spreadsheet_id,),
        )
        row = cur.fetchone()
        return (row[0], row[1]) if row else (None, None)


def _get_cells_as_2d(conn, spreadsheet_id, sheet_id, start_row, start_col, end_row, end_col):
    """Fetch cells and assemble into a 2D list of values.

    If end_row/end_col are None, fetch all data from start onwards.
    """
    conditions = ["spreadsheet_id = %s", "sheet_id = %s"]
    params: list = [spreadsheet_id, sheet_id]

    if start_row is not None:
        conditions.append("row_index >= %s")
        params.append(start_row)
    if start_col is not None:
        conditions.append("col_index >= %s")
        params.append(start_col)
    if end_row is not None:
        conditions.append("row_index <= %s")
        params.append(end_row)
    if end_col is not None:
        conditions.append("col_index <= %s")
        params.append(end_col)

    where = " AND ".join(conditions)
    query = f"SELECT row_index, col_index, value, formula, formatted_value FROM gsheet.cells WHERE {where} ORDER BY row_index, col_index"

    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    if not rows:
        return []

    # Determine bounds
    min_row = min(r[0] for r in rows)
    max_row = max(r[0] for r in rows)
    min_col = min(r[1] for r in rows) if start_col is not None else min(r[1] for r in rows)
    max_col = max(r[1] for r in rows)

    # Build 2D array
    num_rows = max_row - min_row + 1
    num_cols = max_col - min_col + 1
    grid: list[list] = [[""] * num_cols for _ in range(num_rows)]

    for row_idx, col_idx, value, formula, formatted_value in rows:
        r = row_idx - min_row
        c = col_idx - min_col
        # Use formatted_value if available, else value
        grid[r][c] = formatted_value if formatted_value is not None else (value if value is not None else "")

    # Trim trailing empty strings from each row, and trailing empty rows
    result = []
    for row in grid:
        # Trim trailing empty cells
        while row and row[-1] == "":
            row.pop()
        result.append(row)

    # Trim trailing empty rows
    while result and not result[-1]:
        result.pop()

    return result


def _get_cells_as_2d_formula(conn, spreadsheet_id, sheet_id, start_row, start_col, end_row, end_col):
    """Like _get_cells_as_2d but returns formulas when available."""
    conditions = ["spreadsheet_id = %s", "sheet_id = %s"]
    params: list = [spreadsheet_id, sheet_id]

    if start_row is not None:
        conditions.append("row_index >= %s")
        params.append(start_row)
    if start_col is not None:
        conditions.append("col_index >= %s")
        params.append(start_col)
    if end_row is not None:
        conditions.append("row_index <= %s")
        params.append(end_row)
    if end_col is not None:
        conditions.append("col_index <= %s")
        params.append(end_col)

    where = " AND ".join(conditions)
    query = f"SELECT row_index, col_index, value, formula FROM gsheet.cells WHERE {where} ORDER BY row_index, col_index"

    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    if not rows:
        return []

    min_row = min(r[0] for r in rows)
    max_row = max(r[0] for r in rows)
    min_col = min(r[1] for r in rows)
    max_col = max(r[1] for r in rows)

    num_rows = max_row - min_row + 1
    num_cols = max_col - min_col + 1
    grid: list[list] = [[""] * num_cols for _ in range(num_rows)]

    for row_idx, col_idx, value, formula in rows:
        r = row_idx - min_row
        c = col_idx - min_col
        grid[r][c] = formula if formula else (value if value is not None else "")

    result = []
    for row in grid:
        while row and row[-1] == "":
            row.pop()
        result.append(row)
    while result and not result[-1]:
        result.pop()

    return result


def _write_cells(conn, spreadsheet_id, sheet_id, start_row, start_col, values):
    """Write a 2D array of values to cells, upserting."""
    if not values:
        return 0

    updated = 0
    with conn.cursor() as cur:
        for r_offset, row in enumerate(values):
            for c_offset, val in enumerate(row):
                row_idx = start_row + r_offset
                col_idx = start_col + c_offset
                str_val = str(val) if val is not None else ""
                formula = str_val if str_val.startswith("=") else None
                cur.execute(
                    """INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value, formula, formatted_value)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT (spreadsheet_id, sheet_id, row_index, col_index)
                       DO UPDATE SET value = EXCLUDED.value, formula = EXCLUDED.formula, formatted_value = EXCLUDED.formatted_value""",
                    (spreadsheet_id, sheet_id, row_idx, col_idx, str_val, formula, str_val),
                )
                updated += 1
    conn.commit()
    return updated


# ---------------------------------------------------------------------------
# Request objects (each has .execute())
# ---------------------------------------------------------------------------

class _BaseRequest:
    """Base class for all request objects."""
    def execute(self):
        raise NotImplementedError


class SpreadsheetGetRequest(_BaseRequest):
    def __init__(self, pool, spreadsheet_id, ranges, include_grid_data, fields):
        self.pool = pool
        self.spreadsheet_id = spreadsheet_id
        self.ranges = ranges or []
        self.include_grid_data = include_grid_data
        self.fields = fields

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            # Get spreadsheet info
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, title FROM gsheet.spreadsheets WHERE id = %s",
                    (self.spreadsheet_id,),
                )
                ss = cur.fetchone()
                if not ss:
                    raise Exception(f"Spreadsheet {self.spreadsheet_id} not found")

                cur.execute(
                    'SELECT id, title, "index", row_count, column_count FROM gsheet.sheets WHERE spreadsheet_id = %s ORDER BY "index"',
                    (self.spreadsheet_id,),
                )
                sheets_rows = cur.fetchall()

            result = {
                "spreadsheetId": self.spreadsheet_id,
                "properties": {"title": ss["title"]},
                "sheets": [],
            }

            for s in sheets_rows:
                sheet_data = {
                    "properties": {
                        "sheetId": s["id"],
                        "title": s["title"],
                        "index": s["index"],
                        "gridProperties": {
                            "rowCount": s["row_count"] or 1000,
                            "columnCount": s["column_count"] or 26,
                        },
                    }
                }

                if self.include_grid_data and self.ranges:
                    # Add grid data for requested ranges
                    for rng in self.ranges:
                        sheet_title, sr, sc, er, ec = _parse_a1_range(rng)
                        if sheet_title and sheet_title != s["title"]:
                            continue
                        cells_2d = _get_cells_as_2d(conn, self.spreadsheet_id, s["id"], sr, sc, er, ec)
                        # Build rowData
                        row_data = []
                        for row_vals in cells_2d:
                            values_list = []
                            for v in row_vals:
                                values_list.append({
                                    "effectiveValue": {"stringValue": str(v)},
                                    "formattedValue": str(v),
                                })
                            row_data.append({"values": values_list})
                        sheet_data["data"] = [{"rowData": row_data}]

                result["sheets"].append(sheet_data)

            return result
        finally:
            _put_conn(self.pool, conn)


class ValuesGetRequest(_BaseRequest):
    def __init__(self, pool, spreadsheet_id, range_str, value_render_option=None):
        self.pool = pool
        self.spreadsheet_id = spreadsheet_id
        self.range_str = range_str
        self.value_render_option = value_render_option

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            sheet_title, sr, sc, er, ec = _parse_a1_range(self.range_str)

            # Resolve sheet
            if sheet_title:
                sheet_id = _resolve_sheet_id(conn, self.spreadsheet_id, sheet_title)
            else:
                sheet_id, sheet_title = _resolve_default_sheet(conn, self.spreadsheet_id)

            if sheet_id is None:
                return {"range": self.range_str, "majorDimension": "ROWS", "values": []}

            if self.value_render_option == "FORMULA":
                values = _get_cells_as_2d_formula(conn, self.spreadsheet_id, sheet_id, sr, sc, er, ec)
            else:
                values = _get_cells_as_2d(conn, self.spreadsheet_id, sheet_id, sr, sc, er, ec)

            return {
                "range": self.range_str,
                "majorDimension": "ROWS",
                "values": values,
            }
        finally:
            _put_conn(self.pool, conn)


class ValuesUpdateRequest(_BaseRequest):
    def __init__(self, pool, spreadsheet_id, range_str, value_input_option, body):
        self.pool = pool
        self.spreadsheet_id = spreadsheet_id
        self.range_str = range_str
        self.value_input_option = value_input_option
        self.body = body or {}

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            sheet_title, sr, sc, er, ec = _parse_a1_range(self.range_str)
            if sr is None:
                sr = 0
            if sc is None:
                sc = 0

            if sheet_title:
                sheet_id = _resolve_sheet_id(conn, self.spreadsheet_id, sheet_title)
            else:
                sheet_id, sheet_title = _resolve_default_sheet(conn, self.spreadsheet_id)

            if sheet_id is None:
                raise Exception(f"Sheet not found for range {self.range_str}")

            values = self.body.get("values", [])
            updated = _write_cells(conn, self.spreadsheet_id, sheet_id, sr, sc, values)

            num_rows = len(values)
            num_cols = max((len(r) for r in values), default=0)

            return {
                "spreadsheetId": self.spreadsheet_id,
                "updatedRange": self.range_str,
                "updatedRows": num_rows,
                "updatedColumns": num_cols,
                "updatedCells": updated,
            }
        finally:
            _put_conn(self.pool, conn)


class ValuesBatchUpdateRequest(_BaseRequest):
    def __init__(self, pool, spreadsheet_id, body):
        self.pool = pool
        self.spreadsheet_id = spreadsheet_id
        self.body = body or {}

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            data_list = self.body.get("data", [])
            total_updated_cells = 0
            total_updated_rows = 0
            total_updated_cols = 0
            responses = []

            for entry in data_list:
                range_str = entry.get("range", "")
                values = entry.get("values", [])
                sheet_title, sr, sc, er, ec = _parse_a1_range(range_str)
                if sr is None:
                    sr = 0
                if sc is None:
                    sc = 0

                if sheet_title:
                    sheet_id = _resolve_sheet_id(conn, self.spreadsheet_id, sheet_title)
                else:
                    sheet_id, _ = _resolve_default_sheet(conn, self.spreadsheet_id)

                if sheet_id is None:
                    continue

                updated = _write_cells(conn, self.spreadsheet_id, sheet_id, sr, sc, values)
                num_rows = len(values)
                num_cols = max((len(r) for r in values), default=0)
                total_updated_cells += updated
                total_updated_rows += num_rows
                total_updated_cols += num_cols
                responses.append({
                    "spreadsheetId": self.spreadsheet_id,
                    "updatedRange": range_str,
                    "updatedRows": num_rows,
                    "updatedColumns": num_cols,
                    "updatedCells": updated,
                })

            return {
                "spreadsheetId": self.spreadsheet_id,
                "totalUpdatedRows": total_updated_rows,
                "totalUpdatedColumns": total_updated_cols,
                "totalUpdatedCells": total_updated_cells,
                "totalUpdatedSheets": len(responses),
                "responses": responses,
            }
        finally:
            _put_conn(self.pool, conn)


class BatchUpdateRequest(_BaseRequest):
    """Handle spreadsheets().batchUpdate() requests (structural changes)."""

    def __init__(self, pool, spreadsheet_id, body):
        self.pool = pool
        self.spreadsheet_id = spreadsheet_id
        self.body = body or {}

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            requests_list = self.body.get("requests", [])
            replies = []

            for req in requests_list:
                if "addSheet" in req:
                    reply = self._handle_add_sheet(conn, req["addSheet"])
                    replies.append({"addSheet": reply})
                elif "updateSheetProperties" in req:
                    self._handle_update_sheet_properties(conn, req["updateSheetProperties"])
                    replies.append({})
                elif "insertDimension" in req:
                    self._handle_insert_dimension(conn, req["insertDimension"])
                    replies.append({})
                elif "deleteDimension" in req:
                    self._handle_delete_dimension(conn, req["deleteDimension"])
                    replies.append({})
                else:
                    # Unknown request type - just acknowledge
                    replies.append({})

            conn.commit()
            return {
                "spreadsheetId": self.spreadsheet_id,
                "replies": replies,
            }
        finally:
            _put_conn(self.pool, conn)

    def _handle_add_sheet(self, conn, add_sheet_req):
        props = add_sheet_req.get("properties", {})
        title = props.get("title", "Sheet")
        row_count = props.get("gridProperties", {}).get("rowCount", 1000)
        col_count = props.get("gridProperties", {}).get("columnCount", 26)

        with conn.cursor() as cur:
            # Determine next index
            cur.execute(
                'SELECT COALESCE(MAX("index"), -1) + 1 FROM gsheet.sheets WHERE spreadsheet_id = %s',
                (self.spreadsheet_id,),
            )
            next_index = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO gsheet.sheets (spreadsheet_id, title, "index", row_count, column_count)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (self.spreadsheet_id, title, next_index, row_count, col_count),
            )
            new_id = cur.fetchone()[0]

        return {
            "properties": {
                "sheetId": new_id,
                "title": title,
                "index": next_index,
                "gridProperties": {
                    "rowCount": row_count,
                    "columnCount": col_count,
                },
            }
        }

    def _handle_update_sheet_properties(self, conn, update_req):
        props = update_req.get("properties", {})
        fields = update_req.get("fields", "")
        sheet_id = props.get("sheetId")

        if sheet_id is None:
            return

        set_clauses = []
        params = []

        if "title" in fields and "title" in props:
            set_clauses.append("title = %s")
            params.append(props["title"])

        if set_clauses:
            params.append(self.spreadsheet_id)
            params.append(sheet_id)
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE gsheet.sheets SET {', '.join(set_clauses)} WHERE spreadsheet_id = %s AND id = %s",
                    params,
                )

    def _handle_insert_dimension(self, conn, insert_req):
        dim_range = insert_req.get("range", {})
        sheet_id = dim_range.get("sheetId")
        dimension = dim_range.get("dimension", "ROWS")
        start_index = dim_range.get("startIndex", 0)
        end_index = dim_range.get("endIndex", start_index + 1)
        count = end_index - start_index

        if dimension == "ROWS":
            # Shift existing cells down
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE gsheet.cells SET row_index = row_index + %s
                       WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index >= %s""",
                    (count, self.spreadsheet_id, sheet_id, start_index),
                )
                # Update row_count
                cur.execute(
                    "UPDATE gsheet.sheets SET row_count = row_count + %s WHERE spreadsheet_id = %s AND id = %s",
                    (count, self.spreadsheet_id, sheet_id),
                )
        elif dimension == "COLUMNS":
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE gsheet.cells SET col_index = col_index + %s
                       WHERE spreadsheet_id = %s AND sheet_id = %s AND col_index >= %s""",
                    (count, self.spreadsheet_id, sheet_id, start_index),
                )
                cur.execute(
                    "UPDATE gsheet.sheets SET column_count = column_count + %s WHERE spreadsheet_id = %s AND id = %s",
                    (count, self.spreadsheet_id, sheet_id),
                )

    def _handle_delete_dimension(self, conn, delete_req):
        dim_range = delete_req.get("range", {})
        sheet_id = dim_range.get("sheetId")
        dimension = dim_range.get("dimension", "ROWS")
        start_index = dim_range.get("startIndex", 0)
        end_index = dim_range.get("endIndex", start_index + 1)
        count = end_index - start_index

        if dimension == "ROWS":
            with conn.cursor() as cur:
                cur.execute(
                    """DELETE FROM gsheet.cells
                       WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index >= %s AND row_index < %s""",
                    (self.spreadsheet_id, sheet_id, start_index, end_index),
                )
                cur.execute(
                    """UPDATE gsheet.cells SET row_index = row_index - %s
                       WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index >= %s""",
                    (count, self.spreadsheet_id, sheet_id, end_index),
                )
                cur.execute(
                    "UPDATE gsheet.sheets SET row_count = GREATEST(row_count - %s, 0) WHERE spreadsheet_id = %s AND id = %s",
                    (count, self.spreadsheet_id, sheet_id),
                )
        elif dimension == "COLUMNS":
            with conn.cursor() as cur:
                cur.execute(
                    """DELETE FROM gsheet.cells
                       WHERE spreadsheet_id = %s AND sheet_id = %s AND col_index >= %s AND col_index < %s""",
                    (self.spreadsheet_id, sheet_id, start_index, end_index),
                )
                cur.execute(
                    """UPDATE gsheet.cells SET col_index = col_index - %s
                       WHERE spreadsheet_id = %s AND sheet_id = %s AND col_index >= %s""",
                    (count, self.spreadsheet_id, sheet_id, end_index),
                )
                cur.execute(
                    "UPDATE gsheet.sheets SET column_count = GREATEST(column_count - %s, 0) WHERE spreadsheet_id = %s AND id = %s",
                    (count, self.spreadsheet_id, sheet_id),
                )


class CopyToRequest(_BaseRequest):
    """Handle sheets().copyTo() requests."""

    def __init__(self, pool, src_spreadsheet_id, src_sheet_id, body):
        self.pool = pool
        self.src_spreadsheet_id = src_spreadsheet_id
        self.src_sheet_id = src_sheet_id
        self.body = body or {}

    def execute(self):
        dst_spreadsheet_id = self.body.get("destinationSpreadsheetId")
        conn = _get_conn(self.pool)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Get source sheet info
                cur.execute(
                    'SELECT title, row_count, column_count FROM gsheet.sheets WHERE spreadsheet_id = %s AND id = %s',
                    (self.src_spreadsheet_id, self.src_sheet_id),
                )
                src_sheet = cur.fetchone()
                if not src_sheet:
                    raise Exception(f"Source sheet {self.src_sheet_id} not found")

                copy_title = f"Copy of {src_sheet['title']}"

                # Determine next index in destination
                cur.execute(
                    'SELECT COALESCE(MAX("index"), -1) + 1 FROM gsheet.sheets WHERE spreadsheet_id = %s',
                    (dst_spreadsheet_id,),
                )
                next_index = cur.fetchone()["coalesce"]

                # Create sheet in destination
                cur.execute(
                    """INSERT INTO gsheet.sheets (spreadsheet_id, title, "index", row_count, column_count)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                    (dst_spreadsheet_id, copy_title, next_index,
                     src_sheet["row_count"], src_sheet["column_count"]),
                )
                new_sheet_id = cur.fetchone()["id"]

                # Copy cells
                cur.execute(
                    """INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value, formula, formatted_value, cell_format)
                       SELECT %s, %s, row_index, col_index, value, formula, formatted_value, cell_format
                       FROM gsheet.cells WHERE spreadsheet_id = %s AND sheet_id = %s""",
                    (dst_spreadsheet_id, new_sheet_id, self.src_spreadsheet_id, self.src_sheet_id),
                )

            conn.commit()
            return {
                "sheetId": new_sheet_id,
                "title": copy_title,
                "index": next_index,
                "sheetType": "GRID",
            }
        finally:
            _put_conn(self.pool, conn)


# ---------------------------------------------------------------------------
# Resource proxy classes
# ---------------------------------------------------------------------------

class ValuesResource:
    def __init__(self, pool):
        self.pool = pool

    def get(self, spreadsheetId=None, range=None, valueRenderOption=None):
        return ValuesGetRequest(self.pool, spreadsheetId, range, valueRenderOption)

    def update(self, spreadsheetId=None, range=None, valueInputOption=None, body=None):
        return ValuesUpdateRequest(self.pool, spreadsheetId, range, valueInputOption, body)

    def batchUpdate(self, spreadsheetId=None, body=None):
        return ValuesBatchUpdateRequest(self.pool, spreadsheetId, body)


class SheetsResource:
    def __init__(self, pool):
        self.pool = pool

    def copyTo(self, spreadsheetId=None, sheetId=None, body=None):
        return CopyToRequest(self.pool, spreadsheetId, sheetId, body)


class SpreadsheetResource:
    def __init__(self, pool):
        self.pool = pool

    def get(self, spreadsheetId=None, ranges=None, includeGridData=False, fields=None):
        return SpreadsheetGetRequest(self.pool, spreadsheetId, ranges, includeGridData, fields)

    def values(self):
        return ValuesResource(self.pool)

    def batchUpdate(self, spreadsheetId=None, body=None):
        return BatchUpdateRequest(self.pool, spreadsheetId, body)

    def sheets(self):
        return SheetsResource(self.pool)


class PgSheetsService:
    """Mock Google Sheets API service backed by PostgreSQL."""

    def __init__(self, pool):
        self.pool = pool

    def spreadsheets(self):
        return SpreadsheetResource(self.pool)


# ---------------------------------------------------------------------------
# Drive service proxies
# ---------------------------------------------------------------------------

class FilesCreateRequest(_BaseRequest):
    def __init__(self, pool, body, fields):
        self.pool = pool
        self.body = body or {}
        self.fields = fields

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            file_id = str(uuid.uuid4())
            name = self.body.get("name", "Untitled")
            mime_type = self.body.get("mimeType", "")
            parents = self.body.get("parents", [])
            folder_id = parents[0] if parents else None

            now = datetime.now(timezone.utc)

            if mime_type == "application/vnd.google-apps.spreadsheet":
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO gsheet.spreadsheets (id, title, folder_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                        (file_id, name, folder_id, now, now),
                    )
                    # Create a default "Sheet1"
                    cur.execute(
                        """INSERT INTO gsheet.sheets (spreadsheet_id, title, "index", row_count, column_count)
                           VALUES (%s, 'Sheet1', 0, 1000, 26)""",
                        (file_id,),
                    )
                conn.commit()
            elif mime_type == "application/vnd.google-apps.folder":
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO gsheet.folders (id, name, parent_id, created_at) VALUES (%s, %s, %s, %s)",
                        (file_id, name, folder_id, now),
                    )
                conn.commit()

            result = {"id": file_id, "name": name}
            if parents:
                result["parents"] = parents
            return result
        finally:
            _put_conn(self.pool, conn)


class FilesListRequest(_BaseRequest):
    def __init__(self, pool, q, spaces, include_all_drives, supports_all_drives, fields, order_by, page_size):
        self.pool = pool
        self.q = q or ""
        self.fields = fields
        self.order_by = order_by
        self.page_size = page_size

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            files = []

            is_spreadsheet_query = "application/vnd.google-apps.spreadsheet" in self.q
            is_folder_query = "application/vnd.google-apps.folder" in self.q

            if is_spreadsheet_query:
                files = self._query_spreadsheets(conn)
            elif is_folder_query:
                files = self._query_folders(conn)
            else:
                # Try both
                files = self._query_spreadsheets(conn) + self._query_folders(conn)

            return {"files": files}
        finally:
            _put_conn(self.pool, conn)

    def _query_spreadsheets(self, conn):
        conditions = []
        params = []

        # Parse parent folder filter
        parent_match = re.search(r"'([^']+)'\s+in\s+parents", self.q)
        if parent_match:
            folder_id = parent_match.group(1)
            if folder_id == "root":
                conditions.append("(folder_id IS NULL)")
            else:
                conditions.append("folder_id = %s")
                params.append(folder_id)

        # Parse name contains filter
        name_match = re.search(r"name\s+contains\s+'([^']+)'", self.q)
        if name_match:
            conditions.append("title ILIKE %s")
            params.append(f"%{name_match.group(1)}%")

        # Parse fullText contains filter
        fulltext_match = re.search(r"fullText\s+contains\s+'([^']+)'", self.q)
        if fulltext_match and not name_match:
            conditions.append("title ILIKE %s")
            params.append(f"%{fulltext_match.group(1)}%")

        where = " AND ".join(conditions) if conditions else "TRUE"

        order = "updated_at DESC"
        if self.order_by and "name" in self.order_by:
            order = "title"

        limit_clause = ""
        if self.page_size:
            limit_clause = f" LIMIT {int(self.page_size)}"

        query = f"SELECT id, title, folder_id, created_at, updated_at FROM gsheet.spreadsheets WHERE {where} ORDER BY {order}{limit_clause}"

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        files = []
        for row in rows:
            f = {"id": row["id"], "name": row["title"]}
            if row.get("folder_id"):
                f["parents"] = [row["folder_id"]]
            if row.get("created_at"):
                f["createdTime"] = row["created_at"].isoformat()
            if row.get("updated_at"):
                f["modifiedTime"] = row["updated_at"].isoformat()
            files.append(f)
        return files

    def _query_folders(self, conn):
        conditions = []
        params = []

        parent_match = re.search(r"'([^']+)'\s+in\s+parents", self.q)
        if parent_match:
            folder_id = parent_match.group(1)
            if folder_id == "root":
                conditions.append("(parent_id IS NULL)")
            else:
                conditions.append("parent_id = %s")
                params.append(folder_id)

        where = " AND ".join(conditions) if conditions else "TRUE"

        order = "name"
        if self.order_by and "modifiedTime" in self.order_by:
            order = "created_at DESC"

        query = f"SELECT id, name, parent_id FROM gsheet.folders WHERE {where} ORDER BY {order}"

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        files = []
        for row in rows:
            f = {"id": row["id"], "name": row["name"]}
            if row.get("parent_id"):
                f["parents"] = [row["parent_id"]]
            files.append(f)
        return files


class PermissionsCreateRequest(_BaseRequest):
    def __init__(self, pool, file_id, body, send_notification, fields):
        self.pool = pool
        self.file_id = file_id
        self.body = body or {}
        self.send_notification = send_notification
        self.fields = fields

    def execute(self):
        conn = _get_conn(self.pool)
        try:
            perm_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)

            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO gsheet.permissions (id, spreadsheet_id, email_address, role, type, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        perm_id,
                        self.file_id,
                        self.body.get("emailAddress"),
                        self.body.get("role"),
                        self.body.get("type", "user"),
                        now,
                    ),
                )
            conn.commit()
            return {"id": perm_id}
        finally:
            _put_conn(self.pool, conn)


class FilesResource:
    def __init__(self, pool):
        self.pool = pool

    def create(self, supportsAllDrives=None, body=None, fields=None):
        return FilesCreateRequest(self.pool, body, fields)

    def list(self, q=None, spaces=None, includeItemsFromAllDrives=None,
             supportsAllDrives=None, fields=None, orderBy=None, pageSize=None):
        return FilesListRequest(self.pool, q, spaces, includeItemsFromAllDrives,
                                supportsAllDrives, fields, orderBy, pageSize)


class PermissionsResource:
    def __init__(self, pool):
        self.pool = pool

    def create(self, fileId=None, body=None, sendNotificationEmail=None, fields=None):
        return PermissionsCreateRequest(self.pool, fileId, body, sendNotificationEmail, fields)


class PgDriveService:
    """Mock Google Drive API service backed by PostgreSQL."""

    def __init__(self, pool):
        self.pool = pool

    def files(self):
        return FilesResource(self.pool)

    def permissions(self):
        return PermissionsResource(self.pool)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_pg_pool():
    """Create a psycopg2 connection pool from environment variables."""
    return psycopg2.pool.SimpleConnectionPool(
        1,
        5,
        host=os.environ.get("PG_HOST", "localhost"),
        port=int(os.environ.get("PG_PORT", "5432")),
        dbname=os.environ.get("PG_DATABASE", "toolathlon"),
        user=os.environ.get("PG_USER", "postgres"),
        password=os.environ.get("PG_PASSWORD", "postgres"),
    )
