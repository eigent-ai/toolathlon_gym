#  __init__.py - PostgreSQL-backed version (no real YouTube API calls)
from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone, datetime, timedelta
from typing import Any, AsyncIterator, Tuple, Final
from itertools import islice
from contextlib import asynccontextmanager
from urllib.parse import urlparse, parse_qs

import psycopg2
import psycopg2.extras
from mcp import ServerSession
from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from pydantic import Field, BaseModel, AwareDatetime
from functools import lru_cache, partial


def _get_pg_conn():
    import os
    return psycopg2.connect(
        host=os.environ.get('PG_HOST', 'localhost'),
        port=int(os.environ.get('PG_PORT', '5432')),
        dbname=os.environ.get('PG_DATABASE', 'toolathlon'),
        user=os.environ.get('PG_USER', 'postgres'),
        password=os.environ.get('PG_PASSWORD', 'postgres'),
    )


def _parse_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")
    q = parse_qs(parsed_url.query).get("v")
    if q:
        return q[0]
    # Assume it's already a video ID
    return url


@dataclass(frozen=True)
class AppContext:
    pass


@asynccontextmanager
async def _app_lifespan(_server: FastMCP, **kwargs) -> AsyncIterator[AppContext]:
    yield AppContext()


class Transcript(BaseModel):
    """Transcript of a YouTube video."""
    title: str = Field(description="Title of the video")
    transcript: str = Field(description="Transcript of the video")
    next_cursor: str | None = Field(description="Cursor to retrieve the next page of the transcript", default=None)


class TranscriptSnippet(BaseModel):
    """Transcript snippet of a YouTube video."""
    text: str = Field(description="Text of the transcript snippet")
    start: float = Field(description="The timestamp at which this transcript snippet appears on screen in seconds.")
    duration: float = Field(description="The duration of how long the snippet in seconds.")

    def __len__(self) -> int:
        return len(self.model_dump_json())


class TimedTranscript(BaseModel):
    """Transcript of a YouTube video with timestamps."""
    title: str = Field(description="Title of the video")
    snippets: list[TranscriptSnippet] = Field(description="Transcript snippets of the video")
    next_cursor: str | None = Field(description="Cursor to retrieve the next page of the transcript", default=None)


class VideoInfo(BaseModel):
    """Video information."""
    title: str = Field(description="Title of the video")
    description: str = Field(description="Description of the video")
    uploader: str = Field(description="Uploader of the video")
    upload_date: AwareDatetime = Field(description="Upload date of the video")
    duration: str = Field(description="Duration of the video")


def _fetch_from_pg(video_id: str, lang: str = 'en') -> Tuple[str, list[dict]]:
    """Fetch transcript from PostgreSQL."""
    conn = _get_pg_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT title, content, snippets FROM youtube.transcripts WHERE video_id = %s AND language = %s",
            (video_id, lang)
        )
        row = cur.fetchone()
        if not row:
            cur.execute(
                "SELECT title, content, snippets FROM youtube.transcripts WHERE video_id = %s LIMIT 1",
                (video_id,)
            )
            row = cur.fetchone()
        if not row:
            raise ValueError(f"Transcript not found for video: {video_id}")
        title = row['title'] or 'Transcript'
        snippets = row['snippets'] if isinstance(row['snippets'], list) else []
        return title, snippets
    finally:
        conn.close()


def _fetch_video_info_from_pg(video_id: str) -> dict:
    """Fetch video info from PostgreSQL."""
    conn = _get_pg_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT title, description, channel_title, published_at, duration FROM youtube.videos WHERE video_id = %s",
            (video_id,)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Video not found: {video_id}")
        return dict(row)
    finally:
        conn.close()


def server(
    response_limit: int | None = None,
    webshare_proxy_username: str | None = None,
    webshare_proxy_password: str | None = None,
    http_proxy: str | None = None,
    https_proxy: str | None = None,
) -> FastMCP:
    """Initializes the MCP server (PostgreSQL-backed)."""

    mcp = FastMCP("Youtube Transcript", lifespan=partial(_app_lifespan))

    @mcp.tool()
    async def get_transcript(
        ctx: Context[ServerSession, AppContext],
        url: str = Field(description="The URL or video ID of the YouTube video"),
        lang: str = Field(description="The preferred language for the transcript", default="en"),
        next_cursor: str | None = Field(description="Cursor to retrieve the next page of the transcript", default=None),
    ) -> Transcript:
        """Retrieves the transcript of a YouTube video."""
        video_id = _parse_video_id(url)
        title, snippets = _fetch_from_pg(video_id, lang)
        texts = (s['text'] for s in snippets)

        if response_limit is None or response_limit <= 0:
            return Transcript(title=title, transcript="\n".join(texts))

        res = ""
        cursor = None
        for i, line in islice(enumerate(texts), int(next_cursor or 0), None):
            if len(res) + len(line) + 1 > response_limit:
                cursor = str(i)
                break
            res += f"{line}\n"

        return Transcript(title=title, transcript=res.rstrip("\n"), next_cursor=cursor)

    @mcp.tool()
    async def get_timed_transcript(
        ctx: Context[ServerSession, AppContext],
        url: str = Field(description="The URL or video ID of the YouTube video"),
        lang: str = Field(description="The preferred language for the transcript", default="en"),
        next_cursor: str | None = Field(description="Cursor to retrieve the next page of the transcript", default=None),
    ) -> TimedTranscript:
        """Retrieves the transcript of a YouTube video with timestamps."""
        video_id = _parse_video_id(url)
        title, snippets = _fetch_from_pg(video_id, lang)
        snippet_objs = [TranscriptSnippet(text=s['text'], start=float(s.get('start', 0)), duration=float(s.get('duration', 0))) for s in snippets]

        if response_limit is None or response_limit <= 0:
            return TimedTranscript(title=title, snippets=snippet_objs)

        res = []
        size = len(title) + 1
        cursor = None
        for i, snippet in islice(enumerate(snippet_objs), int(next_cursor or 0), None):
            if size + len(snippet) + 1 > response_limit:
                cursor = str(i)
                break
            res.append(snippet)
            size += len(snippet) + 1

        return TimedTranscript(title=title, snippets=res, next_cursor=cursor)

    @mcp.tool()
    def get_video_info(
        ctx: Context[ServerSession, AppContext],
        url: str = Field(description="The URL or video ID of the YouTube video"),
    ) -> VideoInfo:
        """Retrieves the video information."""
        video_id = _parse_video_id(url)
        info = _fetch_video_info_from_pg(video_id)
        # Parse published_at
        pub = info.get('published_at')
        if isinstance(pub, datetime):
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            upload_date = pub
        else:
            upload_date = datetime.now(timezone.utc)
        # Format duration (ISO 8601 → human readable)
        dur_str = info.get('duration', 'PT0S')
        return VideoInfo(
            title=info['title'] or '',
            description=info.get('description') or '',
            uploader=info.get('channel_title') or '',
            upload_date=upload_date,
            duration=dur_str,
        )

    return mcp


__all__: Final = ["server", "Transcript", "TimedTranscript", "TranscriptSnippet", "VideoInfo"]
