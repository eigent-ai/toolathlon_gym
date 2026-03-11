"""Preprocess for arxiv-reading-plan-excel-gcal-email.
Injects arxiv paper data and clears gcal, email schemas.
"""
import argparse
import json
import os
import shutil

import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}
TASK_ROOT = os.path.dirname(os.path.abspath(__file__))
INITIAL_WORKSPACE = os.path.join(TASK_ROOT, "..", "initial_workspace")

PAPERS = [
    ("2301.13379",
     "Large Language Models are not Zero-Shot Communicators",
     ["Abzaliev, Artur"],
     "This paper investigates zero-shot communication capabilities in large language models, finding that LLMs struggle with implicit pragmatic reasoning that humans handle naturally.",
     ["cs.CL"],
     "https://arxiv.org/pdf/2301.13379",
     "2023-01-31", "2023-01-31"),
    ("2302.01560",
     "Toolformer: Language Models Can Teach Themselves to Use Tools",
     ["Schick, T.", "Dwivedi-Yu, J.", "Dessi, R.", "Raileanu, R."],
     "We introduce Toolformer, a model trained to decide which APIs to call, when to call them, what arguments to pass, and how to best incorporate the results into future token prediction.",
     ["cs.CL", "cs.AI"],
     "https://arxiv.org/pdf/2302.01560",
     "2023-02-03", "2023-02-03"),
    ("2303.12528",
     "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face",
     ["Shen, Y.", "Song, K.", "Tan, X.", "Li, D."],
     "We propose HuggingGPT, a system that leverages LLMs like ChatGPT to connect various AI models in Hugging Face to solve AI tasks across language, vision, speech, and other modalities.",
     ["cs.CL", "cs.AI"],
     "https://arxiv.org/pdf/2303.12528",
     "2023-03-30", "2023-03-30"),
    ("2305.10403",
     "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
     ["Yao, S.", "Yu, D.", "Zhao, J.", "Shafran, I."],
     "We introduce Tree of Thoughts (ToT), a framework that allows LLMs to perform deliberate decision making by considering multiple different reasoning paths and evaluating choices to decide the next course of action.",
     ["cs.CL"],
     "https://arxiv.org/pdf/2305.10403",
     "2023-05-17", "2023-05-17"),
    ("2308.12950",
     "AgentBench: Evaluating LLMs as Agents",
     ["Liu, X.", "Yu, H.", "Zhang, H.", "Xu, Y."],
     "We present AgentBench, a comprehensive benchmark to evaluate LLM-as-Agent across 8 distinct environments covering web browsing, online shopping, database operations, and household tasks.",
     ["cs.CL", "cs.AI"],
     "https://arxiv.org/pdf/2308.12950",
     "2023-08-24", "2023-08-24"),
    ("2309.17453",
     "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
     ["Asai, A.", "Wu, Z.", "Wang, Y.", "Salehi, H."],
     "We introduce Self-RAG, a framework that trains an arbitrary language model to retrieve on demand and generate text informed by retrieved passages while critically reflecting on its own output.",
     ["cs.CL"],
     "https://arxiv.org/pdf/2309.17453",
     "2023-09-28", "2023-09-28"),
    ("2201.11903",
     "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
     ["Wei, J.", "Wang, X.", "Schuurmans, D.", "Bosma, M."],
     "We explore chain-of-thought prompting as a simple method to elicit multi-step reasoning capabilities in large language models. A chain of thought is a series of intermediate reasoning steps.",
     ["cs.CL", "cs.AI"],
     "https://arxiv.org/pdf/2201.11903",
     "2022-01-28", "2022-01-28"),
    ("2310.06825",
     "Mistral 7B",
     ["Jiang, A.", "Sablayrolles, A.", "Mensch, A.", "Bamford, C."],
     "We introduce Mistral 7B, a 7-billion-parameter language model engineered for superior performance and efficiency. Mistral 7B outperforms the best open 13B model on all evaluated benchmarks.",
     ["cs.CL"],
     "https://arxiv.org/pdf/2310.06825",
     "2023-10-10", "2023-10-10"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Clear writable schemas
    cur.execute("DELETE FROM arxiv.papers")
    cur.execute("DELETE FROM gcal.events")
    for table in ["sent_log", "messages", "folders"]:
        try:
            cur.execute(f'DELETE FROM email."{table}"')
        except Exception:
            conn.rollback()
    conn.commit()

    # Inject arxiv papers
    for (arxiv_id, title, authors, abstract, categories, pdf_url, published, updated) in PAPERS:
        cur.execute(
            """INSERT INTO arxiv.papers
               (id, title, authors, summary, categories, pdf_url, published, updated, is_downloaded)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO UPDATE SET
                 title=EXCLUDED.title, authors=EXCLUDED.authors, summary=EXCLUDED.summary,
                 categories=EXCLUDED.categories, pdf_url=EXCLUDED.pdf_url,
                 published=EXCLUDED.published, updated=EXCLUDED.updated""",
            (arxiv_id, title, json.dumps(authors), abstract,
             json.dumps(categories), pdf_url,
             published + "T00:00:00+00:00", updated + "T00:00:00+00:00", True)
        )
    conn.commit()
    print(f"Injected {len(PAPERS)} papers into arxiv.papers")

    # Insert default email folders
    cur.execute("INSERT INTO email.folders (name, flags) VALUES ('INBOX', '[\"\\\\HasNoChildren\"]') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO email.folders (name, flags) VALUES ('Sent', '[\"\\\\HasNoChildren\"]') ON CONFLICT DO NOTHING")
    conn.commit()

    cur.close()
    conn.close()

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
