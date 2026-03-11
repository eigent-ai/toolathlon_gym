"""
Preprocess for yt-fireship-scholarly-ppt-gsheet-email task.

Clears and injects:
- 5 papers into scholarly.arxiv_papers and scholarly.scholar_papers
- 2 emails (from research@ai-group.org and team@lab.edu)
- Clears gsheet tables

NOTE: youtube schema is READ-ONLY. This preprocess does NOT touch youtube.videos
or youtube.channels. The task uses the existing Fireship channel data in the DB.
"""
import argparse
import json
import os
import uuid
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

ARXIV_PAPERS = [
    {
        "id": "1706.03762",
        "title": "Attention Is All You Need",
        "authors": json.dumps([{"name": "Vaswani"}, {"name": "Shazeer"}, {"name": "Parmar"}]),
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
        "categories": json.dumps(["cs.LG", "cs.CL"]),
        "primary_category": "cs.LG",
        "pdf_url": "https://arxiv.org/pdf/1706.03762",
        "published": "2017-06-12",
    },
    {
        "id": "1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": json.dumps([{"name": "Devlin"}, {"name": "Chang"}, {"name": "Lee"}]),
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional representations.",
        "categories": json.dumps(["cs.CL"]),
        "primary_category": "cs.CL",
        "pdf_url": "https://arxiv.org/pdf/1810.04805",
        "published": "2018-10-11",
    },
    {
        "id": "2303.08774",
        "title": "GPT-4 Technical Report",
        "authors": json.dumps([{"name": "OpenAI"}]),
        "abstract": "We report the development of GPT-4, a large-scale multimodal model which can accept image and text inputs and produce text outputs. GPT-4 exhibits human-level performance on various professional and academic benchmarks.",
        "categories": json.dumps(["cs.AI", "cs.CL"]),
        "primary_category": "cs.AI",
        "pdf_url": "https://arxiv.org/pdf/2303.08774",
        "published": "2023-03-15",
    },
    {
        "id": "2212.08073",
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "authors": json.dumps([{"name": "Bai"}, {"name": "Jones"}, {"name": "Ndousse"}]),
        "abstract": "As AI systems become more capable, we would like to enlist their help to supervise other AIs. We experiment with methods for training a harmless AI assistant through self-improvement, without any human labels identifying harmful outputs.",
        "categories": json.dumps(["cs.AI"]),
        "primary_category": "cs.AI",
        "pdf_url": "https://arxiv.org/pdf/2212.08073",
        "published": "2022-12-15",
    },
    {
        "id": "2307.09288",
        "title": "Llama 2: Open Foundation and Fine-Tuned Chat Models",
        "authors": json.dumps([{"name": "Touvron"}, {"name": "Martin"}, {"name": "Stone"}]),
        "abstract": "We develop and release Llama 2, a collection of pretrained and fine-tuned large language models ranging in scale from 7 billion to 70 billion parameters. Our fine-tuned Llama 2-Chat models are optimized for dialogue use cases.",
        "categories": json.dumps(["cs.CL"]),
        "primary_category": "cs.CL",
        "pdf_url": "https://arxiv.org/pdf/2307.09288",
        "published": "2023-07-18",
    },
]

