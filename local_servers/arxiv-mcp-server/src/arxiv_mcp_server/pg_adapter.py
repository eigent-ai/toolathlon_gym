"""PostgreSQL adapter replacing arxiv API calls for the arxiv-mcp-server."""

import os
import json
import logging
import psycopg2
import psycopg2.extras
from typing import Dict, Any, List
import mcp.types as types
from .config import Settings
from .tools import search_tool, download_tool, list_tool, read_tool  # noqa: F401

logger = logging.getLogger("arxiv-mcp-server")
settings = Settings()


def _get_conn():
    return psycopg2.connect(
        host=os.environ.get('PG_HOST', 'localhost'),
        port=int(os.environ.get('PG_PORT', '5432')),
        dbname=os.environ.get('PG_DATABASE', 'toolathlon'),
        user=os.environ.get('PG_USER', 'postgres'),
        password=os.environ.get('PG_PASSWORD', 'postgres'),
    )


# ---- search.py replacement ----

async def handle_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle paper search using PostgreSQL instead of arXiv API."""
    try:
        max_results = min(int(arguments.get("max_results", 10)), settings.MAX_RESULTS)
        base_query = arguments["query"]
        date_from = arguments.get("date_from")
        date_to = arguments.get("date_to")
        categories = arguments.get("categories")
        sort_by = arguments.get("sort_by", "relevance")

        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                conditions = []
                params = []

                # Full-text search
                if base_query.strip():
                    conditions.append(
                        "to_tsvector('english', coalesce(title,'') || ' ' || coalesce(summary,'')) "
                        "@@ plainto_tsquery('english', %s)"
                    )
                    params.append(base_query)

                # Date filtering
                if date_from:
                    conditions.append("published >= %s::timestamptz")
                    params.append(date_from)
                if date_to:
                    conditions.append("published <= %s::timestamptz")
                    params.append(date_to + "T23:59:59Z" if "T" not in date_to else date_to)

                # Category filtering
                if categories:
                    cat_conditions = []
                    for cat in categories:
                        cat_conditions.append("categories @> %s::jsonb")
                        params.append(json.dumps([cat]))
                    conditions.append("(" + " OR ".join(cat_conditions) + ")")

                where_clause = " AND ".join(conditions) if conditions else "TRUE"

                # Sort
                if sort_by == "date":
                    order_clause = "published DESC NULLS LAST"
                else:
                    if base_query.strip():
                        order_clause = (
                            "ts_rank(to_tsvector('english', coalesce(title,'') || ' ' || coalesce(summary,'')), "
                            "plainto_tsquery('english', %s)) DESC"
                        )
                        params.append(base_query)
                    else:
                        order_clause = "published DESC NULLS LAST"

                params.append(max_results)

                sql = f"""
                    SELECT id, title, authors, summary, categories, primary_category,
                           published, doi, journal_ref, comment, pdf_url, links
                    FROM arxiv.papers
                    WHERE {where_clause}
                    ORDER BY {order_clause}
                    LIMIT %s
                """
                cur.execute(sql, params)
                rows = cur.fetchall()

            # Fallback to ILIKE if FTS returns nothing
            if not rows and base_query.strip():
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, authors, summary, categories, primary_category,
                               published, doi, journal_ref, comment, pdf_url, links
                        FROM arxiv.papers
                        WHERE title ILIKE %s OR summary ILIKE %s
                        LIMIT %s
                    """, (f'%{base_query}%', f'%{base_query}%', max_results))
                    rows = cur.fetchall()

            results = []
            for r in rows:
                authors = r['authors'] or []
                if isinstance(authors, list):
                    authors = [a['name'] if isinstance(a, dict) else str(a) for a in authors]
                else:
                    authors = [str(authors)]

                paper_id = r['id']
                short_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

                results.append({
                    "id": short_id,
                    "title": r['title'],
                    "authors": authors,
                    "abstract": r['summary'] or '',
                    "categories": r['categories'] or [],
                    "published": r['published'].isoformat() if r['published'] else '',
                    "url": r.get('pdf_url') or f"http://arxiv.org/pdf/{paper_id}",
                    "resource_uri": f"arxiv://{short_id}",
                })

            response_data = {"total_results": len(results), "papers": results}
            return [types.TextContent(type="text", text=json.dumps(response_data, indent=2))]

        finally:
            conn.close()

    except Exception as e:
        logger.error(f"PG search error: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


# ---- download.py replacement ----

conversion_statuses: Dict[str, Any] = {}


async def handle_download(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle paper download using PostgreSQL (mark as downloaded)."""
    try:
        paper_id = arguments["paper_id"]
        check_status = arguments.get("check_status", False)

        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, is_downloaded, markdown_content FROM arxiv.papers WHERE id = %s", (paper_id,))
                row = cur.fetchone()

            if not row:
                return [types.TextContent(type="text", text=json.dumps({
                    "status": "error",
                    "message": f"Paper {paper_id} not found in database",
                }))]

            if check_status:
                if row['is_downloaded']:
                    return [types.TextContent(type="text", text=json.dumps({
                        "status": "success",
                        "message": "Paper is ready",
                        "resource_uri": f"arxiv://{paper_id}",
                    }))]
                else:
                    return [types.TextContent(type="text", text=json.dumps({
                        "status": "unknown",
                        "message": "Paper not yet downloaded",
                    }))]

            if row['is_downloaded']:
                return [types.TextContent(type="text", text=json.dumps({
                    "status": "success",
                    "message": "Paper already available",
                    "resource_uri": f"arxiv://{paper_id}",
                }))]

            # Mark as downloaded
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE arxiv.papers SET is_downloaded = TRUE WHERE id = %s",
                    (paper_id,)
                )
                conn.commit()

            return [types.TextContent(type="text", text=json.dumps({
                "status": "success",
                "message": "Paper downloaded and converted successfully",
                "resource_uri": f"arxiv://{paper_id}",
            }))]

        finally:
            conn.close()

    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}",
        }))]


# ---- list_papers.py replacement ----

async def handle_list_papers(arguments=None) -> List[types.TextContent]:
    """List all downloaded papers from PostgreSQL."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, title, summary, authors, pdf_url, links
                    FROM arxiv.papers
                    WHERE is_downloaded = TRUE
                """)
                rows = cur.fetchall()

            papers = []
            for r in rows:
                authors = r['authors'] or []
                if isinstance(authors, list):
                    authors = [a['name'] if isinstance(a, dict) else str(a) for a in authors]
                links_data = r.get('links') or []
                if isinstance(links_data, list):
                    links = [l['href'] if isinstance(l, dict) else str(l) for l in links_data]
                else:
                    links = []

                papers.append({
                    "title": r['title'],
                    "summary": r['summary'] or '',
                    "authors": authors,
                    "links": links,
                    "pdf_url": r.get('pdf_url') or f"http://arxiv.org/pdf/{r['id']}",
                })

            response_data = {"total_papers": len(papers), "papers": papers}
            return [types.TextContent(type="text", text=json.dumps(response_data, indent=2))]

        finally:
            conn.close()

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


# ---- read_paper.py replacement ----

async def handle_read_paper(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Read paper content from PostgreSQL."""
    try:
        paper_id = arguments["paper_id"]

        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, is_downloaded, markdown_content
                    FROM arxiv.papers
                    WHERE id = %s
                """, (paper_id,))
                row = cur.fetchone()

            if not row:
                return [types.TextContent(type="text", text=json.dumps({
                    "status": "error",
                    "message": f"Paper {paper_id} not found in storage. You may need to download it first using download_paper.",
                }))]

            if not row['is_downloaded']:
                return [types.TextContent(type="text", text=json.dumps({
                    "status": "error",
                    "message": f"Paper {paper_id} not found in storage. You may need to download it first using download_paper.",
                }))]

            content = row['markdown_content'] or ''
            return [types.TextContent(type="text", text=json.dumps({
                "status": "success",
                "paper_id": paper_id,
                "content": content,
            }))]

        finally:
            conn.close()

    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({
            "status": "error",
            "message": f"Error reading paper: {str(e)}",
        }))]
