import os
import psycopg2
import psycopg2.extras
from typing import List


def _get_conn():
    return psycopg2.connect(
        host=os.environ.get('PG_HOST', 'localhost'),
        port=int(os.environ.get('PG_PORT', '5432')),
        dbname=os.environ.get('PG_DATABASE', 'toolathlon'),
        user=os.environ.get('PG_USER', 'postgres'),
        password=os.environ.get('PG_PASSWORD', 'postgres'),
    )


class ArxivSearch:
    def __init__(self):
        pass

    def search(self, keyword, max_results=10) -> List[str]:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Use full-text search on title and abstract
                cur.execute("""
                    SELECT id, title, authors, abstract, categories, primary_category,
                           published, updated, doi, journal_ref, comment, pdf_url, html_url
                    FROM scholarly.arxiv_papers
                    WHERE to_tsvector('english', coalesce(title,'') || ' ' || coalesce(abstract,''))
                          @@ plainto_tsquery('english', %s)
                    ORDER BY ts_rank(
                        to_tsvector('english', coalesce(title,'') || ' ' || coalesce(abstract,'')),
                        plainto_tsquery('english', %s)
                    ) DESC
                    LIMIT %s
                """, (keyword, keyword, max_results))
                rows = cur.fetchall()

            if not rows:
                # Fallback: ILIKE search
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, authors, abstract, categories, primary_category,
                               published, updated, doi, journal_ref, comment, pdf_url, html_url
                        FROM scholarly.arxiv_papers
                        WHERE title ILIKE %s OR abstract ILIKE %s
                        LIMIT %s
                    """, (f'%{keyword}%', f'%{keyword}%', max_results))
                    rows = cur.fetchall()

            formatted_results = []
            for r in rows:
                authors = r['authors'] or []
                if isinstance(authors, list):
                    authors = ", ".join(str(a) for a in authors)
                categories = r['categories'] or []
                if isinstance(categories, list):
                    all_categories = ", ".join(categories)
                else:
                    all_categories = str(categories)
                published = r['published'].strftime("%Y-%m-%d") if r['published'] else "N/A"
                updated = r.get('updated')
                updated = updated.strftime("%Y-%m-%d") if updated else "N/A"
                pdf_url = r.get('pdf_url') or f"http://arxiv.org/pdf/{r['id']}"
                entry_id = f"http://arxiv.org/abs/{r['id']}"
                links = pdf_url + "||" + entry_id

                article_data = "\n".join([
                    f"Title: {r['title']}",
                    f"Authors: {authors}",
                    f"Published: {published}",
                    f"Updated: {updated}",
                    f"Primary Category: {r.get('primary_category', 'N/A')}",
                    f"All Categories: {all_categories}",
                    f"DOI: {r.get('doi') or 'N/A'}",
                    f"Journal Reference: {r.get('journal_ref') or 'N/A'}",
                    f"Comment: {r.get('comment') or 'N/A'}",
                    f"Entry ID: {entry_id}",
                    f"PDF URL: {pdf_url}",
                    f"All Links: {links}",
                    f"Summary: {r['abstract'] or ''}",
                ])
                formatted_results.append(article_data)
            return formatted_results
        finally:
            conn.close()
