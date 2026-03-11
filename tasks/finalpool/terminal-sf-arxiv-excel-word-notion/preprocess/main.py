"""Preprocess for terminal-sf-arxiv-excel-word-notion.
Clears arxiv and notion schemas. Injects 5 arxiv papers (3 relevant + 2 noise).
Snowflake is read-only."""
import argparse
import json
import os
import uuid
import glob as globmod

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
        # Clear arxiv
        cur.execute("DELETE FROM arxiv.papers")
        print("[preprocess] Cleared arxiv data.")

        # Clear notion
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        print("[preprocess] Cleared notion data.")

        # Inject 5 arxiv papers: 3 relevant to employee retention, 2 noise
        papers = [
            {
                "id": "2301.04521",
                "title": "Predictive Models for Employee Turnover Using Machine Learning",
                "authors": json.dumps(["J. Smith", "A. Johnson", "K. Lee"]),
                "summary": "This paper presents a comprehensive study on using machine learning techniques to predict employee turnover. We evaluate random forest, gradient boosting, and neural network models on a dataset of 50,000 employees across multiple industries. Our results show that random forest models achieve 85% prediction accuracy using features including job satisfaction, performance ratings, tenure, and compensation. We find that job satisfaction combined with performance rating is the most predictive feature pair, particularly for identifying high-performing employees at risk of voluntary departure. The model provides actionable insights for HR departments to implement targeted retention interventions.",
                "categories": json.dumps(["cs.LG", "cs.AI"]),
                "primary_category": "cs.LG",
                "published": "2023-01-15T00:00:00+00:00",
                "updated": "2023-03-20T00:00:00+00:00",
            },
            {
                "id": "2302.08934",
                "title": "Intervention Programs for High-Performer Retention in Technology Firms",
                "authors": json.dumps(["M. Garcia", "L. Chen"]),
                "summary": "Employee retention of high performers is a critical challenge for technology firms. This study analyzes the effectiveness of various intervention programs across 120 technology companies over a five-year period. We find that targeted career development programs reduce high-performer attrition by 23%, while mentorship programs achieve a 15% reduction. Flexible work arrangements contribute an additional 12% reduction. Compensation adjustments alone show only an 8% improvement, suggesting that non-monetary factors play a dominant role. We propose a multi-factor retention framework that combines career development, mentorship, and work flexibility for optimal results.",
                "categories": json.dumps(["cs.CY", "cs.HC"]),
                "primary_category": "cs.CY",
                "published": "2023-02-20T00:00:00+00:00",
                "updated": "2023-04-10T00:00:00+00:00",
            },
            {
                "id": "2303.12456",
                "title": "The Role of Job Satisfaction in Voluntary Turnover: A Meta-Analysis",
                "authors": json.dumps(["R. Brown", "S. Patel", "T. Wilson"]),
                "summary": "This meta-analysis synthesizes findings from 187 studies spanning three decades of research on the relationship between job satisfaction and voluntary employee turnover. Our analysis confirms that job satisfaction is the strongest single predictor of voluntary turnover, with a weighted mean correlation of -0.58, stronger than compensation (r=-0.31), organizational commitment (r=-0.51), or job alternatives (r=0.29). We identify moderating factors including industry sector, organizational size, and economic conditions. For organizations with large workforces, we recommend systematic satisfaction monitoring combined with department-level intervention programs as the most cost-effective retention strategy.",
                "categories": json.dumps(["cs.CY", "stat.AP"]),
                "primary_category": "cs.CY",
                "published": "2023-03-25T00:00:00+00:00",
                "updated": "2023-05-15T00:00:00+00:00",
            },
            {
                "id": "2304.07891",
                "title": "Deep Reinforcement Learning for Autonomous Vehicle Navigation in Urban Environments",
                "authors": json.dumps(["X. Zhang", "Y. Wang"]),
                "summary": "We propose a novel deep reinforcement learning framework for autonomous vehicle navigation in complex urban environments. Our approach combines proximal policy optimization with a hierarchical attention mechanism to handle dynamic obstacles and traffic signals. Experiments on the CARLA simulator demonstrate that our method achieves a 94% success rate in navigating through dense urban traffic, outperforming previous state-of-the-art methods by 12%. We also introduce a safety constraint module that reduces collision rates by 67%.",
                "categories": json.dumps(["cs.RO", "cs.AI"]),
                "primary_category": "cs.RO",
                "published": "2023-04-18T00:00:00+00:00",
                "updated": "2023-04-18T00:00:00+00:00",
            },
            {
                "id": "2305.03210",
                "title": "Quantum Computing Applications in Protein Folding Simulation",
                "authors": json.dumps(["P. Kumar", "D. Nakamura", "F. Mueller"]),
                "summary": "This paper explores the application of variational quantum eigensolver algorithms to protein folding simulation problems. We demonstrate that current noisy intermediate-scale quantum computers can approximate folding energies for small peptide chains with accuracy comparable to classical density functional theory methods. Our hybrid quantum-classical approach reduces computational time by a factor of 3 for chains of up to 50 residues. We discuss the scalability limitations and propose error mitigation strategies for near-term quantum hardware.",
                "categories": json.dumps(["quant-ph", "q-bio.BM"]),
                "primary_category": "quant-ph",
                "published": "2023-05-10T00:00:00+00:00",
                "updated": "2023-06-01T00:00:00+00:00",
            },
        ]

        for p in papers:
            cur.execute("""
                INSERT INTO arxiv.papers (id, title, authors, summary, categories, primary_category, published, updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (p["id"], p["title"], p["authors"], p["summary"],
                  p["categories"], p["primary_category"], p["published"], p["updated"]))
        print("[preprocess] Injected 5 arxiv papers (3 relevant + 2 noise).")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up any leftover agent outputs
    if args.agent_workspace:
        for pattern in ["Retention_Strategy.xlsx", "Retention_Strategy_Report.docx",
                        "flight_risk_analysis.py", "flight_risk_analysis.json",
                        "synthesis.py", "synthesis.json"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
