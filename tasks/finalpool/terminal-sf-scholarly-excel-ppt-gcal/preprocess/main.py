"""Preprocess for terminal-sf-scholarly-excel-ppt-gcal.
Clears scholarly and gcal schemas. Injects 6 papers (4 relevant + 2 noise) and calendar conflicts."""
import argparse
import glob as globmod
import json
import os
import uuid
from datetime import datetime, timedelta

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
        # Clear scholarly and gcal
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM gcal.events")
        conn.commit()
        print("[preprocess] Cleared scholarly and gcal data.")

        # Inject 6 scholarly papers (4 relevant + 2 noise)
        papers = [
            # Relevant paper 1
            {
                "title": "Optimizing Regional Sales Performance Through Data-Driven Territory Management",
                "authors": json.dumps([{"name": "J. Anderson"}, {"name": "M. Brooks"}]),
                "abstract": "This study examines how data-driven territory management strategies can optimize regional sales performance. Through analysis of 200 sales organizations, we find that systematic territory rebalancing based on market potential data leads to 15-20% revenue improvement in underperforming regions. Key factors include customer density optimization, workload balancing across sales representatives, and alignment of territory boundaries with market opportunity. Our framework provides actionable recommendations for sales leaders seeking to improve regional performance through evidence-based territory design.",
                "pub_year": 2024,
                "venue": "Journal of Sales Management",
                "citation_count": 45,
            },
            # Relevant paper 2
            {
                "title": "Customer Segmentation Strategies for B2B Sales Growth",
                "authors": json.dumps([{"name": "R. Patel"}, {"name": "S. Kim"}]),
                "abstract": "We present a comprehensive framework for customer segmentation in B2B sales environments. Our research demonstrates that tiered engagement models based on customer lifetime value analysis improve customer retention rates by 25% and increase average deal sizes by 18%. The study analyzes segmentation approaches across Consumer, Enterprise, Government, and SMB segments, providing specific strategies for each tier. Results show that personalized engagement strategies aligned with segment characteristics yield the highest ROI in sales optimization efforts.",
                "pub_year": 2023,
                "venue": "Harvard Business Review Analytics",
                "citation_count": 78,
            },
            # Relevant paper 3
            {
                "title": "Dynamic Pricing and Discount Optimization in Enterprise Sales",
                "authors": json.dumps([{"name": "L. Zhang"}, {"name": "K. Mueller"}]),
                "abstract": "This paper investigates the impact of dynamic pricing and optimized discount structures on enterprise sales revenue. Analysis of 150 companies reveals that structured discount frameworks reduce revenue leakage by 8-12% in price-sensitive markets. We propose an algorithmic approach to discount optimization that considers customer segment, deal size, competitive landscape, and regional market conditions. The findings are particularly relevant for organizations operating in emerging markets where price sensitivity significantly affects sales outcomes.",
                "pub_year": 2024,
                "venue": "Management Science",
                "citation_count": 32,
            },
            # Relevant paper 4
            {
                "title": "The Impact of Sales Team Specialization on Regional Performance",
                "authors": json.dumps([{"name": "A. Fernandez"}, {"name": "D. Wilson"}]),
                "abstract": "We study the effects of sales team specialization versus generalist approaches on regional sales performance. Our longitudinal study of 80 multinational companies shows that specialized sales teams outperform generalist teams by 18% in emerging markets and 12% in mature markets. Specialization by vertical industry, product line, or customer size tier all show positive effects. The research provides a practical framework for sales leaders to determine optimal specialization strategies based on market maturity, product complexity, and customer segmentation patterns.",
                "pub_year": 2023,
                "venue": "Journal of Marketing Research",
                "citation_count": 56,
            },
            # Noise paper 1 - healthcare
            {
                "title": "Machine Learning Applications in Clinical Trial Optimization",
                "authors": json.dumps([{"name": "H. Nakamura"}, {"name": "P. Garcia"}]),
                "abstract": "This paper presents a novel machine learning framework for optimizing clinical trial design and patient recruitment. Using deep learning models trained on electronic health records, we achieve a 30% improvement in patient matching accuracy for Phase III clinical trials. Our approach combines natural language processing of medical literature with structured patient data to identify optimal trial sites and recruitment strategies. The methodology has been validated across 15 therapeutic areas including oncology, cardiology, and neurology.",
                "pub_year": 2024,
                "venue": "Nature Medicine AI",
                "citation_count": 120,
            },
            # Noise paper 2 - pure ML theory
            {
                "title": "Convergence Analysis of Federated Learning with Non-IID Data Distributions",
                "authors": json.dumps([{"name": "Y. Wang"}, {"name": "T. Brown"}]),
                "abstract": "We provide theoretical convergence guarantees for federated learning algorithms under non-identically distributed data across participating nodes. Our analysis extends previous work by establishing tight bounds on the convergence rate of FedAvg and FedProx under heterogeneous data settings. We introduce a novel variance reduction technique that achieves linear speedup with the number of participating clients while maintaining differential privacy guarantees. Experimental results on standard benchmarks confirm our theoretical predictions.",
                "pub_year": 2025,
                "venue": "International Conference on Machine Learning",
                "citation_count": 89,
            },
        ]

        for i, paper in enumerate(papers):
            cur.execute("""
                INSERT INTO scholarly.scholar_papers (id, title, authors, abstract, pub_year, venue, citation_count, url, eprint_url, pub_url, bib)
                VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """, (
                i + 1,
                paper["title"],
                paper["authors"],
                paper["abstract"],
                paper["pub_year"],
                paper["venue"],
                paper["citation_count"],
                f"https://scholar.example.com/paper/{i+1}",
                f"https://scholar.example.com/paper/{i+1}/pdf",
                f"https://scholar.example.com/paper/{i+1}/pub",
                json.dumps({"entry_type": "article", "fields": {"title": paper["title"], "year": str(paper["pub_year"])}}),
            ))

        # Inject calendar conflicts (busy slots in next 2 weeks from launch_time)
        lt = datetime.strptime(args.launch_time or "2026-03-07 10:00:00", "%Y-%m-%d %H:%M:%S")
        def ts(days, hours, minutes=0):
            return (lt + timedelta(days=days, hours=hours - 10, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        conflict_events = [
            ("Team Standup", ts(2, 9), ts(2, 9, 30), "Daily standup"),
            ("Product Roadmap Review", ts(2, 10), ts(2, 12), "Quarterly product review"),
            ("Board Prep Meeting", ts(3, 9), ts(3, 11), "Board presentation prep"),
            ("Lunch with Investors", ts(3, 12), ts(3, 13, 30), "Investor relations lunch"),
            ("Engineering Sync", ts(4, 9), ts(4, 10, 30), "Cross-team sync"),
            ("Marketing Campaign Review", ts(4, 14), ts(4, 15, 30), "Q1 campaign review"),
            ("All Hands Meeting", ts(5, 9), ts(5, 10), "Company all-hands"),
            ("Customer Success Review", ts(5, 10, 30), ts(5, 12), "Monthly CS review"),
            ("Finance Review", ts(6, 9), ts(6, 11), "Monthly finance review"),
            ("Team Building Event", ts(6, 13), ts(6, 17), "Quarterly team event"),
            ("Sprint Planning", ts(9, 9), ts(9, 10, 30), "Sprint planning session"),
            ("Vendor Meeting", ts(9, 11), ts(9, 12), "Vendor contract discussion"),
            ("Training Session", ts(10, 9), ts(10, 12), "Sales tools training"),
            ("1:1 with CEO", ts(10, 14), ts(10, 15), "Monthly check-in"),
        ]
        for summary, start, end, desc in conflict_events:
            cur.execute("""
                INSERT INTO gcal.events (id, summary, description, start_datetime, end_datetime, status)
                VALUES (%s, %s, %s, %s, %s, 'confirmed')
            """, (str(uuid.uuid4()), summary, desc, start, end))

        conn.commit()
        print("[preprocess] Injected 6 scholarly papers and 14 calendar conflicts.")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up agent workspace
    if args.agent_workspace:
        for pattern in ["Sales_Strategy_Analysis.xlsx", "Sales_Strategy_Presentation.pptx",
                        "analyze_sales_gaps.py", "match_recommendations.py", "generate_summary.py",
                        "sales_gaps.json", "research_recommendations.json", "executive_summary.txt"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
