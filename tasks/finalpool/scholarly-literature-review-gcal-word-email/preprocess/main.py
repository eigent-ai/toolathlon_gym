"""Preprocess for scholarly-literature-review-gcal-word-email.
Injects scholarly paper data and clears gcal, email schemas.
"""
import argparse
import os
import shutil

import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}
TASK_ROOT = os.path.dirname(os.path.abspath(__file__))
INITIAL_WORKSPACE = os.path.join(TASK_ROOT, "..", "initial_workspace")

PAPERS = [
    ("Attention Is All You Need",
     ["Vaswani, A.", "Shazeer, N.", "Parmar, N.", "Uszkoreit, J."],
     2017, 86000,
     "We propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output.",
     "https://arxiv.org/abs/1706.03762"),
    ("BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
     ["Devlin, J.", "Chang, M. W.", "Lee, K.", "Toutanova, K."],
     2019, 62000,
     "We introduce BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations.",
     "https://arxiv.org/abs/1810.04805"),
    ("A Survey of Deep Learning",
     ["LeCun, Y.", "Bengio, Y.", "Hinton, G."],
     2015, 55000,
     "Overview of deep learning techniques and their applications to various domains including vision, speech, and natural language processing.",
     "https://doi.org/10.1038/nature14539"),
    ("Language Models are Few-Shot Learners",
     ["Brown, T.", "Mann, B.", "Ryder, N.", "Subbiah, M."],
     2020, 42000,
     "We describe GPT-3, an autoregressive language model with 175 billion parameters. GPT-3 achieves strong performance on many NLP datasets including translation, question-answering, and cloze tasks.",
     "https://arxiv.org/abs/2005.14165"),
    ("Training language models to follow instructions with human feedback",
     ["Ouyang, L.", "Wu, J.", "Jiang, X.", "Almeida, D."],
     2022, 18000,
     "We train language models to follow instructions with human feedback using reinforcement learning from human feedback (RLHF). This results in models that are more helpful and less harmful.",
     "https://arxiv.org/abs/2203.02155"),
    ("LLaMA: Open and Efficient Foundation Language Models",
     ["Touvron, H.", "Lavril, T.", "Gautier, I.", "Lacroix, T."],
     2023, 15000,
     "We introduce LLaMA, a collection of foundation language models ranging from 7B to 65B parameters. Our models match or outperform GPT-3 on most benchmarks while being trained only on publicly available data.",
     "https://arxiv.org/abs/2302.13971"),
    ("Scaling Laws for Neural Language Models",
     ["Kaplan, J.", "McCandlish, S.", "Henighan, T.", "Brown, T."],
     2020, 8500,
     "We study empirical scaling laws for language model performance on the cross-entropy loss. Performance has a power-law relationship with each of: model size, dataset size, and compute used for training.",
     "https://arxiv.org/abs/2001.08361"),
    ("ImageNet Classification with Deep Convolutional Neural Networks",
     ["Krizhevsky, A.", "Sutskever, I.", "Hinton, G."],
     2012, 92000,
     "We trained a large deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 different classes.",
     "https://papers.nips.cc/paper/2012"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    import json
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Clear writable schemas
    cur.execute("DELETE FROM scholarly.scholar_papers")
    cur.execute("DELETE FROM scholarly.arxiv_papers")
    for table in ["comments", "blocks", "pages", "databases"]:
        cur.execute(f"DELETE FROM notion.{table}")
    cur.execute("DELETE FROM gcal.events")
    for table in ["sent_log", "messages", "folders"]:
        try:
            cur.execute(f'DELETE FROM email."{table}"')
        except Exception:
            conn.rollback()
    conn.commit()

    # Inject scholar papers
    for title, authors, year, citations, abstract, url in PAPERS:
        cur.execute(
            """INSERT INTO scholarly.scholar_papers
               (title, authors, pub_year, citation_count, abstract, url)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (title, json.dumps(authors), year, citations, abstract, url)
        )
    conn.commit()
    print(f"Injected {len(PAPERS)} papers into scholarly.scholar_papers")

    # Insert default email folders
    cur.execute("INSERT INTO email.folders (name, flags) VALUES ('INBOX', '[\"\\\\HasNoChildren\"]') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO email.folders (name, flags) VALUES ('Sent', '[\"\\\\HasNoChildren\"]') ON CONFLICT DO NOTHING")
    conn.commit()

    cur.close()
    conn.close()
    print("Cleared schemas: scholarly, gcal, email.")

    # Copy initial_workspace files
    if args.agent_workspace:
        initial_ws = os.path.abspath(INITIAL_WORKSPACE)
        agent_ws = args.agent_workspace
        os.makedirs(agent_ws, exist_ok=True)
        if os.path.exists(initial_ws):
            for fname in os.listdir(initial_ws):
                src = os.path.join(initial_ws, fname)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(agent_ws, fname))
            print(f"Copied initial workspace files to {agent_ws}")

    print("Preprocess complete.")


if __name__ == "__main__":
    main()
