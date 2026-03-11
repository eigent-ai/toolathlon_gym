"""Preprocess script for yf-sector-scholarly-excel-word."""
import os
import argparse, json, os, sys, shutil, subprocess, time
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel"
}

TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_conn():
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)

def clear_writable_schemas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM scholarly.scholar_papers")
    cur.execute("DELETE FROM scholarly.arxiv_papers")
    conn.commit()
    cur.close()
    conn.close()

def inject_data(launch_time):
    conn = get_conn()
    cur = conn.cursor()
    launch_dt = datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S")
    # Inject scholarly papers (noise + relevant)
    cur.execute("""INSERT INTO scholarly.arxiv_papers (id, title, authors, abstract, categories, primary_category, pdf_url, published)
        VALUES ('2301.00001', 'LLM Reasoning Survey', '[{"name": "Author A"}]'::jsonb, 'A survey of reasoning methods in large language models.',
        '["cs.CL", "cs.AI"]'::jsonb, 'cs.CL', 'https://arxiv.org/pdf/2301.00001', '2023-01-15')""")
    cur.execute("""INSERT INTO scholarly.arxiv_papers (id, title, authors, abstract, categories, primary_category, pdf_url, published)
        VALUES ('2302.00002', 'Prompt Engineering Guide', '[{"name": "Author B"}]'::jsonb, 'A comprehensive guide to prompt engineering.',
        '["cs.AI"]'::jsonb, 'cs.AI', 'https://arxiv.org/pdf/2302.00002', '2023-02-20')""")
    cur.execute("""INSERT INTO scholarly.arxiv_papers (id, title, authors, abstract, categories, primary_category, pdf_url, published)
        VALUES ('2303.00003', 'In-Context Learning Theory', '[{"name": "Author C"}]'::jsonb, 'Theoretical foundations of in-context learning.',
        '["cs.LG"]'::jsonb, 'cs.LG', 'https://arxiv.org/pdf/2303.00003', '2023-03-10')""")
    # Noise papers
    cur.execute("""INSERT INTO scholarly.arxiv_papers (id, title, authors, abstract, categories, primary_category, pdf_url, published)
        VALUES ('2304.99901', 'Quantum Computing Basics', '[{"name": "Author D"}]'::jsonb, 'Introduction to quantum computing.',
        '["quant-ph"]'::jsonb, 'quant-ph', 'https://arxiv.org/pdf/2304.99901', '2023-04-01')""")
    cur.execute("""INSERT INTO scholarly.arxiv_papers (id, title, authors, abstract, categories, primary_category, pdf_url, published)
        VALUES ('2305.99902', 'Ocean Modeling Techniques', '[{"name": "Author E"}]'::jsonb, 'Advanced ocean modeling.',
        '["physics.ao-ph"]'::jsonb, 'physics.ao-ph', 'https://arxiv.org/pdf/2305.99902', '2023-05-15')""")
    conn.commit()
    cur.close()
    conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    clear_writable_schemas()
    inject_data(args.launch_time)

if __name__ == "__main__":
    main()