SCHOLAR_PAPERS = [
    {
        "title": "Attention Is All You Need",
        "authors": json.dumps([{"name": "Vaswani"}, {"name": "Shazeer"}, {"name": "Parmar"}]),
        "abstract": "We propose the Transformer architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "pub_year": 2017,
        "venue": "NeurIPS",
        "citation_count": 85000,
        "url": "https://arxiv.org/abs/1706.03762",
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": json.dumps([{"name": "Devlin"}, {"name": "Chang"}, {"name": "Lee"}]),
        "abstract": "We introduce BERT, a new language representation model pre-trained on large text corpora.",
        "pub_year": 2018,
        "venue": "NAACL",
        "citation_count": 52000,
        "url": "https://arxiv.org/abs/1810.04805",
    },
    {
        "title": "GPT-4 Technical Report",
        "authors": json.dumps([{"name": "OpenAI"}]),
        "abstract": "GPT-4 is a large-scale multimodal model demonstrating human-level performance on professional benchmarks.",
        "pub_year": 2023,
        "venue": "arXiv",
        "citation_count": 8000,
        "url": "https://arxiv.org/abs/2303.08774",
    },
    {
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "authors": json.dumps([{"name": "Bai"}, {"name": "Jones"}]),
        "abstract": "We train a harmless AI assistant through self-improvement using constitutional AI principles.",
        "pub_year": 2022,
        "venue": "arXiv",
        "citation_count": 2100,
        "url": "https://arxiv.org/abs/2212.08073",
    },
    {
        "title": "Llama 2: Open Foundation and Fine-Tuned Chat Models",
        "authors": json.dumps([{"name": "Touvron"}, {"name": "Martin"}]),
        "abstract": "We develop Llama 2, a collection of open-source large language models optimized for dialogue.",
        "pub_year": 2023,
        "venue": "arXiv",
        "citation_count": 15000,
        "url": "https://arxiv.org/abs/2307.09288",
    },
]

EMAILS = [
    {
        "subject": "AI Trend Analysis Request - Research Group",
        "from_addr": "research@ai-group.org",
        "to_addr": json.dumps(["researcher@lab.edu"]),
        "body": (
            "Hello,\n\n"
            "Our research group is planning a quarterly technology briefing and we would like "
            "to commission an overview of the current AI and machine learning landscape. "
            "We are particularly interested in understanding which topics are trending in "
            "both the popular tech media space and the academic literature.\n\n"
            "Could you prepare a presentation covering the main AI technologies, "
            "with references to both video content from key tech educators and "
            "peer-reviewed papers? Please also set up a shared spreadsheet so the whole team "
            "can access and contribute to the findings.\n\n"
            "Best regards,\nresearch@ai-group.org"
        ),
    },
    {
        "subject": "Literature Review for Lab Meeting",
        "from_addr": "team@lab.edu",
        "to_addr": json.dumps(["researcher@lab.edu"]),
        "body": (
            "Hi,\n\n"
            "Could you put together a literature review on large language models and "
            "transformer architectures for our next lab meeting? It would be helpful to "
            "have both a structured spreadsheet with the key papers and citation counts, "
            "and a short presentation we can walk through together.\n\n"
            "Feel free to also include any relevant content from tech explainer channels "
            "to help contextualize the academic work for newer lab members.\n\n"
            "Thanks,\nteam@lab.edu"
        ),
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM email.attachments")
        try:
            cur.execute("DELETE FROM email.sent_log")
        except Exception:
            pass
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
    conn.commit()
    print("[preprocess] Cleared email, gsheet, scholarly tables.")


def get_or_create_inbox(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
        conn.commit()
        return cur.fetchone()[0]


def inject_scholarly(conn):
    with conn.cursor() as cur:
        for p in ARXIV_PAPERS:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                    (id, title, authors, abstract, categories, primary_category, pdf_url, published)
                VALUES (%s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s::date)
                ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title
            """, (
                p["id"], p["title"], p["authors"], p["abstract"],
                p["categories"], p["primary_category"], p["pdf_url"], p["published"],
            ))
        for p in SCHOLAR_PAPERS:
            cur.execute("""
                INSERT INTO scholarly.scholar_papers
                    (title, authors, abstract, pub_year, venue, citation_count, url)
                VALUES (%s, %s::jsonb, %s, %s, %s, %s, %s)
            """, (
                p["title"], p["authors"], p["abstract"],
                p["pub_year"], p["venue"], p["citation_count"], p["url"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(ARXIV_PAPERS)} arxiv papers and {len(SCHOLAR_PAPERS)} scholar papers.")


def inject_emails(conn, folder_id):
    with conn.cursor() as cur:
        for em in EMAILS:
            cur.execute("""
                INSERT INTO email.messages
                    (folder_id, message_id, subject, from_addr, to_addr, date, body_text)
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), %s)
            """, (
                folder_id,
                str(uuid.uuid4()),
                em["subject"], em["from_addr"], em["to_addr"], em["body"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(EMAILS)} emails.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_scholarly(conn)
        folder_id = get_or_create_inbox(conn)
        inject_emails(conn, folder_id)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
