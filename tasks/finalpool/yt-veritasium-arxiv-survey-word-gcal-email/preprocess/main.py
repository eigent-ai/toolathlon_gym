"""
Preprocess for yt-veritasium-arxiv-survey-word-gcal-email task.

Injects:
  - 7 papers into arxiv.papers
  - 2 emails (from seminar@science.edu and collab@research.org)
  - 1 gcal event: Lab Meeting 2026-04-10 09:00-10:00
  - Clears arxiv, email, gcal tables before injecting

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import argparse
import json
import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

PAPERS = [
    {
        "id": "2301.10226",
        "title": "The Many-Worlds Interpretation Revisited: Quantum Decoherence and Branching",
        "authors": [{"name": "Sean Carroll"}],
        "summary": "We revisit the many-worlds interpretation of quantum mechanics through the lens of modern decoherence theory. Quantum branching is analyzed using density matrix formalism and pointer states. We argue that decoherence provides a natural mechanism for the emergence of classical branches from quantum superpositions, resolving key objections to the Everettian framework.",
        "categories": ["quant-ph"],
        "primary_category": "quant-ph",
        "pdf_url": "https://arxiv.org/pdf/2301.10226",
        "published": "2023-01-24",
    },
    {
        "id": "2302.08468",
        "title": "Game Theory and Evolution: Mathematical Models of Cooperation",
        "authors": [{"name": "Martin Nowak"}],
        "summary": "We present a comprehensive analysis of evolutionary game theory models applied to cooperation in biological systems. Replicator dynamics, invasion analysis, and spatial games are used to study the emergence and stability of cooperative behavior. Results are validated against empirical data from microbial communities and animal social groups.",
        "categories": ["math.PR", "q-bio.PE"],
        "primary_category": "q-bio.PE",
        "pdf_url": "https://arxiv.org/pdf/2302.08468",
        "published": "2023-02-16",
    },
    {
        "id": "2303.14100",
        "title": "Cognitive Biases in Scientific Reasoning",
        "authors": [{"name": "Daniel Kahneman"}, {"name": "Amos Tversky"}],
        "summary": "We examine how cognitive biases systematically distort scientific reasoning and decision making. Anchoring, confirmation bias, availability heuristic, and overconfidence are studied in the context of scientific hypothesis generation and experimental design. We propose debiasing strategies for research teams and propose a framework for bias-aware experimental methodology.",
        "categories": ["q-bio.NC"],
        "primary_category": "q-bio.NC",
        "pdf_url": "https://arxiv.org/pdf/2303.14100",
        "published": "2023-03-24",
    },
    {
        "id": "2304.01537",
        "title": "Paradoxes in Mathematics: From Cantor to Godel",
        "authors": [{"name": "Timothy Gowers"}],
        "summary": "We trace the development of mathematical paradoxes from Cantor's diagonal argument through Russell's paradox to Godel's incompleteness theorems. The role of self-reference, infinite sets, and formal systems in generating paradoxes is analyzed. We discuss how these foundational crises shaped modern mathematical logic and set theory.",
        "categories": ["math.LO"],
        "primary_category": "math.LO",
        "pdf_url": "https://arxiv.org/pdf/2304.01537",
        "published": "2023-04-03",
    },
    {
        "id": "2305.12312",
        "title": "Fluid Dynamics in Nature: Biomimetic Engineering",
        "authors": [{"name": "John Dabiri"}],
        "summary": "We investigate fluid dynamic principles observed in biological organisms and their application to biomimetic engineering design. Vortex dynamics in fish locomotion, bird flight aerodynamics, and jellyfish propulsion are analyzed using computational fluid dynamics. Applications to energy-efficient underwater vehicles and wind turbine design are discussed.",
        "categories": ["physics.flu-dyn"],
        "primary_category": "physics.flu-dyn",
        "pdf_url": "https://arxiv.org/pdf/2305.12312",
        "published": "2023-05-20",
    },
    {
        "id": "2306.09341",
        "title": "The Fermi Paradox: Statistical Analysis of Intelligent Life",
        "authors": [{"name": "Anders Sandberg"}],
        "summary": "We apply Bayesian statistical methods to the Fermi paradox, analyzing the probability of intelligent civilizations given the Drake equation parameters. Monte Carlo simulations across plausible parameter ranges suggest that the absence of observed extraterrestrial intelligence is consistent with humans being rare or alone in the observable universe.",
        "categories": ["astro-ph.EP"],
        "primary_category": "astro-ph.EP",
        "pdf_url": "https://arxiv.org/pdf/2306.09341",
        "published": "2023-06-15",
    },
    {
        "id": "2307.15988",
        "title": "Neuroplasticity: How Learning Changes the Brain",
        "authors": [{"name": "Michael Merzenich"}],
        "summary": "We review the mechanisms of neuroplasticity and their implications for learning and cognitive rehabilitation. Synaptic plasticity, long-term potentiation, and cortical remapping are examined across development and adulthood. Evidence from clinical interventions demonstrates that targeted training can restore function following brain injury and slow age-related cognitive decline.",
        "categories": ["q-bio.NC"],
        "primary_category": "q-bio.NC",
        "pdf_url": "https://arxiv.org/pdf/2307.15988",
        "published": "2023-07-29",
    },
]

GCAL_EVENTS = [
    {
        "summary": "Lab Meeting",
        "description": "Weekly lab team meeting. Agenda: project updates, paper reading assignments.",
        "start": "2026-04-10 09:00:00",
        "end": "2026-04-10 10:00:00",
    },
]

EMAILS = [
    {
        "message_id": "msg-seminar-001",
        "subject": "Science Communication Survey - Status Inquiry",
        "from_addr": "seminar@science.edu",
        "to_addr": ["researcher@scicomm.org"],
        "date": "2026-03-05 10:00:00+00",
        "body_text": (
            "Hello,\n\n"
            "We wanted to check on the status of the Veritasium science communication survey. "
            "We are hoping to schedule the team seminar for early April and need the final document "
            "at least a week in advance for review. Could you confirm the timeline and send us a draft "
            "when ready?\n\n"
            "Best,\nSeminar Committee\nseminar@science.edu"
        ),
    },
    {
        "message_id": "msg-collab-001",
        "subject": "Interest in Science Communication Collaboration",
        "from_addr": "collab@research.org",
        "to_addr": ["researcher@scicomm.org"],
        "date": "2026-03-06 14:00:00+00",
        "body_text": (
            "Hi,\n\n"
            "I heard you are working on a survey linking popular science videos to academic research. "
            "This aligns closely with our lab's outreach work. We would be very interested in collaborating "
            "and possibly co-presenting at a seminar. Please let me know if there is an opportunity to get involved.\n\n"
            "Best regards,\nDr. Research\ncollab@research.org"
        ),
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM arxiv.papers")
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared arxiv, gcal, email tables.")


def inject_arxiv_papers(conn):
    with conn.cursor() as cur:
        for p in PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers
                (id, title, authors, summary, categories, primary_category, pdf_url, published, is_downloaded)
                VALUES (%s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary
            """, (
                p["id"], p["title"], json.dumps(p["authors"]),
                p["summary"], json.dumps(p["categories"]),
                p["primary_category"], p["pdf_url"], p["published"], True,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into arxiv.papers.")


def inject_gcal_events(conn):
    with conn.cursor() as cur:
        for ev in GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime,
                    start_timezone, end_timezone, creator, organizer, attendees)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
            """, (
                ev["summary"], ev["description"], ev["start"], ev["end"],
                "Asia/Shanghai", "Asia/Shanghai",
                json.dumps({}), json.dumps({}), json.dumps([]),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(GCAL_EVENTS)} GCal events.")


def inject_emails(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()
            cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
            row = cur.fetchone()
        folder_id = row[0]

        for em in EMAILS:
            cur.execute("""
                INSERT INTO email.messages (message_id, subject, from_addr, to_addr, date, body_text, folder_id)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s)
                ON CONFLICT (message_id) DO NOTHING
            """, (
                em["message_id"], em["subject"], em["from_addr"],
                json.dumps(em["to_addr"]), em["date"], em["body_text"], folder_id,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(EMAILS)} emails.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_arxiv_papers(conn)
        inject_gcal_events(conn)
        inject_emails(conn)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
