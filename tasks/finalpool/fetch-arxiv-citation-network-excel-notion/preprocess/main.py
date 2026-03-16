"""Preprocess script for fetch-arxiv-citation-network-excel-notion."""
import os
import argparse, json, os, sys, shutil, tarfile, subprocess, time
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": int(os.environ.get("PGPORT", "5432")),
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

    cur.execute("DELETE FROM arxiv.papers")

    cur.execute("DELETE FROM scholarly.scholar_papers")
    cur.execute("DELETE FROM scholarly.arxiv_papers")
    conn.commit()
    cur.close()
    conn.close()

def inject_data(launch_time):
    conn = get_conn()
    cur = conn.cursor()
    launch_dt = datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S")
    
    cur.execute("""INSERT INTO notion.pages (id, parent, properties, archived, in_trash, url) VALUES
        ('noise-arxiv_citation-001', '{"type": "workspace", "workspace": true}'::jsonb,
         '{"title": {"id": "title", "type": "title", "title": [{"type": "text", "text": {"content": "Old Project Notes"}}]}}'::jsonb,
         false, false, 'https://notion.so/old-notes')""")

    # Inject papers
    cur.execute("""INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded) VALUES
        ('2301.01234', 'Scaling Laws for Large Language Models', '[{"name": "J. Kaplan"}]'::jsonb,
         'We study empirical scaling laws for language model performance.', '["cs.CL"]'::jsonb, 'cs.CL',
         'https://arxiv.org/pdf/2301.01234', '2023-01-15', true),
        ('2302.05678', 'Advances in Vision Transformers', '[{"name": "A. Dosovitskiy"}]'::jsonb,
         'We survey recent advances in vision transformer architectures.', '["cs.CV"]'::jsonb, 'cs.CV',
         'https://arxiv.org/pdf/2302.05678', '2023-02-20', true),
        ('2303.09012', 'Multi-Agent Reinforcement Learning Framework', '[{"name": "M. Lanctot"}]'::jsonb,
         'We propose a new framework for multi-agent reinforcement learning.', '["cs.AI"]'::jsonb, 'cs.AI',
         'https://arxiv.org/pdf/2303.09012', '2023-03-10', true),
        ('2304.03456', 'Federated Learning: A Comprehensive Survey', '[{"name": "Q. Yang"}]'::jsonb,
         'This paper provides a comprehensive survey of federated learning.', '["cs.LG"]'::jsonb, 'cs.LG',
         'https://arxiv.org/pdf/2304.03456', '2023-04-05', true),
        ('9999.99999', 'Noise Paper on Unrelated Topic', '[{"name": "N. Oise"}]'::jsonb,
         'This paper discusses quantum computing applications in biology.', '["quant-ph"]'::jsonb, 'quant-ph',
         'https://arxiv.org/pdf/9999.99999', '2023-05-01', true)""")

    cur.execute("""INSERT INTO scholarly.arxiv_papers (id, title, authors, abstract, categories, primary_category, pdf_url, published) VALUES
        ('2301.01234', 'Scaling Laws for Large Language Models', '[{"name": "J. Kaplan"}]'::jsonb,
         'We study empirical scaling laws.', '["cs.CL"]'::jsonb, 'cs.CL', 'https://arxiv.org/pdf/2301.01234', '2023-01-15'),
        ('2302.05678', 'Advances in Vision Transformers', '[{"name": "A. Dosovitskiy"}]'::jsonb,
         'We survey vision transformers.', '["cs.CV"]'::jsonb, 'cs.CV', 'https://arxiv.org/pdf/2302.05678', '2023-02-20')""")
    conn.commit()
    cur.close()
    conn.close()


def setup_mock_server(port=30322):
    files_dir = os.path.join(TASK_ROOT, "files")
    tmp_dir = os.path.join(TASK_ROOT, "tmp")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    # Kill existing process on port
    try:
        subprocess.run(f"kill -9 $(lsof -ti:30322) 2>/dev/null", shell=True, timeout=5)
    except Exception:
        pass
    time.sleep(0.5)

    # Extract mock pages
    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)

    # Start HTTP server
    mock_dir = os.path.join(tmp_dir, "mock_pages")
    if os.path.exists(mock_dir):
        log_path = os.path.join(mock_dir, "server.log")
        subprocess.Popen(
            f"nohup python3 -m http.server 30322 --directory {mock_dir} > {log_path} 2>&1 &",
            shell=True
        )
        time.sleep(1)
        print(f"Mock server started on port 30322")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False, default="2026-03-07 10:00:00")
    args = parser.parse_args()

    clear_writable_schemas()
    inject_data(args.launch_time)
    setup_mock_server(30322)

if __name__ == "__main__":
    main()
