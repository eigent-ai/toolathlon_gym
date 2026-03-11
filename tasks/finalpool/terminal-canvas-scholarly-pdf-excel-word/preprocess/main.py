"""Preprocess for terminal-canvas-scholarly-pdf-excel-word.
Canvas is read-only. Inject scholarly papers and noise data."""
import argparse
import glob
import json
import os
from datetime import datetime

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_scholarly(cur):
    print("[preprocess] Clearing scholarly data...")
    cur.execute("DELETE FROM scholarly.scholar_papers")


def inject_scholarly(cur):
    print("[preprocess] Injecting scholarly papers...")
    papers = [
        # Task-relevant papers
        ("A Survey of Machine Learning Approaches for Analytics",
         json.dumps([{"name": "J. Smith"}, {"name": "M. Chen"}]),
         "This comprehensive survey reviews machine learning methods used in applied analytics, "
         "covering supervised and unsupervised approaches for data-driven decision making.",
         2014, "Journal of Analytics Research", 120),
        ("Algorithm Design Patterns in Applied Data Science",
         json.dumps([{"name": "R. Patel"}, {"name": "S. Kumar"}]),
         "This paper presents common algorithm design patterns encountered in data science "
         "applications, including divide-and-conquer, dynamic programming, and greedy algorithms.",
         2013, "ACM Computing Surveys", 85),
        ("Teaching Analytics: Curriculum Design Principles",
         json.dumps([{"name": "L. Johnson"}, {"name": "A. Williams"}]),
         "A study of curriculum design principles for analytics education, examining how courses "
         "can better prepare students for data analysis roles in industry.",
         2015, "IEEE Education Conference", 45),
        ("Computational Thinking in Modern Algorithm Courses",
         json.dumps([{"name": "K. Brown"}, {"name": "T. Davis"}]),
         "Explores the integration of computational thinking frameworks into algorithm courses "
         "at the undergraduate and graduate level.",
         2014, "Computer Science Education", 62),
        ("Scalable Algorithms for Big Data Processing",
         json.dumps([{"name": "H. Wang"}, {"name": "D. Lee"}, {"name": "F. Zhang"}]),
         "Presents scalable algorithms for processing large datasets, focusing on MapReduce "
         "paradigm and distributed computing approaches.",
         2013, "Big Data Research", 95),
        ("Statistical Methods for Data-Driven Decision Making",
         json.dumps([{"name": "P. Anderson"}, {"name": "C. Taylor"}]),
         "Reviews statistical methods commonly used in data-driven analytics applications "
         "including regression analysis, hypothesis testing, and Bayesian methods.",
         2015, "Statistical Science", 38),
        ("Advances in Neural Network Optimization",
         json.dumps([{"name": "Y. Liu"}, {"name": "B. Martinez"}]),
         "Surveys recent advances in neural network optimization techniques including "
         "Adam, RMSProp, and learning rate scheduling strategies.",
         2014, "Neural Computing", 150),
        # Noise papers
        ("Marine Biology Population Dynamics",
         json.dumps([{"name": "O. Fisher"}, {"name": "N. Wave"}]),
         "Studies population dynamics of marine species in tropical ecosystems.",
         2013, "Marine Biology", 30),
        ("Archaeological Survey of Ancient Settlements",
         json.dumps([{"name": "A. Stone"}, {"name": "B. Dig"}]),
         "Comprehensive archaeological survey of settlement patterns in the Bronze Age.",
         2014, "Archaeology Journal", 15),
        ("Quantum Entanglement in Photonic Systems",
         json.dumps([{"name": "Q. Photon"}, {"name": "E. Laser"}]),
         "Experimental study of quantum entanglement properties in integrated photonic circuits.",
         2015, "Physical Review Letters", 200),
    ]

    for i, (title, authors, abstract, year, venue, citations) in enumerate(papers, 1):
        cur.execute("""
            INSERT INTO scholarly.scholar_papers
            (title, authors, abstract, pub_year, venue, citation_count)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, authors, abstract, year, venue, citations))

    print(f"[preprocess] Injected {len(papers)} scholarly papers (7 relevant + 3 noise)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_scholarly(cur)
        inject_scholarly(cur)
        conn.commit()
        print("[preprocess] DB setup done.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Curriculum_Research_Alignment.xlsx", "Curriculum_Review_Report.docx",
                        "alignment_*.py", "alignment_*.json", "assignments_*.json", "papers_*.json"]:
            for f in glob.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
