#!/usr/bin/env python3
"""Runner that ensures stdin is in blocking mode before starting FastMCP."""
import fcntl, os, sys

# Set stdin to blocking mode (anyio on macOS may see EAGAIN as EOF otherwise)
flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags & ~os.O_NONBLOCK)

from mcp_youtube_transcript import server
s = server(50000)
s.run()
