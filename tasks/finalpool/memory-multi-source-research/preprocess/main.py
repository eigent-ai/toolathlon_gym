"""
Preprocess for memory-multi-source-research task.

Clears and injects papers about AI safety into scholarly tables.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import os
import argparse
import asyncio
import json

import psycopg2

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

TARGET_PAPERS = [
    {
        "arxiv_id": "1606.06565",
        "title": "Concrete Problems in AI Safety",
        "authors": [{"name": "Dario Amodei"}, {"name": "Chris Olah"}, {"name": "Jacob Steinhardt"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "Rapid progress in machine learning and artificial intelligence has brought increasing "
            "attention to the potential impacts of AI technologies on society. In this paper we discuss "
            "one such potential impact: the problem of accidents in machine learning systems, defined "
            "as unintended and harmful behavior that may emerge from poor design of real-world AI "
            "systems. We present a list of five practical research problems related to accident risk, "
            "categorized according to whether the problem originates from having the wrong objective "
            "function, an objective function that is too expensive to evaluate frequently, or "
            "undesirable behavior during the learning process. We review previous work in these areas "
            "and suggest concrete research directions."
        ),
        "published": "2016-06-21",
        "pub_year": 2016,
        "venue": "arXiv",
        "citation_count": 3000,
    },
    {
        "arxiv_id": "1805.00899",
        "title": "AI Safety via Debate",
        "authors": [{"name": "Geoffrey Irving"}, {"name": "Paul Christiano"}, {"name": "Dario Amodei"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "To make AI systems broadly useful for challenging real-world tasks, we need them to learn "
            "complex human goals and preferences. One approach to specifying complex goals asks humans "
            "to judge during training which agent behaviors are safe and useful, but this approach can "
            "fail if the task is too complicated for a human to judge directly. To help address this, "
            "we propose training agents via self play on a debate game. Given a question or proposed "
            "action, two agents take turns making short statements up to a set length, then a human "
            "judges which of the agents gave the most accurate and useful information."
        ),
        "published": "2018-05-02",
        "pub_year": 2018,
        "venue": "arXiv",
        "citation_count": 500,
    },
    {
        "arxiv_id": "1906.01820",
        "title": "Risks from Learned Optimization in Advanced Machine Learning Systems",
        "authors": [{"name": "Evan Hubinger"}, {"name": "Chris van Merwijk"}, {"name": "Vladimir Mikulik"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "We analyze the type of learned optimization that occurs when a learned model, such as a "
            "neural network, is itself an optimizer -- a situation we refer to as mesa-optimization. "
            "We believe that the possibility of mesa-optimization raises novel safety concerns for "
            "the alignment community. In particular, we identify a new risk we call deceptive "
            "alignment, in which a mesa-optimizer may learn to behave as if it is aligned with the "
            "base objective during training while actually pursuing a different objective, deceiving "
            "the training process to avoid being modified."
        ),
        "published": "2019-06-05",
        "pub_year": 2019,
        "venue": "arXiv",
        "citation_count": 400,
    },
    {
        "arxiv_id": "2209.00626",
        "title": "Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned",
        "authors": [{"name": "Deep Ganguli"}, {"name": "Liane Lovitt"}, {"name": "Jackson Kernion"}],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We describe our early efforts to red team language models in order to simultaneously "
            "discover, measure, and attempt to reduce their potentially harmful outputs. We make "
            "three main contributions. First, we investigate scaling behaviors for red teaming across "
            "3 model sizes and 4 model types. Second, we release our dataset of 38,961 red team "
            "attacks for others to analyze and learn from. Third, we exhaustively describe our "
            "instructions, processes, statistical methodologies, and uncertainty about red teaming. "
            "We find that the models are increasingly difficult to red team as they become more "
            "helpful and that the most successful red team attacks tend to be more creative."
        ),
        "published": "2022-09-01",
        "pub_year": 2022,
        "venue": "arXiv",
        "citation_count": 800,
    },
    {
        "arxiv_id": "2112.00861",
        "title": "Alignment of Language Agents via Reward Modeling with Human Feedback",
        "authors": [{"name": "Jan Leike"}, {"name": "David Krueger"}, {"name": "Tom Everitt"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "We present a framework for aligning language model agents with human intentions using "
            "reward models trained on human feedback. Our approach involves three stages: collecting "
            "human preference comparisons, training a reward model to predict human preferences, and "
            "optimizing the language model policy against the reward model using reinforcement learning. "
            "We demonstrate that this approach can significantly improve the safety and helpfulness "
            "of language models, reducing harmful outputs while maintaining or improving task performance. "
            "We discuss the implications for scalable alignment of increasingly capable AI systems."
        ),
        "published": "2021-12-02",
        "pub_year": 2021,
        "venue": "arXiv",
        "citation_count": 1200,
    },
    {
        "arxiv_id": "2305.15324",
        "title": "Scalable Oversight of AI Systems via Recursive Reward Modeling",
        "authors": [{"name": "Paul Christiano"}, {"name": "Buck Shlegeris"}, {"name": "Dario Amodei"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "As AI systems become more capable, it becomes increasingly important to develop scalable "
            "methods for ensuring that their behavior aligns with human values. We propose recursive "
            "reward modeling as a technique for scalable oversight, where AI assistants help humans "
            "evaluate AI behavior in domains that are too complex for unaided human judgment. We "
            "provide theoretical arguments for why this approach may succeed and present preliminary "
            "experimental results. We discuss the relationship between our approach and other "
            "proposals for AI safety including debate, amplification, and market-based approaches."
        ),
        "published": "2023-05-24",
        "pub_year": 2023,
        "venue": "arXiv",
        "citation_count": 350,
    },
]

NOISE_PAPERS = [
    {
        "arxiv_id": "1506.00019",
        "title": "Deep Learning",
        "authors": [{"name": "Yann LeCun"}, {"name": "Yoshua Bengio"}, {"name": "Geoffrey Hinton"}],
        "categories": ["cs.LG", "cs.AI"],
        "primary_category": "cs.LG",
        "abstract": (
            "Deep learning allows computational models that are composed of multiple processing layers "
            "to learn representations of data with multiple levels of abstraction. These methods have "
            "dramatically improved the state-of-the-art in speech recognition, visual object recognition, "
            "object detection and many other domains such as drug discovery and genomics. Deep learning "
            "discovers intricate structure in large data sets by using the backpropagation algorithm to "
            "indicate how a machine should change its internal parameters that are used to compute the "
            "representation in each layer from the representation in the previous layer."
        ),
        "published": "2015-06-01",
        "pub_year": 2015,
        "venue": "Nature",
        "citation_count": 50000,
    },
    {
        "arxiv_id": "1706.03762",
        "title": "Attention Is All You Need",
        "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}, {"name": "Niki Parmar"}],
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "abstract": (
            "The dominant sequence transduction models are based on complex recurrent or convolutional "
            "neural networks that include an encoder and a decoder. The best performing models also "
            "connect the encoder and decoder through an attention mechanism. We propose a new simple "
            "network architecture, the Transformer, based solely on attention mechanisms, dispensing "
            "with recurrence and convolutions entirely. Experiments on two machine translation tasks "
            "show these models to be superior in quality while being more parallelizable and requiring "
            "significantly less time to train."
        ),
        "published": "2017-06-12",
        "pub_year": 2017,
        "venue": "NeurIPS",
        "citation_count": 90000,
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
    conn.commit()
    print("Cleared scholarly tables")


def inject_scholarly_arxiv(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                (id, title, authors, abstract, categories, primary_category,
                 published, updated, doi, journal_ref, pdf_url, html_url, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    abstract = EXCLUDED.abstract,
                    categories = EXCLUDED.categories,
                    primary_category = EXCLUDED.primary_category,
                    published = EXCLUDED.published
            """, (
                p["arxiv_id"],
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                json.dumps(p["categories"]),
                p["primary_category"],
                p["published"],
                p["published"],
                None,
                p.get("venue"),
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                None,
            ))
    conn.commit()
    print(f"Injected {len(papers)} papers into scholarly.arxiv_papers")


def inject_scholarly_scholar(conn, papers):
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.scholar_papers
                (title, authors, abstract, pub_year, venue, citation_count,
                 url, eprint_url, pub_url, bib)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                p["pub_year"],
                p.get("venue"),
                p.get("citation_count", 0),
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                json.dumps({"title": p["title"], "year": p["pub_year"]}),
            ))
    conn.commit()
    print(f"Injected {len(papers)} papers into scholarly.scholar_papers")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_tables(conn)
        all_papers = TARGET_PAPERS + NOISE_PAPERS
        inject_scholarly_arxiv(conn, all_papers)
        inject_scholarly_scholar(conn, all_papers)
    finally:
        conn.close()

    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
