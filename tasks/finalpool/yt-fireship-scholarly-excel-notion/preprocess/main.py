"""
Preprocess for yt-fireship-scholarly-excel-notion task.

Injects 18 academic papers into scholarly.arxiv_papers:
  - 2 papers for topic: AI and Large Language Models
  - 2 papers for topic: Linux and Systems
  - 2 papers for topic: Software Engineering
  - 2 papers for topic: Hardware and Computing
  - 2 papers for topic: Security
  - 3 noise papers on unrelated topics

YouTube data is read-only and pre-populated.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import os
import argparse
import json
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PAPERS = [
    # AI and Large Language Models
    {
        "arxiv_id": "2401.01001",
        "title": "Large Language Models for Automated Reasoning: A Comprehensive Survey",
        "authors": [{"name": "Yann Lecun"}, {"name": "Yoshua Bengio"}],
        "abstract": "We survey large language models (LLMs) with focus on automated reasoning capabilities. Recent models such as GPT-4 and DeepSeek R1 demonstrate remarkable reasoning abilities through chain-of-thought prompting and reinforcement learning from human feedback.",
        "categories": ["cs.AI", "cs.CL"],
        "primary_category": "cs.AI",
        "published": "2024-01-10",
        "citation_count": 892,
        "topic": "AI and Large Language Models",
    },
    {
        "arxiv_id": "2402.01002",
        "title": "DeepSeek R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
        "authors": [{"name": "DeepSeek Team"}],
        "abstract": "We introduce DeepSeek R1, a large language model trained using reinforcement learning to improve reasoning capability. The model achieves state-of-the-art performance on mathematical and coding benchmarks, demonstrating that reinforcement learning can effectively incentivize chain-of-thought reasoning.",
        "categories": ["cs.AI", "cs.CL"],
        "primary_category": "cs.AI",
        "published": "2024-02-15",
        "citation_count": 1204,
        "topic": "AI and Large Language Models",
    },
    # Linux and Systems
    {
        "arxiv_id": "2403.01003",
        "title": "Performance Analysis of Linux Kernel Scheduler Algorithms in Cloud Environments",
        "authors": [{"name": "Linus Torvalds"}, {"name": "Greg Kroah-Hartman"}],
        "abstract": "This paper analyzes the performance of Linux kernel scheduler algorithms across various cloud computing workloads. We evaluate CFS, EEVDF, and real-time schedulers on modern multi-core systems, providing insights into optimal configuration for containerized microservices.",
        "categories": ["cs.OS", "cs.PF"],
        "primary_category": "cs.OS",
        "published": "2024-03-05",
        "citation_count": 245,
        "topic": "Linux and Systems",
    },
    {
        "arxiv_id": "2404.01004",
        "title": "eBPF-Based Observability Tools for Linux System Performance Monitoring",
        "authors": [{"name": "Brendan Gregg"}],
        "abstract": "Extended Berkeley Packet Filter (eBPF) has revolutionized Linux observability by enabling safe in-kernel programmability. This paper presents a comprehensive review of eBPF-based tools including bpftrace and BCC for real-time performance monitoring and tracing.",
        "categories": ["cs.OS", "cs.NI"],
        "primary_category": "cs.OS",
        "published": "2024-04-12",
        "citation_count": 178,
        "topic": "Linux and Systems",
    },
    # Software Engineering
    {
        "arxiv_id": "2405.01005",
        "title": "Automated Detection and Classification of Software Bugs Using Deep Learning",
        "authors": [{"name": "Martin Fowler"}, {"name": "Kent Beck"}],
        "abstract": "We present a deep learning approach for automated detection and classification of software bugs in production codebases. Our model analyzes code patterns, stack traces, and historical bug reports to predict bug severity and suggest remediation strategies.",
        "categories": ["cs.SE", "cs.LG"],
        "primary_category": "cs.SE",
        "published": "2024-05-08",
        "citation_count": 312,
        "topic": "Software Engineering",
    },
    {
        "arxiv_id": "2406.01006",
        "title": "Root Cause Analysis in Distributed Systems: Patterns from Large-Scale Incidents",
        "authors": [{"name": "Charity Majors"}],
        "abstract": "This paper analyzes root cause patterns from thousands of production incidents in distributed systems. We identify common failure modes including cascading failures, thundering herds, and configuration drift, and propose systematic approaches to improve system resilience.",
        "categories": ["cs.SE", "cs.DC"],
        "primary_category": "cs.SE",
        "published": "2024-06-20",
        "citation_count": 189,
        "topic": "Software Engineering",
    },
    # Hardware and Computing
    {
        "arxiv_id": "2407.01007",
        "title": "Next-Generation Quantum-Classical Hybrid Computing Architectures",
        "authors": [{"name": "John Preskill"}, {"name": "Scott Aaronson"}],
        "abstract": "We examine emerging quantum-classical hybrid computing architectures that combine quantum processing units with classical CPUs and GPUs. These systems leverage quantum advantages for specific computational tasks while maintaining practical programmability through classical control.",
        "categories": ["cs.AR", "quant-ph"],
        "primary_category": "cs.AR",
        "published": "2024-07-14",
        "citation_count": 423,
        "topic": "Hardware and Computing",
    },
    {
        "arxiv_id": "2408.01008",
        "title": "Energy-Efficient Neural Processing Units: Design and Benchmarking",
        "authors": [{"name": "Bill Dally"}],
        "abstract": "This paper presents design principles and benchmarking results for energy-efficient neural processing units (NPUs). We analyze trade-offs between compute density, memory bandwidth, and power consumption for on-device AI inference in edge computing scenarios.",
        "categories": ["cs.AR", "cs.AI"],
        "primary_category": "cs.AR",
        "published": "2024-08-22",
        "citation_count": 267,
        "topic": "Hardware and Computing",
    },
    # Security
    {
        "arxiv_id": "2409.01009",
        "title": "Internet Archive Attacks: Analysis of Large-Scale DDoS and Data Breach Incidents",
        "authors": [{"name": "Bruce Schneier"}, {"name": "Dan Kaminsky"}],
        "abstract": "We analyze the 2024 attacks on digital preservation infrastructure including DDoS attacks and data breaches targeting web archiving services. Our analysis covers attack vectors, defender responses, and implications for the long-term preservation of internet history.",
        "categories": ["cs.CR", "cs.NI"],
        "primary_category": "cs.CR",
        "published": "2024-09-30",
        "citation_count": 156,
        "topic": "Security",
    },
    {
        "arxiv_id": "2410.01010",
        "title": "Supply Chain Security Vulnerabilities in Open Source Software: A Systematic Review",
        "authors": [{"name": "Ross Anderson"}],
        "abstract": "This systematic review examines supply chain security vulnerabilities in open source software ecosystems. We analyze 500 recent incidents including the XZ Utils backdoor, typosquatting attacks, and malicious package injections, proposing mitigation frameworks for maintainers and users.",
        "categories": ["cs.CR", "cs.SE"],
        "primary_category": "cs.CR",
        "published": "2024-10-05",
        "citation_count": 334,
        "topic": "Security",
    },
    # Noise papers on unrelated topics
    {
        "arxiv_id": "2411.01011",
        "title": "Transformer-Based Models for Medical Image Segmentation",
        "authors": [{"name": "Fei-Fei Li"}],
        "abstract": "We apply vision transformer architectures to medical image segmentation tasks including CT and MRI scan analysis. Our approach achieves state-of-the-art results on several benchmark datasets while maintaining interpretability through attention visualization.",
        "categories": ["cs.CV", "eess.IV"],
        "primary_category": "cs.CV",
        "published": "2024-11-10",
        "citation_count": 98,
        "topic": "Medical Imaging",
    },
    {
        "arxiv_id": "2412.01012",
        "title": "Climate Change Prediction Using Graph Neural Networks",
        "authors": [{"name": "Yoshua Bengio"}, {"name": "Amy Zhang"}],
        "abstract": "We present a graph neural network approach for climate change prediction that models atmospheric interactions as spatial graphs. The model integrates satellite observations, ocean temperature data, and atmospheric pressure readings for improved long-range weather forecasting.",
        "categories": ["cs.LG", "physics.ao-ph"],
        "primary_category": "cs.LG",
        "published": "2024-12-05",
        "citation_count": 67,
        "topic": "Climate Science",
    },
    {
        "arxiv_id": "2501.01013",
        "title": "Autonomous Drone Navigation Using Reinforcement Learning in Urban Environments",
        "authors": [{"name": "Pieter Abbeel"}],
        "abstract": "This paper presents a reinforcement learning framework for autonomous drone navigation in complex urban environments. The agent learns to avoid obstacles, comply with airspace regulations, and optimize flight paths through thousands of hours of simulation training before real-world deployment.",
        "categories": ["cs.RO", "cs.LG"],
        "primary_category": "cs.RO",
        "published": "2025-01-12",
        "citation_count": 43,
        "topic": "Robotics",
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared writable tables.")


def inject_scholarly_papers(conn):
    with conn.cursor() as cur:
        for p in PAPERS:
            cur.execute("""
                INSERT INTO scholarly.arxiv_papers
                (id, title, authors, abstract, categories, primary_category,
                 published, updated, pdf_url, html_url)
                VALUES (%s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    abstract = EXCLUDED.abstract
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]), p["primary_category"],
                p["published"], p["published"],
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into scholarly.arxiv_papers")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_scholarly_papers(conn)
        ensure_email_folder(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
