"""
Preprocess for scholarly-arxiv-cross-reference task.
- Inject specific papers into scholarly.arxiv_papers and arxiv.papers
- Clear email data so agent starts fresh
"""
import os
import argparse
import json

import psycopg2

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

SCHOLARLY_PAPERS = [
    {
        "id": "1602.05629",
        "title": "Communication-Efficient Learning of Deep Networks from Decentralized Data",
        "authors": [{"name": "H. Brendan McMahan"}, {"name": "Eider Moore"}, {"name": "Daniel Ramage"}],
        "published": "2016-02-17T00:00:00",
        "journal_ref": "AISTATS 2017",
        "summary": "Modern mobile devices have access to a wealth of data suitable for learning models. We propose federated learning, where the training data remains distributed on the mobile devices, and the devices collaboratively learn a shared model."
    },
    {
        "id": "1812.06127",
        "title": "Federated Optimization in Heterogeneous Networks",
        "authors": [{"name": "Tian Li"}, {"name": "Anit Kumar Sahu"}, {"name": "Manzil Zaheer"}],
        "published": "2018-12-14T00:00:00",
        "journal_ref": "MLSys 2020",
        "summary": "Federated learning is a distributed optimization paradigm that enables training on heterogeneous networks while keeping data local to each device."
    },
    {
        "id": "1908.07873",
        "title": "Federated Learning: Challenges, Methods, and Future Directions",
        "authors": [{"name": "Tian Li"}, {"name": "Anit Kumar Sahu"}, {"name": "Ameet Talwalkar"}],
        "published": "2019-08-21T00:00:00",
        "journal_ref": "IEEE Signal Processing Magazine 2020",
        "summary": "Federated learning involves training statistical models over remote devices or siloed data centers while keeping data localized."
    },
    {
        "id": "2001.08361",
        "title": "Scaling Laws for Neural Language Models",
        "authors": [{"name": "Jared Kaplan"}, {"name": "Sam McCandlish"}, {"name": "Tom Henighan"}],
        "published": "2020-01-23T00:00:00",
        "journal_ref": None,
        "summary": "We study empirical scaling laws for language model performance on the cross-entropy loss."
    },
    {
        "id": "2005.14165",
        "title": "Language Models are Few-Shot Learners",
        "authors": [{"name": "Tom B. Brown"}, {"name": "Benjamin Mann"}, {"name": "Nick Ryder"}],
        "published": "2020-05-28T00:00:00",
        "journal_ref": "NeurIPS 2020",
        "summary": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance."
    },
]

ARXIV_PAPERS = [
    {
        "id": "1602.05629",
        "title": "Communication-Efficient Learning of Deep Networks from Decentralized Data",
        "authors": [{"name": "H. Brendan McMahan"}, {"name": "Eider Moore"}, {"name": "Daniel Ramage"}],
        "published": "2016-02-17T00:00:00",
        "summary": "Modern mobile devices have access to a wealth of data suitable for learning models. We propose federated learning, where the training data remains distributed on the mobile devices, and the devices collaboratively learn a shared model.",
        "categories": ["cs.LG", "cs.DC"]
    },
    {
        "id": "1812.06127",
        "title": "Federated Optimization in Heterogeneous Networks",
        "authors": [{"name": "Tian Li"}, {"name": "Anit Kumar Sahu"}, {"name": "Manzil Zaheer"}],
        "published": "2018-12-14T00:00:00",
        "summary": "Federated learning is a distributed optimization paradigm that enables training on heterogeneous networks while keeping data local to each device.",
        "categories": ["cs.LG", "cs.DC"]
    },
    {
        "id": "1908.07873",
        "title": "Federated Learning: Challenges, Methods, and Future Directions",
        "authors": [{"name": "Tian Li"}, {"name": "Anit Kumar Sahu"}, {"name": "Ameet Talwalkar"}],
        "published": "2019-08-21T00:00:00",
        "summary": "Federated learning involves training statistical models over remote devices or siloed data centers while keeping data localized.",
        "categories": ["cs.LG", "stat.ML"]
    },
    {
        "id": "1207.00580",
        "title": "Improving Neural Networks by Preventing Co-adaptation of Feature Detectors",
        "authors": [{"name": "Geoffrey E. Hinton"}, {"name": "Nitish Srivastava"}, {"name": "Alex Krizhevsky"}],
        "published": "2012-07-03T00:00:00",
        "summary": "We describe a technique called dropout for addressing overfitting in neural networks.",
        "categories": ["cs.NE", "cs.LG"]
    },
    {
        "id": "1502.03167",
        "title": "Batch Normalization: Accelerating Deep Network Training",
        "authors": [{"name": "Sergey Ioffe"}, {"name": "Christian Szegedy"}],
        "published": "2015-02-11T00:00:00",
        "summary": "Training deep neural networks is complicated by the fact that the distribution of each layer's inputs changes during training. We propose batch normalization.",
        "categories": ["cs.LG"]
    },
    {
        "id": "1912.04977",
        "title": "Advances and Open Problems in Federated Learning",
        "authors": [{"name": "Peter Kairouz"}, {"name": "H. Brendan McMahan"}, {"name": "Brendan Avent"}],
        "published": "2019-12-10T00:00:00",
        "summary": "Federated learning is a machine learning setting where many clients collaboratively train a model under the orchestration of a central server.",
        "categories": ["cs.LG", "cs.CR"]
    },
]


def inject_papers(conn):
    """Clear and inject papers into both scholarly and arxiv schemas."""
    with conn.cursor() as cur:
        # Clear existing data
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM arxiv.papers")
        conn.commit()
        print("[preprocess] Cleared existing papers from both schemas")

        # Inject scholarly papers
        for p in SCHOLARLY_PAPERS:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers (id, title, authors, published, journal_ref, abstract)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title, authors = EXCLUDED.authors,
                    published = EXCLUDED.published, journal_ref = EXCLUDED.journal_ref,
                    abstract = EXCLUDED.abstract
            """, (p["id"], p["title"], json.dumps(p["authors"]),
                  p["published"], p["journal_ref"], p["summary"]))
        conn.commit()
        print(f"[preprocess] Injected {len(SCHOLARLY_PAPERS)} papers into scholarly.arxiv_papers")

        # Inject arxiv papers
        for p in ARXIV_PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers (id, title, authors, summary, published, categories)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title, authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary, published = EXCLUDED.published,
                    categories = EXCLUDED.categories
            """, (p["id"], p["title"], json.dumps(p["authors"]),
                  p["summary"], p["published"], json.dumps(p["categories"])))
        conn.commit()
        print(f"[preprocess] Injected {len(ARXIV_PAPERS)} papers into arxiv.papers")


def clear_email(conn):
    """Clear all email data."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM email.drafts")
    conn.commit()
    print("[preprocess] Cleared email data")


def verify_data(conn):
    """Verify both databases have papers."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM scholarly.arxiv_papers")
        scholarly_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM arxiv.papers")
        arxiv_count = cur.fetchone()[0]
        print(f"[preprocess] scholarly.arxiv_papers: {scholarly_count} papers")
        print(f"[preprocess] arxiv.papers: {arxiv_count} papers")

        # Check overlap
        cur.execute("""
            SELECT s.id FROM scholarly.arxiv_papers s
            INNER JOIN arxiv.papers a ON s.id = a.id
        """)
        overlap = cur.fetchall()
        print(f"[preprocess] Overlap: {len(overlap)} papers")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        inject_papers(conn)
        clear_email(conn)
        verify_data(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
