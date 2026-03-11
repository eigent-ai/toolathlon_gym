"""Local shim that shadows the installed yfinance package.

Routes all data access through PostgreSQL via pg_adapter,
so server.py's `import yfinance as yf; yf.Ticker(...)` hits the DB.
"""
from pg_adapter import PgTicker as Ticker  # noqa: F401
