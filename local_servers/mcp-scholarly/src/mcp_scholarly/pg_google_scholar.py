import os
import psycopg2
import psycopg2.extras
from typing import List

MAX_RESULTS = 10


def _get_conn():
    return psycopg2.connect(
        host=os.environ.get('PG_HOST', 'localhost'),
        port=int(os.environ.get('PG_PORT', '5432')),
        dbname=os.environ.get('PG_DATABASE', 'toolathlon'),
        user=os.environ.get('PG_USER', 'postgres'),
        password=os.environ.get('PG_PASSWORD', 'postgres'),
    )


class GoogleScholar:
    def __init__(self):
        pass

    def search_pubs(self, keyword) -> List[str]:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, title, authors, abstract, pub_year, venue,
                           citation_count, url, eprint_url, pub_url, bib
                    FROM scholarly.scholar_papers
                    WHERE to_tsvector('english', coalesce(title,'') || ' ' || coalesce(abstract,''))
                          @@ plainto_tsquery('english', %s)
                    ORDER BY ts_rank(
                        to_tsvector('english', coalesce(title,'') || ' ' || coalesce(abstract,'')),
                        plainto_tsquery('english', %s)
                    ) DESC
                    LIMIT %s
                """, (keyword, keyword, MAX_RESULTS))
                rows = cur.fetchall()

            if not rows:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, authors, abstract, pub_year, venue,
                               citation_count, url, eprint_url, pub_url, bib
                        FROM scholarly.scholar_papers
                        WHERE title ILIKE %s OR abstract ILIKE %s
                        LIMIT %s
                    """, (f'%{keyword}%', f'%{keyword}%', MAX_RESULTS))
                    rows = cur.fetchall()

            articles = []
            for r in rows:
                authors = r['authors'] or []
                if isinstance(authors, list):
                    authors = ", ".join(str(a) for a in authors)

                article_string = "\n".join([
                    f"Title: {r['title']}",
                    f"Authors: {authors}",
                    f"Publication Year: {r.get('pub_year') or 'No year available'}",
                    f"Venue: {r.get('venue') or 'No venue available'}",
                    f"Google Scholar Rank: N/A",
                    f"Citations: {r.get('citation_count', 0)}",
                    f"Author IDs: No author IDs",
                    f"Publication URL: {r.get('pub_url') or r.get('url') or 'No URL available'}",
                    f"Cited-by URL: No cited-by URL",
                    f"Related Articles URL: No related articles URL",
                    f"Abstract: {r.get('abstract') or 'No abstract available'}",
                ])
                articles.append(article_string)
            return articles
        finally:
            conn.close()
