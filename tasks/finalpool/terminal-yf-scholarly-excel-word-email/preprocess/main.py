"""Preprocess for terminal-yf-scholarly-excel-word-email.
Injects scholarly papers. Clears email. YF is read-only."""
import argparse
import glob as globmod
import json
import os
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear email data
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.drafts")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.messages")
        conn.commit()
        print("[preprocess] Cleared email data.")

        # Clear scholarly data
        cur.execute("DELETE FROM scholarly.scholar_papers")
        conn.commit()
        print("[preprocess] Cleared scholarly papers.")

        # Inject relevant scholarly papers
        papers = [
            {
                "title": "Efficient Capital Markets: A Review of Theory and Empirical Work",
                "authors": json.dumps(["Eugene Fama"]),
                "abstract": "This paper reviews the theoretical and empirical literature on the efficient "
                           "markets hypothesis, classifying the work into three categories: weak-form, "
                           "semi-strong form, and strong-form tests of market efficiency.",
                "pub_year": 1970,
                "venue": "Journal of Finance",
                "citation_count": 15000,
            },
            {
                "title": "Random Walks in Stock Market Prices",
                "authors": json.dumps(["Eugene Fama"]),
                "abstract": "An examination of the random walk model and its implications for stock "
                           "market price behavior. The paper provides empirical evidence that stock "
                           "prices follow approximately a random walk.",
                "pub_year": 1965,
                "venue": "Financial Analysts Journal",
                "citation_count": 8500,
            },
            {
                "title": "Algorithmic Trading and Market Quality",
                "authors": json.dumps(["Terrence Hendershott", "Charles Jones", "Albert Menkveld"]),
                "abstract": "This study examines the impact of algorithmic trading on market quality "
                           "including liquidity, price discovery, and volatility. Results suggest "
                           "algorithmic trading improves market efficiency.",
                "pub_year": 2011,
                "venue": "Journal of Finance",
                "citation_count": 3200,
            },
            {
                "title": "Market Efficiency in the Age of Big Data",
                "authors": json.dumps(["David Easley", "Marcos Lopez de Prado", "Maureen O'Hara"]),
                "abstract": "Reviews how modern data analytics, machine learning, and alternative data "
                           "sources affect the efficient market hypothesis and price discovery mechanisms.",
                "pub_year": 2021,
                "venue": "Journal of Financial Economics",
                "citation_count": 850,
            },
        ]

        # Noise papers
        noise_papers = [
            {
                "title": "Deep Learning for Natural Language Processing: A Survey",
                "authors": json.dumps(["Various Authors"]),
                "abstract": "Survey of deep learning techniques applied to NLP tasks.",
                "pub_year": 2020,
                "venue": "ACL",
                "citation_count": 500,
            },
            {
                "title": "Climate Change and Agricultural Productivity",
                "authors": json.dumps(["Smith et al."]),
                "abstract": "Analysis of climate change impacts on crop yields.",
                "pub_year": 2019,
                "venue": "Nature",
                "citation_count": 300,
            },
            {
                "title": "Quantum Computing Applications in Cryptography",
                "authors": json.dumps(["Chen et al."]),
                "abstract": "Overview of quantum computing applications in modern cryptography.",
                "pub_year": 2022,
                "venue": "IEEE",
                "citation_count": 200,
            },
        ]

        for i, paper in enumerate(papers + noise_papers):
            cur.execute("""
                INSERT INTO scholarly.scholar_papers (id, title, authors, abstract, pub_year, venue, citation_count)
                VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s)
            """, (i + 1, paper["title"], paper["authors"], paper["abstract"],
                  paper["pub_year"], paper["venue"], paper["citation_count"]))

        conn.commit()
        print(f"[preprocess] Injected {len(papers)} relevant + {len(noise_papers)} noise scholarly papers.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up agent workspace
    if args.agent_workspace:
        for pattern in ["FinTech_Research_Report.xlsx", "FinTech_Research_Report.docx", "market_analysis.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
