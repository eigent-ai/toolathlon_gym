"""
Preprocess for yt-veritasium-scholarly-notion-excel task.

Injects 15 academic papers (3 per topic matching top 5 Veritasium video topics) into scholarly.arxiv_papers.
Clears notion pages with matching title.
YouTube data is READ-ONLY.
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

NOTION_PAGE_TITLE = "Science Video-Paper Resource Map"

# Papers related to top 5 Veritasium video topics
# Top 5 Veritasium by views:
# 1. How One Company Secretly Poisoned The Planet (environmental pollution)
# 2. Can you keep zooming in forever? (fractals/infinity/microscopy)
# 3. How a Student's Question Saved This NYC Skyscraper (structural engineering)
# 4. Something Strange Happens When You Trust Quantum Mechanics (quantum mechanics)
# 5. The Closest We've Come to a Theory of Everything (theoretical physics)

PAPERS = [
    # Topic 1: environmental pollution
    {
        "arxiv_id": "2301.11001",
        "title": "Environmental Impact of Industrial Pollutants: A Systematic Review",
        "authors": [{"name": "James K. Porter"}, {"name": "Maria E. Santos"}],
        "abstract": "We review the environmental and health impacts of industrial chemical pollutants released into ecosystems over the past century. Studies demonstrate the long-term persistence of organochlorine compounds and their bioaccumulation effects.",
        "categories": ["q-bio.PE", "physics.soc-ph"],
        "primary_category": "q-bio.PE",
        "published": "2023-01-15",
        "citation_count": 210,
        "topic": "environmental pollution",
    },
    {
        "arxiv_id": "2301.11002",
        "title": "Atmospheric Dispersion of Toxic Chemicals from Industrial Sources",
        "authors": [{"name": "Chen Wei"}, {"name": "Sarah Johnson"}],
        "abstract": "This paper models the atmospheric dispersion of toxic chemical pollutants from industrial facilities, providing improved estimates of regional contamination footprints.",
        "categories": ["physics.ao-ph"],
        "primary_category": "physics.ao-ph",
        "published": "2023-02-10",
        "citation_count": 145,
        "topic": "environmental pollution",
    },
    {
        "arxiv_id": "2301.11003",
        "title": "Long-term Health Effects of Chemical Pollution Exposure",
        "authors": [{"name": "Robert A. Miller"}],
        "abstract": "Epidemiological study of populations exposed to industrial chemical pollution, documenting elevated cancer risk and neurological impacts across three decades of follow-up.",
        "categories": ["q-bio.QM"],
        "primary_category": "q-bio.QM",
        "published": "2023-03-05",
        "citation_count": 189,
        "topic": "environmental pollution",
    },
    # Topic 2: fractals and infinity
    {
        "arxiv_id": "2302.22001",
        "title": "Fractal Geometry in Natural Structures: Mathematical Foundations",
        "authors": [{"name": "Lisa M. Chen"}],
        "abstract": "A mathematical analysis of fractal self-similarity in natural phenomena including coastlines, snowflakes, and cellular structures. We examine the Hausdorff dimension across diverse natural systems.",
        "categories": ["math.DS", "math-ph"],
        "primary_category": "math.DS",
        "published": "2023-04-12",
        "citation_count": 98,
        "topic": "fractals and infinity",
    },
    {
        "arxiv_id": "2302.22002",
        "title": "Infinite Series and Convergence in Optical Microscopy Systems",
        "authors": [{"name": "David Park"}, {"name": "Anna Kovacs"}],
        "abstract": "We explore the mathematical limits of optical magnification systems using infinite series theory and analyze theoretical resolution bounds for light microscopy.",
        "categories": ["physics.optics", "math.FA"],
        "primary_category": "physics.optics",
        "published": "2023-05-08",
        "citation_count": 67,
        "topic": "fractals and infinity",
    },
    {
        "arxiv_id": "2302.22003",
        "title": "Mandelbrot Set Properties and Computational Exploration",
        "authors": [{"name": "Pierre Dubois"}, {"name": "Yu Zhang"}],
        "abstract": "Computational study of the Mandelbrot set boundary and its infinite complexity. We present algorithms for efficient deep zoom rendering and analyze statistical properties of boundary regions.",
        "categories": ["math.DS", "cs.CG"],
        "primary_category": "math.DS",
        "published": "2023-06-20",
        "citation_count": 54,
        "topic": "fractals and infinity",
    },
    # Topic 3: structural engineering
    {
        "arxiv_id": "2303.33001",
        "title": "Resonance Failures in Tall Building Design: Historical Case Studies",
        "authors": [{"name": "Thomas A. Hughes"}, {"name": "Nina Patel"}],
        "abstract": "We analyze historical structural failures in tall buildings caused by resonance and wind-induced vibration, deriving lessons for modern engineering practice.",
        "categories": ["physics.app-ph", "cond-mat.mtrl-sci"],
        "primary_category": "physics.app-ph",
        "published": "2023-02-28",
        "citation_count": 134,
        "topic": "structural engineering",
    },
    {
        "arxiv_id": "2303.33002",
        "title": "Wind Load Analysis for High-Rise Building Structures",
        "authors": [{"name": "Carlos Rodriguez"}],
        "abstract": "Modern computational fluid dynamics applied to wind load estimation for high-rise buildings. We demonstrate how student-discovered structural vulnerabilities led to improved design codes.",
        "categories": ["physics.flu-dyn"],
        "primary_category": "physics.flu-dyn",
        "published": "2023-03-15",
        "citation_count": 112,
        "topic": "structural engineering",
    },
    {
        "arxiv_id": "2303.33003",
        "title": "Tuned Mass Dampers in Earthquake and Wind Mitigation for Skyscrapers",
        "authors": [{"name": "Kenji Tanaka"}, {"name": "Sophie Laurent"}],
        "abstract": "Review of tuned mass damper technology deployed in iconic skyscrapers worldwide, with performance data from major seismic and wind events.",
        "categories": ["physics.app-ph"],
        "primary_category": "physics.app-ph",
        "published": "2023-07-10",
        "citation_count": 88,
        "topic": "structural engineering",
    },
    # Topic 4: quantum mechanics
    {
        "arxiv_id": "2304.44001",
        "title": "Quantum Superposition and Measurement: Foundational Experiments",
        "authors": [{"name": "Elena Novak"}, {"name": "Marcus Webb"}],
        "abstract": "A review of foundational quantum mechanics experiments demonstrating superposition, entanglement, and wave-particle duality, with analysis of philosophical implications.",
        "categories": ["quant-ph"],
        "primary_category": "quant-ph",
        "published": "2023-01-25",
        "citation_count": 276,
        "topic": "quantum mechanics",
    },
    {
        "arxiv_id": "2304.44002",
        "title": "Quantum Entanglement as a Resource for Computation",
        "authors": [{"name": "Frank Einstein"}, {"name": "Guo Mei"}],
        "abstract": "We characterize quantum entanglement as a computational resource, showing how trusting quantum mechanical predictions enables exponential speedups in certain algorithms.",
        "categories": ["quant-ph", "cs.CC"],
        "primary_category": "quant-ph",
        "published": "2023-08-14",
        "citation_count": 198,
        "topic": "quantum mechanics",
    },
    {
        "arxiv_id": "2304.44003",
        "title": "Quantum Randomness and Its Applications in Cryptography",
        "authors": [{"name": "Hana Sato"}],
        "abstract": "Analysis of genuine quantum randomness sources and their deployment in cryptographic protocols, demonstrating security advantages over classical pseudorandom number generators.",
        "categories": ["quant-ph", "cs.CR"],
        "primary_category": "quant-ph",
        "published": "2023-09-03",
        "citation_count": 143,
        "topic": "quantum mechanics",
    },
    # Topic 5: theoretical physics
    {
        "arxiv_id": "2305.55001",
        "title": "String Theory and the Quest for Unification: Current Status",
        "authors": [{"name": "Ahmed Hassan"}, {"name": "Priya Sharma"}],
        "abstract": "We survey the current status of string theory as a candidate theory of everything, examining its successes, challenges, and experimental prospects.",
        "categories": ["hep-th"],
        "primary_category": "hep-th",
        "published": "2023-04-22",
        "citation_count": 321,
        "topic": "theoretical physics",
    },
    {
        "arxiv_id": "2305.55002",
        "title": "Loop Quantum Gravity: A Path to Quantum General Relativity",
        "authors": [{"name": "Isabella Romano"}],
        "abstract": "Comprehensive review of loop quantum gravity as an approach to reconciling quantum mechanics and general relativity, with predictions for observable signatures.",
        "categories": ["gr-qc", "hep-th"],
        "primary_category": "gr-qc",
        "published": "2023-05-30",
        "citation_count": 245,
        "topic": "theoretical physics",
    },
    {
        "arxiv_id": "2305.55003",
        "title": "The Standard Model and Beyond: Searching for New Physics",
        "authors": [{"name": "Leon Fischer"}, {"name": "Yuki Tanaka"}],
        "abstract": "Review of extensions to the Standard Model of particle physics, examining supersymmetry, extra dimensions, and dark matter candidates at the LHC and beyond.",
        "categories": ["hep-ph"],
        "primary_category": "hep-ph",
        "published": "2023-06-15",
        "citation_count": 287,
        "topic": "theoretical physics",
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers WHERE id LIKE '23%'")
        cur.execute("""
            DELETE FROM notion.pages
            WHERE properties::text ILIKE %s
        """, (f"%{NOTION_PAGE_TITLE}%",))
    conn.commit()
    print("[preprocess] Cleared old scholarly papers and matching notion pages.")


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_scholarly_papers(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
