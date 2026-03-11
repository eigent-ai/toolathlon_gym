"""
Preprocess for arxiv-federated-learning-notion task.
- Clears Notion data so the agent starts with a clean slate.
- Clears and injects federated learning papers into arxiv.papers.
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

FL_PAPERS = [
    {
        "id": "1602.05629",
        "title": "Communication-Efficient Learning of Deep Networks from Decentralized Data",
        "authors": [{"name": "H. Brendan McMahan"}, {"name": "Eider Moore"}, {"name": "Daniel Ramage"}, {"name": "Seth Hampson"}, {"name": "Blaise Agüera y Arcas"}],
        "summary": "Modern mobile devices have access to a wealth of data suitable for learning models, which in turn can greatly improve the user experience on the device. For example, language models can improve speech recognition and text entry, and image models can automatically select relevant photos. However, this rich data is often privacy sensitive, large in quantity, or both, which may preclude logging to the data center and training there using conventional approaches. We advocate an alternative that leaves the training data distributed on the mobile devices, and learns a shared model by aggregating locally-computed updates. We term this decentralized approach Federated Learning. We present a practical method for the federated learning of deep networks based on iterative model averaging, and conduct an extensive empirical evaluation, considering five different model architectures and four datasets. These experiments demonstrate the approach is robust to the unbalanced and non-IID data distributions that are a defining characteristic of this setting. Communication costs are the principal constraint, and we show a reduction in required communication rounds by 10-100x as compared to synchronized stochastic gradient descent.",
        "published": "2016-02-17T00:00:00+00:00",
        "categories": ["cs.LG", "cs.AI", "cs.DC"],
    },
    {
        "id": "1812.06127",
        "title": "Federated Optimization in Heterogeneous Networks",
        "authors": [{"name": "Tian Li"}, {"name": "Anit Kumar Sahu"}, {"name": "Manzil Zaheer"}, {"name": "Maziar Sanjabi"}, {"name": "Ameet Talwalkar"}, {"name": "Virginia Smith"}],
        "summary": "Federated Learning is a distributed machine learning paradigm that enables model training on a large corpus of decentralized data. Federated learning systems face significant challenges in dealing with heterogeneity in the network. In this work, we tackle the heterogeneity in federated networks by proposing FedProx, a re-parametrization of FedAvg which adds a proximal term to the local subproblem. We provide convergence guarantees for FedProx under heterogeneous data and systems, and we demonstrate that it leads to more robust and fair convergence behavior relative to FedAvg across a suite of federated datasets. We further use our theory to motivate a framework for systematically understanding the trade-offs in federated optimization.",
        "published": "2018-12-14T00:00:00+00:00",
        "categories": ["cs.LG", "cs.DC", "math.OC", "stat.ML"],
    },
    {
        "id": "1908.07873",
        "title": "Federated Learning: Challenges, Methods, and Future Directions",
        "authors": [{"name": "Tian Li"}, {"name": "Anit Kumar Sahu"}, {"name": "Ameet Talwalkar"}, {"name": "Virginia Smith"}],
        "summary": "Federated learning involves training statistical models over remote devices or siloed data centers, such as mobile phones or hospitals, while keeping data localized. Training in heterogeneous and potentially massive networks introduces novel challenges that require rethinking of the tools in distributed optimization, systems design, and statistical learning. In this article, we discuss the unique characteristics and challenges of federated learning, provide a broad overview of current approaches, and outline several directions of future work that are relevant to a range of research communities.",
        "published": "2019-08-21T00:00:00+00:00",
        "categories": ["cs.LG", "cs.AI", "cs.CR", "cs.DC", "stat.ML"],
    },
    {
        "id": "1912.04977",
        "title": "Advances and Open Problems in Federated Learning",
        "authors": [{"name": "Peter Kairouz"}, {"name": "H. Brendan McMahan"}, {"name": "Brendan Avent"}, {"name": "Aurélien Bellet"}, {"name": "Mehdi Bennis"}],
        "summary": "Federated learning (FL) is a machine learning setting where many clients (e.g., mobile devices or whole organizations) collaboratively train a model under the orchestration of a central server (e.g., service provider), while keeping the training data decentralized. FL embodies the principles of focused data collection and minimization, and can mitigate many of the systemic privacy risks and costs resulting from traditional, centralized machine learning and data science approaches. Motivated by the explosive growth in FL research, this paper discusses recent advances and presents an extensive collection of open problems and challenges.",
        "published": "2019-12-10T00:00:00+00:00",
        "categories": ["cs.LG", "cs.AI", "cs.CR", "cs.DC", "stat.ML"],
    },
]


def clear_notion(conn):
    """Clear all Notion data."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
    conn.commit()
    print("[preprocess] Cleared Notion data")


def inject_arxiv_papers(conn):
    """Clear and inject federated learning papers into arxiv.papers."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM arxiv.papers")
        for p in FL_PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers (id, title, authors, summary, published, categories)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                p["id"],
                p["title"],
                json.dumps(p["authors"]),
                p["summary"],
                p["published"],
                json.dumps(p["categories"]),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(FL_PAPERS)} FL papers into arxiv.papers")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_notion(conn)
        inject_arxiv_papers(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
