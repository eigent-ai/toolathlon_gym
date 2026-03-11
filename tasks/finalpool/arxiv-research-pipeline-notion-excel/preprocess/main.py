"""Preprocess script for arxiv-research-pipeline-notion-excel."""
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
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM scholarly.scholar_papers")
    cur.execute("DELETE FROM scholarly.arxiv_papers")
    cur.execute("DELETE FROM arxiv.papers")
    cur.execute("DELETE FROM arxiv_latex.papers")
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
    # Inject arxiv papers
    cur.execute("""INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
        VALUES ('2301.00001', 'LLM Reasoning Survey', '[{"name": "Author A"}]'::jsonb, 'A survey of reasoning methods in large language models.',
        '["cs.CL", "cs.AI"]'::jsonb, 'cs.CL', 'https://arxiv.org/pdf/2301.00001', '2023-01-15', true)""")
    cur.execute("""INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
        VALUES ('2302.00002', 'Prompt Engineering Guide', '[{"name": "Author B"}]'::jsonb, 'A comprehensive guide to prompt engineering.',
        '["cs.AI"]'::jsonb, 'cs.AI', 'https://arxiv.org/pdf/2302.00002', '2023-02-20', true)""")
    cur.execute("""INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
        VALUES ('2303.00003', 'In-Context Learning Theory', '[{"name": "Author C"}]'::jsonb, 'Theoretical foundations of in-context learning.',
        '["cs.LG"]'::jsonb, 'cs.LG', 'https://arxiv.org/pdf/2303.00003', '2023-03-10', true)""")
    # Noise
    cur.execute("""INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
        VALUES ('2399.00099', 'Unrelated Biology Paper', '[{"name": "Author Z"}]'::jsonb, 'A study on marine biology.',
        '["q-bio"]'::jsonb, 'q-bio', 'https://arxiv.org/pdf/2399.00099', '2023-06-01', false)""")
    # Inject arxiv-latex papers
    cur.execute("""INSERT INTO arxiv_latex.papers (id, title, abstract, full_prompt, sections)
        VALUES ('2301.00001', 'LLM Reasoning Survey', 'A survey of reasoning methods.',
        '\\documentclass{article}\n\\begin{document}\n\\title{LLM Reasoning Survey}\n\\end{document}',
        '[{"title": "Abstract", "content": "A survey of reasoning methods in LLMs."}, {"title": "1 Introduction", "content": "Large language models have shown remarkable capabilities."}, {"title": "2 Methods", "content": "We review chain-of-thought, tree of thoughts, and process supervision methods."}]'::jsonb)""")
    cur.execute("""INSERT INTO arxiv_latex.papers (id, title, abstract, full_prompt, sections)
        VALUES ('2302.00002', 'Prompt Engineering Guide', 'A comprehensive guide.',
        '\\documentclass{article}\n\\begin{document}\n\\title{Prompt Engineering}\n\\end{document}',
        '[{"title": "Abstract", "content": "A comprehensive guide to prompt engineering techniques."}, {"title": "1 Introduction", "content": "Prompt engineering is crucial for LLM performance."}]'::jsonb)""")
    # Noise notion data
    cur.execute("""INSERT INTO notion.pages (id, parent, properties, archived)
        VALUES ('noise-page-001',
        '{"type": "workspace", "workspace": true}'::jsonb,
        '{"title": {"id": "title", "type": "title", "title": [{"type": "text", "text": {"content": "Meeting Notes Archive"}}]}}'::jsonb,
        false)""")
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