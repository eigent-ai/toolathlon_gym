"""Preprocess for terminal-arxiv-yf-excel-word-notion-email.
Clears arxiv, notion, email schemas. Injects 6 papers (4 relevant + 2 noise) into arxiv.
Injects noise notion and email data.
"""
import argparse
import json
import os
import uuid
from datetime import datetime

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
          user="eigent", password="camel")

# 4 relevant papers (AI + finance)
RELEVANT_PAPERS = [
    {
        "id": "2306.06031",
        "title": "FinGPT: Large Language Models for Financial Applications",
        "authors": [{"name": "Hongyang Yang"}, {"name": "Xiao-Yang Liu"}, {"name": "Christina Dan Wang"}],
        "summary": "Large language models (LLMs) have shown remarkable capabilities in various NLP tasks. This paper presents FinGPT, an open-source framework for financial large language models. FinGPT provides accessible tools for financial sentiment analysis, stock movement prediction, and automated financial report generation using state-of-the-art language models.",
        "categories": ["cs.CL", "q-fin.ST"],
        "primary_category": "cs.CL",
        "published": "2023-06-09",
        "pdf_url": "https://arxiv.org/pdf/2306.06031"
    },
    {
        "id": "2304.07619",
        "title": "Can Large Language Models Predict Stock Price Movements?",
        "authors": [{"name": "Qianqian Chen"}, {"name": "Yuwei Li"}, {"name": "Feng Zhang"}],
        "summary": "This paper investigates whether large language models such as ChatGPT can predict stock price movements. We design experiments using financial news headlines and evaluate LLM zero-shot and few-shot prediction performance. Results show that LLMs achieve promising accuracy in predicting stock direction, outperforming traditional sentiment analysis approaches.",
        "categories": ["q-fin.ST", "cs.CL"],
        "primary_category": "q-fin.ST",
        "published": "2023-04-15",
        "pdf_url": "https://arxiv.org/pdf/2304.07619"
    },
    {
        "id": "2302.14040",
        "title": "Deep Learning for Financial Risk Prediction",
        "authors": [{"name": "Rajesh Kumar"}, {"name": "Priya Patel"}, {"name": "Amit Singh"}],
        "summary": "We propose a deep learning framework for credit risk assessment and financial risk prediction. Our model combines recurrent neural networks with attention mechanisms to process sequential financial data. Experiments on banking datasets show significant improvements over traditional statistical models in predicting loan defaults and credit risk scores.",
        "categories": ["q-fin.RM", "cs.LG"],
        "primary_category": "q-fin.RM",
        "published": "2023-02-27",
        "pdf_url": "https://arxiv.org/pdf/2302.14040"
    },
    {
        "id": "2311.10723",
        "title": "Machine Learning in Quantitative Finance: Applications and Challenges",
        "authors": [{"name": "Carlos Martinez"}, {"name": "Wei Zhao"}, {"name": "David Brown"}],
        "summary": "This comprehensive survey reviews machine learning applications in quantitative finance, covering algorithmic trading, portfolio optimization, risk management, and market microstructure analysis. We examine how deep learning, reinforcement learning, and natural language processing are transforming financial decision-making and discuss challenges including data quality, interpretability, and regulatory compliance.",
        "categories": ["q-fin.CP", "cs.LG"],
        "primary_category": "q-fin.CP",
        "published": "2023-11-17",
        "pdf_url": "https://arxiv.org/pdf/2311.10723"
    },
]

