import argparse
import json
import os
import uuid
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Clear writable schemas
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")

        # Inject 8 scholarly papers: 5 relevant bioinformatics/biochemistry, 3 noise

        papers = [
            (1001, "Protein Folding Dynamics in Enzyme Kinetics",
             json.dumps(["Sarah Chen", "John Smith"]),
             "This paper investigates protein folding mechanisms and their role in enzyme kinetics. "
             "We analyze biochemistry applications of molecular dynamics simulations to understand "
             "bioinformatics approaches for predicting protein structure and function in life sciences research.",
             2023, "Journal of Molecular Biology", 45, "https://example.com/paper1"),

            (1002, "Regulation of Gene Expression in Eukaryotic Systems",
             json.dumps(["James Okafor", "Li Wei"]),
             "We present a comprehensive study of gene expression regulation mechanisms. "
             "Our bioinformatics pipeline analyzes transcription factor binding and biochemistry "
             "of chromatin remodeling with practical applications in life sciences.",
             2023, "Nature Genetics", 82, "https://example.com/paper2"),

            (1003, "Novel Sequence Alignment Algorithms for Genomic Analysis",
             json.dumps(["Maria Gonzalez", "Ahmed Hassan"]),
             "This work introduces improved sequence alignment algorithms for bioinformatics applications. "
             "We demonstrate key concepts in computational biology with practical approaches "
             "to large-scale genomic data analysis in the life sciences domain.",
             2022, "Bioinformatics Journal", 63, "https://example.com/paper3"),

            (1004, "Machine Learning Approaches for Genomic Variant Classification",
             json.dumps(["Raj Patel", "Emily Davis"]),
             "We apply machine learning techniques to genomics data for variant classification. "
             "Our bioinformatics framework covers deep learning applications with practical "
             "implications for precision medicine and life sciences.",
             2023, "Genome Research", 55, "https://example.com/paper4"),

            (1005, "Integrative Bioinformatics for Drug Discovery",
             json.dumps(["Anna Park", "Carlos Rivera"]),
             "An integrative bioinformatics approach to biochemistry-driven drug discovery. "
             "This module covers key computational methods with practical applications "
             "in structural biology and life sciences research.",
             2022, "Drug Discovery Today", 38, "https://example.com/paper5"),

            # Noise papers
            (1006, "Macroeconomic Policy Impacts on Global Trade",
             json.dumps(["Robert Brown", "Karen White"]),
             "This paper examines how macroeconomic policies affect international trade flows. "
             "We analyze tariff structures and monetary policy using econometric models.",
             2023, "Journal of Economics", 30, "https://example.com/noise1"),

            (1007, "Renaissance Art and Cultural Identity in Florence",
             json.dumps(["Sophie Martin"]),
             "An exploration of Renaissance art movements in Florence and their impact on "
             "European cultural identity through painting and sculpture traditions.",
             2021, "Art History Review", 12, "https://example.com/noise2"),

            (1008, "Thermal Conductivity in Composite Materials",
             json.dumps(["David Kim", "Laura Chen"]),
             "We measure thermal conductivity properties of novel composite materials "
             "for aerospace engineering applications using finite element analysis.",
             2022, "Materials Science Journal", 25, "https://example.com/noise3"),
        ]

        for p in papers:
            cur.execute("""
                INSERT INTO scholarly.scholar_papers (id, title, authors, abstract, pub_year, venue, citation_count, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, p)

        # Inject noise emails
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        inbox_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s, false)
        """, (
            inbox_id, str(uuid.uuid4()),
            "Faculty Meeting Reminder",
            "admin@university.edu",
            json.dumps(["dean@university.edu"]),
            "Reminder: Faculty meeting scheduled for next Tuesday at 2pm."
        ))

        cur.execute("""
            INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s, false)
        """, (
            inbox_id, str(uuid.uuid4()),
            "Budget Review Q3",
            "finance@university.edu",
            json.dumps(["dean@university.edu"]),
            "Please review the Q3 budget report attached."
        ))

        conn.commit()
        print("Preprocess completed successfully.")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
