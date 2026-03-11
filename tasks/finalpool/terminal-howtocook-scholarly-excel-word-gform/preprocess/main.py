"""Preprocess for terminal-howtocook-scholarly-excel-word-gform.
Clears scholarly, gform. Injects 6 papers into scholarly.scholar_papers (4 relevant + 2 noise).
"""
import argparse
import json
import os
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}

RELEVANT_PAPERS = [
    {
        "title": "Effectiveness of Workplace Nutrition Programs: A Systematic Review and Meta-Analysis",
        "authors": [{"name": "Sarah M. Chen"}, {"name": "David R. Liu"}, {"name": "Emily K. Torres"}],
        "abstract": "This systematic review examines 42 workplace nutrition intervention programs conducted between 2010 and 2023. Results show that structured meal planning programs reduced employee BMI by an average of 1.8 points over 12 months, with 67% of participants reporting improved dietary habits. Programs combining meal recommendations with educational workshops showed 23% higher adherence rates than meal-only interventions. The most effective programs offered diverse menu options accommodating at least three dietary restriction categories.",
        "pub_year": 2023,
        "venue": "Journal of Occupational Health Psychology",
        "citation_count": 156,
        "url": "https://doi.org/10.1037/ocp.2023.0142"
    },
    {
        "title": "Dietary Intervention Strategies for Improving Employee Health Outcomes in Corporate Settings",
        "authors": [{"name": "Michael J. Patterson"}, {"name": "Lisa A. Wong"}],
        "abstract": "We conducted a randomized controlled trial with 500 employees across 4 corporate campuses to evaluate dietary intervention strategies. Employees who received weekly evidence-based meal plans showed significant improvements in self-reported energy levels (p<0.001) and a 15% reduction in sick days over 6 months. High-protein lunch options were associated with improved afternoon productivity scores. The study found that programs with budgets between $30-$40 per employee per week achieved optimal cost-effectiveness ratios.",
        "pub_year": 2022,
        "venue": "American Journal of Preventive Medicine",
        "citation_count": 89,
        "url": "https://doi.org/10.1016/j.amepre.2022.03.015"
    },
    {
        "title": "The Role of Vegetarian and Low-Sodium Diets in Workplace Wellness: A Longitudinal Study",
        "authors": [{"name": "Priya Sharma"}, {"name": "Robert K. Nguyen"}, {"name": "Angela M. Davis"}],
        "abstract": "This three-year longitudinal study tracked 1,200 employees participating in corporate nutrition programs that offered vegetarian and low-sodium meal options. Employees who regularly chose vegetarian meals showed 12% lower cholesterol levels compared to the control group. Low-sodium diet adherents demonstrated a mean blood pressure reduction of 8 mmHg systolic. The study recommends that workplace nutrition programs include at least 40% vegetarian options and clearly label sodium content to maximize health benefits.",
        "pub_year": 2021,
        "venue": "Nutrition Research Reviews",
        "citation_count": 203,
        "url": "https://doi.org/10.1017/S0954422421000178"
    },
    {
        "title": "Employee Engagement in Corporate Nutrition Programs: Survey Design and Feedback Mechanisms",
        "authors": [{"name": "Thomas B. Miller"}, {"name": "Jennifer L. Clark"}],
        "abstract": "Effective nutrition programs require continuous employee feedback. Our study of 15 corporate wellness programs found that organizations using structured dietary preference surveys had 35% higher program participation rates. Programs that updated menus quarterly based on survey feedback retained 78% of participants after one year, compared to 45% retention in static programs. The most successful surveys included questions about dietary restrictions, meal timing preferences, budget comfort levels, and interest in educational components like cooking workshops.",
        "pub_year": 2022,
        "venue": "Journal of Workplace Behavioral Health",
        "citation_count": 47,
        "url": "https://doi.org/10.1080/15555240.2022.2089123"
    },
]

NOISE_PAPERS = [
    {
        "title": "Optimizing Sports Nutrition for Elite Marathon Runners: Carbohydrate Loading Strategies",
        "authors": [{"name": "James T. Foster"}, {"name": "Yuki Tanaka"}],
        "abstract": "This study examines carbohydrate loading protocols for elite marathon runners competing in major international events. We tested five different glycogen supercompensation strategies across 80 professional athletes during their competition season. Results indicate that a modified 3-day loading protocol increased muscle glycogen stores by 28% compared to traditional 7-day protocols, with no significant difference in gastrointestinal distress.",
        "pub_year": 2023,
        "venue": "International Journal of Sport Nutrition and Exercise Metabolism",
        "citation_count": 31,
        "url": "https://doi.org/10.1123/ijsnem.2023.0087"
    },
    {
        "title": "Agricultural Policy and Food Supply Chain Resilience in Developing Nations",
        "authors": [{"name": "Carlos M. Rodriguez"}, {"name": "Amina B. Osei"}],
        "abstract": "This paper analyzes the impact of agricultural subsidies and trade policies on food supply chain resilience in 25 developing nations between 2015 and 2022. We find that nations with diversified agricultural output and strategic grain reserves experienced 40% fewer food supply disruptions during global crises. Policy recommendations include investment in local food processing infrastructure and reduction of dependency on single-crop exports.",
        "pub_year": 2022,
        "venue": "World Development",
        "citation_count": 72,
        "url": "https://doi.org/10.1016/j.worlddev.2022.106091"
    },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear scholarly
        cur.execute("DELETE FROM scholarly.scholar_papers")
        print("[preprocess] Cleared scholarly.scholar_papers.")

        # Clear gform
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        print("[preprocess] Cleared gform data.")

        # Inject papers (4 relevant + 2 noise)
        all_papers = RELEVANT_PAPERS + NOISE_PAPERS
        for p in all_papers:
            cur.execute("""
                INSERT INTO scholarly.scholar_papers (title, authors, abstract, pub_year, venue, citation_count, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (p["title"], json.dumps(p["authors"]), p["abstract"],
                  p["pub_year"], p["venue"], p["citation_count"], p["url"]))
        conn.commit()
        print(f"[preprocess] Injected {len(all_papers)} papers into scholarly.scholar_papers.")

        # Inject noise gform
        noise_form_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gform.forms (id, title, document_title, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (noise_form_id, "IT Equipment Request Form", "IT Equipment Request Form",
              "Form for requesting new IT equipment."))
        cur.execute("""
            INSERT INTO gform.questions (id, form_id, item_id, title, question_type, required, position)
            VALUES (%s, %s, %s, %s, %s, true, 0)
        """, (str(uuid.uuid4()), noise_form_id, str(uuid.uuid4()),
              "What equipment do you need?", "TEXT"))
        conn.commit()
        print("[preprocess] Injected noise gform data.")

        # Verify
        cur.execute("SELECT COUNT(*) FROM scholarly.scholar_papers")
        count = cur.fetchone()[0]
        print(f"[preprocess] scholarly.scholar_papers count: {count}")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Clean up agent workspace
    if args.agent_workspace:
        for fname in ["Nutrition_Program_Analysis.xlsx", "Nutrition_Program_Proposal.docx",
                       "categorize_recipes.py", "analyze_research.py", "build_menus.py",
                       "validate_menus.py", "categorized_recipes.json", "research_findings.json",
                       "evidence_based_menus.json"]:
            fpath = os.path.join(args.agent_workspace, fname)
            if os.path.exists(fpath):
                os.remove(fpath)
                print(f"[preprocess] Removed {fpath}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