# 2 noise papers (not finance-related)
NOISE_PAPERS = [
    {
        "id": "2305.18290",
        "title": "Drag Your GAN: Interactive Point-based Manipulation on the Generative Image Manifold",
        "authors": [{"name": "Xingang Pan"}, {"name": "Ayush Tewari"}, {"name": "Thomas Leimkuhler"}],
        "summary": "We present DragGAN, an approach that allows users to interactively drag image content to precise target positions. This technique enables realistic image manipulation by moving points on the generative image manifold.",
        "categories": ["cs.CV", "cs.GR"],
        "primary_category": "cs.CV",
        "published": "2023-05-25",
        "pdf_url": "https://arxiv.org/pdf/2305.18290"
    },
    {
        "id": "2307.09288",
        "title": "Llama 2: Open Foundation and Fine-Tuned Chat Models",
        "authors": [{"name": "Hugo Touvron"}, {"name": "Louis Martin"}, {"name": "Kevin Stone"}],
        "summary": "We develop and release Llama 2, a collection of pretrained and fine-tuned large language models ranging from 7B to 70B parameters. Our fine-tuned models, called Llama 2-Chat, are optimized for dialogue use cases and outperform most open-source chat models on helpfulness and safety benchmarks.",
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "published": "2023-07-18",
        "pdf_url": "https://arxiv.org/pdf/2307.09288"
    },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        # Clear schemas
        cur.execute("DELETE FROM arxiv.papers")
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        conn.commit()
        print("[preprocess] Cleared arxiv, notion, email schemas.")

        # Inject arxiv papers (4 relevant + 2 noise)
        all_papers = RELEVANT_PAPERS + NOISE_PAPERS
        for p in all_papers:
            cur.execute("""
                INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, published, pdf_url, is_downloaded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title, authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary, categories = EXCLUDED.categories,
                    primary_category = EXCLUDED.primary_category,
                    published = EXCLUDED.published, pdf_url = EXCLUDED.pdf_url
            """, (p["id"], p["title"], json.dumps(p["authors"]),
                  p["summary"], json.dumps(p["categories"]),
                  p["primary_category"], p["published"], p["pdf_url"]))
        conn.commit()
        print(f"[preprocess] Injected {len(all_papers)} papers into arxiv.papers")

        # Inject noise notion data
        noise_db_id = str(uuid.uuid4())
        noise_title = json.dumps([{"type": "text", "text": {"content": "Sprint Backlog"}, "plain_text": "Sprint Backlog"}])
        cur.execute(
            "INSERT INTO notion.databases (id, title, properties) VALUES (%s, %s, %s)",
            (noise_db_id, noise_title, json.dumps({"Name": {"title": {}}, "Status": {"select": {}}}))
        )
        for i in range(3):
            cur.execute(
                "INSERT INTO notion.pages (id, parent, properties) VALUES (%s, %s, %s)",
                (str(uuid.uuid4()), json.dumps({"database_id": noise_db_id}),
                 json.dumps({"title": {"title": [{"text": {"content": f"Task {i+1}"}, "plain_text": f"Task {i+1}"}]}}))
            )
        conn.commit()
        print("[preprocess] Injected noise notion data.")

        # Inject noise email data
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if row:
            inbox_id = row[0]
        else:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            inbox_id = cur.fetchone()[0]
            cur.execute("INSERT INTO email.folders (name) VALUES ('Sent')")
            cur.execute("INSERT INTO email.folders (name) VALUES ('Drafts')")
            conn.commit()

        noise_emails = [
            ("Meeting reminder: Q4 planning", "admin@firm.com", "team@firm.com", "Please join the Q4 planning meeting tomorrow at 2pm."),
            ("Lunch order for Friday", "social@firm.com", "office@firm.com", "Please submit your lunch orders by Thursday EOD."),
        ]
        for subj, from_a, to_a, body in noise_emails:
            cur.execute("""
                INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s, false)
            """, (inbox_id, str(uuid.uuid4()), subj, from_a, json.dumps([to_a]), body))
        conn.commit()
        print("[preprocess] Injected noise email data.")

        # Verify
        cur.execute("SELECT COUNT(*) FROM arxiv.papers")
        print(f"[preprocess] arxiv.papers: {cur.fetchone()[0]} papers")
        cur.execute("SELECT COUNT(*) FROM notion.databases")
        print(f"[preprocess] notion.databases: {cur.fetchone()[0]} databases")
        cur.execute("SELECT COUNT(*) FROM email.messages")
        print(f"[preprocess] email.messages: {cur.fetchone()[0]} messages")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
