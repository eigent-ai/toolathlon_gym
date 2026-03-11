"""
Preprocess for arxiv-conference-prep task.

Clears and injects papers into:
  - scholarly.scholar_papers (5 RLHF papers + 1 noise paper)
  - scholarly.arxiv_papers  (same 6 papers)
  - arxiv_latex.papers      (same 6 papers with LaTeX content)

Also clears gcal.events and email tables so the agent starts fresh.

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
    {
        "arxiv_id": "2203.02155",
        "title": "Training language models to follow instructions with human feedback",
        "authors": [
            {"name": "Long Ouyang"}, {"name": "Jeff Wu"}, {"name": "Xu Jiang"},
            {"name": "Diogo Almeida"}, {"name": "Carroll Wainwright"},
            {"name": "Pamela Mishkin"}, {"name": "Chong Zhang"},
            {"name": "Sandhini Agarwal"}, {"name": "Katarina Slama"},
            {"name": "Alex Ray"}, {"name": "John Schulman"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "Making language models bigger does not inherently make them better at following a user's intent. "
            "Large language models can generate outputs that are untruthful, toxic, or simply not helpful. "
            "We show an avenue for aligning language models with user intent on a wide range of tasks by "
            "fine-tuning with human feedback. Starting with a set of labeler-written prompts and prompts "
            "submitted through an API, we collect a dataset of labeler demonstrations of the desired model "
            "behavior, which we use to fine-tune GPT-3 using supervised learning. We then collect a dataset "
            "of rankings of model outputs, which we use to further fine-tune this supervised model using "
            "reinforcement learning from human feedback (RLHF). The resulting model, called InstructGPT, "
            "shows improvements in truthfulness and reductions in toxic output generation."
        ),
        "published": "2022-03-04",
        "pub_year": 2022,
        "venue": "NeurIPS 2022",
        "citation_count": 8500,
        "markdown_content": (
            "# Training language models to follow instructions with human feedback\n\n"
            "## Abstract\n\n"
            "We show an avenue for aligning language models with user intent by fine-tuning with human feedback. "
            "The resulting model, InstructGPT, shows improvements in truthfulness and reductions in toxic output.\n\n"
            "## Introduction\n\n"
            "Large language models can generate outputs that are untruthful, toxic, or unhelpful. We use RLHF "
            "to align models with human preferences.\n\n"
            "## Methodology\n\n"
            "Our approach has three steps: (1) Collect demonstration data and train a supervised policy using "
            "supervised fine-tuning (SFT). (2) Collect comparison data and train a reward model (RM). "
            "(3) Optimize the policy against the reward model using PPO. The reward model is trained on human "
            "rankings of model outputs. We use Proximal Policy Optimization to update the language model policy "
            "to maximize the reward while staying close to the original model via a KL penalty.\n\n"
            "## Experiments\n\n"
            "InstructGPT with 1.3B parameters is preferred to GPT-3 with 175B parameters by human evaluators. "
            "It shows improvements in truthfulness on TruthfulQA and reductions in toxic output on RealToxicityPrompts."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Training language models to follow instructions with human feedback}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We show an avenue for aligning language models with user intent by fine-tuning with human feedback.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Large language models can generate untruthful, toxic, or unhelpful outputs. We use RLHF to align them.\n\n"
            "\\section{Methodology}\n"
            "Three steps: (1) SFT on demonstration data, (2) train reward model on comparison data, "
            "(3) optimize policy with PPO against reward model with KL penalty.\n\n"
            "\\section{Experiments}\n"
            "InstructGPT 1.3B is preferred to GPT-3 175B by human evaluators.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2009.01325",
        "title": "Learning to summarize from human feedback",
        "authors": [
            {"name": "Nisan Stiennon"}, {"name": "Long Ouyang"},
            {"name": "Jeff Wu"}, {"name": "Daniel Ziegler"},
            {"name": "Ryan Lowe"}, {"name": "Chelsea Voss"},
            {"name": "Alec Radford"}, {"name": "Dario Amodei"},
            {"name": "Paul Christiano"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "As language models become more powerful, training and evaluation are increasingly bottlenecked by "
            "the data and metrics used for a particular task. We propose training models to optimize for human "
            "preferences by training a reward model from human comparisons, then using that reward model as a "
            "reward function to fine-tune a summarization policy using reinforcement learning. We apply our "
            "method to abstractive summarization of Reddit posts and find that our models generate better "
            "summaries than those trained with supervised learning alone."
        ),
        "published": "2020-09-02",
        "pub_year": 2020,
        "venue": "NeurIPS 2020",
        "citation_count": 3200,
        "markdown_content": (
            "# Learning to summarize from human feedback\n\n"
            "## Abstract\n\n"
            "We propose training models to optimize for human preferences using a reward model trained from "
            "human comparisons and RL fine-tuning for summarization.\n\n"
            "## Introduction\n\n"
            "Training and evaluation of language models are bottlenecked by data and metrics. Human feedback "
            "provides a more direct signal for quality.\n\n"
            "## Methodology\n\n"
            "We first train a reward model from human comparisons of summaries. The reward model takes a post "
            "and summary as input and outputs a scalar reward. We then use this reward model to fine-tune a "
            "summarization policy using PPO. We also apply techniques like KL regularization to prevent the "
            "policy from diverging too far from the supervised baseline.\n\n"
            "## Experiments\n\n"
            "Models trained with human feedback generate better summaries than supervised baselines on Reddit "
            "TL;DR dataset. Human evaluators prefer our RL-trained summaries 61% of the time."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Learning to summarize from human feedback}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We propose training models to optimize for human preferences using reward models and RL.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Human feedback provides a more direct signal for model quality than automated metrics.\n\n"
            "\\section{Methodology}\n"
            "Train reward model from human comparisons, then fine-tune summarization policy with PPO "
            "and KL regularization.\n\n"
            "\\section{Experiments}\n"
            "Human evaluators prefer our RL-trained summaries 61% of the time on Reddit TL;DR.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2212.08073",
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "authors": [
            {"name": "Yuntao Bai"}, {"name": "Saurav Kadavath"},
            {"name": "Sandipan Kundu"}, {"name": "Amanda Askell"},
            {"name": "Jackson Kernion"}, {"name": "Andy Jones"},
            {"name": "Anna Chen"}, {"name": "Anna Goldie"},
            {"name": "Azalia Mirhoseini"}, {"name": "Cameron McKinnon"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We experiment with methods for training a harmless AI assistant through a process we call "
            "Constitutional AI (CAI). The idea is to use a set of principles (a constitution) to guide the "
            "model to produce harmless outputs without relying entirely on human feedback for harmlessness. "
            "We first use the constitution to generate self-critiques and revisions, creating a dataset of "
            "AI-generated revisions (RLAIF). We then train a preference model on this data and use it for RL. "
            "This approach reduces the need for human labels while producing models that are both helpful and harmless."
        ),
        "published": "2022-12-15",
        "pub_year": 2022,
        "venue": "arXiv preprint",
        "citation_count": 2800,
        "markdown_content": (
            "# Constitutional AI: Harmlessness from AI Feedback\n\n"
            "## Abstract\n\n"
            "We experiment with Constitutional AI (CAI) for training harmless AI assistants using AI feedback "
            "instead of purely human feedback.\n\n"
            "## Introduction\n\n"
            "Training harmless AI systems typically requires extensive human labeling. Constitutional AI uses "
            "a set of principles to guide self-improvement.\n\n"
            "## Methodology\n\n"
            "Constitutional AI has two phases. In the critique-revision phase, the model generates outputs and "
            "then critiques its own outputs based on constitutional principles, producing revised responses. "
            "In the RL phase, we train a preference model on AI-generated comparisons (RLAIF) rather than human "
            "comparisons (RLHF). The preference model is then used to fine-tune the policy via reinforcement "
            "learning. The constitution consists of principles about helpfulness, harmlessness, and honesty.\n\n"
            "## Experiments\n\n"
            "CAI models are both more helpful and more harmless than models trained with RLHF alone. "
            "The approach significantly reduces the need for human red-teaming labels."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Constitutional AI: Harmlessness from AI Feedback}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We experiment with Constitutional AI for training harmless AI assistants using AI feedback.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Training harmless AI typically requires extensive human labeling. CAI uses principles for self-improvement.\n\n"
            "\\section{Methodology}\n"
            "Two phases: critique-revision (self-critique based on constitutional principles) and RL phase "
            "(RLAIF with AI-generated comparisons). The constitution defines helpfulness, harmlessness, honesty.\n\n"
            "\\section{Experiments}\n"
            "CAI models are more helpful and harmless than RLHF-only models.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2305.18290",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "authors": [
            {"name": "Rafael Rafailov"}, {"name": "Archit Sharma"},
            {"name": "Eric Mitchell"}, {"name": "Stefano Ermon"},
            {"name": "Christopher D. Manning"}, {"name": "Chelsea Finn"},
        ],
        "categories": ["cs.LG", "cs.AI", "cs.CL"],
        "primary_category": "cs.LG",
        "abstract": (
            "While large-scale unsupervised language models learn broad world knowledge and some reasoning skills, "
            "achieving precise control of their behavior is difficult due to the completely unsupervised nature "
            "of their training. Existing methods for gaining such steerability collect human labels of the relative "
            "quality of model generations and fine-tune the unsupervised LM to align with these preferences, "
            "often with reinforcement learning from human feedback (RLHF). We introduce Direct Preference "
            "Optimization (DPO), an algorithm that implicitly optimizes the same objective as existing RLHF "
            "algorithms but is simple to implement and stable to train. DPO does not require fitting a reward "
            "model, sampling from the LM during fine-tuning, or performing significant hyperparameter tuning."
        ),
        "published": "2023-05-29",
        "pub_year": 2023,
        "venue": "NeurIPS 2023",
        "citation_count": 4200,
        "markdown_content": (
            "# Direct Preference Optimization: Your Language Model is Secretly a Reward Model\n\n"
            "## Abstract\n\n"
            "We introduce DPO, an algorithm that implicitly optimizes the same objective as RLHF but is simpler "
            "and more stable to train, without requiring a separate reward model.\n\n"
            "## Introduction\n\n"
            "RLHF typically involves training a reward model and then using RL to optimize against it. This "
            "pipeline is complex and unstable. DPO provides a simpler alternative.\n\n"
            "## Methodology\n\n"
            "DPO leverages a mapping between reward functions and optimal policies to transform the constrained "
            "reward maximization problem into a simple classification loss over preference pairs. Given a dataset "
            "of preferred and dispreferred completions, DPO directly optimizes the policy using a binary "
            "cross-entropy objective. The key insight is that the optimal policy under a KL-constrained reward "
            "maximization objective can be expressed in closed form as a function of the reward model.\n\n"
            "## Experiments\n\n"
            "DPO matches or exceeds PPO-based RLHF on summarization and dialogue tasks while being significantly "
            "simpler. On TL;DR summarization, DPO achieves similar win rates to PPO with fewer hyperparameters."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Direct Preference Optimization: Your Language Model is Secretly a Reward Model}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We introduce DPO, implicitly optimizing the same RLHF objective but simpler and more stable.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "RLHF is complex and unstable. DPO provides a simpler alternative.\n\n"
            "\\section{Methodology}\n"
            "DPO transforms constrained reward maximization into classification loss over preference pairs. "
            "Binary cross-entropy objective directly on the policy, leveraging closed-form optimal policy.\n\n"
            "\\section{Experiments}\n"
            "DPO matches PPO-based RLHF on summarization and dialogue with fewer hyperparameters.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "1707.06347",
        "title": "Proximal Policy Optimization Algorithms",
        "authors": [
            {"name": "John Schulman"}, {"name": "Filip Wolski"},
            {"name": "Prafulla Dhariwal"}, {"name": "Alec Radford"},
            {"name": "Oleg Klimov"},
        ],
        "categories": ["cs.LG", "cs.AI"],
        "primary_category": "cs.LG",
        "abstract": (
            "We propose a new family of policy gradient methods for reinforcement learning, which alternate "
            "between sampling data through interaction with the environment, and optimizing a surrogate objective "
            "function using stochastic gradient ascent. Whereas standard policy gradient methods perform one "
            "gradient update per data sample, we propose a novel objective function that enables multiple epochs "
            "of minibatch updates. The new methods, which we call proximal policy optimization (PPO), have some "
            "of the benefits of trust region policy optimization (TRPO), but they are much simpler to implement, "
            "more general, and have better sample complexity. PPO is the foundation algorithm used in RLHF pipelines."
        ),
        "published": "2017-07-20",
        "pub_year": 2017,
        "venue": "arXiv preprint",
        "citation_count": 12000,
        "markdown_content": (
            "# Proximal Policy Optimization Algorithms\n\n"
            "## Abstract\n\n"
            "We propose PPO, a family of policy gradient methods that are simple to implement, general, and "
            "have good sample complexity. PPO is the foundation algorithm used in RLHF.\n\n"
            "## Introduction\n\n"
            "Policy gradient methods are the workhorse of RL for complex control. TRPO provides monotonic "
            "improvement guarantees but is complex. PPO achieves similar benefits with simpler implementation.\n\n"
            "## Methodology\n\n"
            "PPO uses a clipped surrogate objective that prevents large policy updates. The objective function "
            "is L_CLIP = E[min(r_t * A_t, clip(r_t, 1-epsilon, 1+epsilon) * A_t)] where r_t is the probability "
            "ratio between old and new policy, and A_t is the advantage estimate. We also use a combined "
            "objective with a value function loss and an entropy bonus. PPO alternates between sampling and "
            "optimization with multiple epochs of minibatch updates.\n\n"
            "## Experiments\n\n"
            "PPO outperforms other online policy gradient methods on Atari and MuJoCo benchmarks."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Proximal Policy Optimization Algorithms}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We propose PPO, simple policy gradient methods with good sample complexity, used in RLHF.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "TRPO is complex. PPO achieves similar benefits with simpler implementation.\n\n"
            "\\section{Methodology}\n"
            "Clipped surrogate objective: L_CLIP = E[min(r_t * A_t, clip(r_t, 1-eps, 1+eps) * A_t)]. "
            "Combined objective with value loss and entropy bonus. Multiple epochs of minibatch updates.\n\n"
            "\\section{Experiments}\n"
            "PPO outperforms other methods on Atari and MuJoCo while being simpler.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "1712.01815",
        "title": "Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm",
        "authors": [
            {"name": "David Silver"}, {"name": "Thomas Hubert"},
            {"name": "Julian Schrittwieser"}, {"name": "Ioannis Antonoglou"},
            {"name": "Matthew Lai"}, {"name": "Arthur Guez"},
        ],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "The game of chess is the most widely-studied domain in the history of artificial intelligence. "
            "The strongest programs are based on a combination of sophisticated search techniques, domain-specific "
            "adaptations, and handcrafted evaluation functions. In this paper we introduce AlphaZero, a general "
            "reinforcement learning algorithm that masters chess, shogi, and Go through self-play without any "
            "domain-specific knowledge beyond game rules. AlphaZero achieves superhuman performance in all three games."
        ),
        "published": "2017-12-05",
        "pub_year": 2017,
        "venue": "Science 2018",
        "citation_count": 5000,
        "markdown_content": (
            "# Mastering Chess and Shogi by Self-Play\n\n"
            "## Abstract\n\n"
            "AlphaZero masters chess, shogi, and Go through self-play without domain-specific knowledge.\n\n"
            "## Introduction\n\n"
            "Chess has been studied in AI for decades. We introduce AlphaZero, a general RL algorithm.\n\n"
            "## Methodology\n\n"
            "AlphaZero uses a deep neural network with Monte Carlo tree search. It learns entirely from "
            "self-play starting from random initialization. No domain knowledge beyond game rules.\n\n"
            "## Experiments\n\n"
            "AlphaZero defeats Stockfish in chess and Elmo in shogi convincingly.\n\n"
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Mastering Chess and Shogi by Self-Play}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "AlphaZero masters chess, shogi, and Go through self-play.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "We introduce AlphaZero, a general RL algorithm for board games.\n\n"
            "\\section{Methodology}\n"
            "Deep neural network with MCTS, learning from self-play only.\n\n"
            "\\section{Experiments}\n"
            "AlphaZero defeats Stockfish and Elmo.\n\n"
            "\\end{document}"
        ),
    },
]


def clear_tables(conn):
    """Clear existing data from all relevant tables."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared scholarly, arxiv_latex, gcal, and email tables.")


def inject_arxiv_papers(conn):
    """Inject papers into scholarly.arxiv_papers."""
    with conn.cursor() as cur:
        for p in PAPERS:
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
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]), p["primary_category"],
                p["published"], p["published"], None, p.get("venue"),
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}", None,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into scholarly.arxiv_papers")


def inject_scholar_papers(conn):
    """Inject papers into scholarly.scholar_papers."""
    with conn.cursor() as cur:
        for p in PAPERS:
            cur.execute("""
                INSERT INTO scholarly.scholar_papers
                (title, authors, abstract, pub_year, venue, citation_count,
                 url, eprint_url, pub_url, bib)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p["title"], json.dumps(p["authors"]), p["abstract"],
                p["pub_year"], p.get("venue"), p.get("citation_count", 0),
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                json.dumps({"title": p["title"], "year": p["pub_year"]}),
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into scholarly.scholar_papers")


def inject_arxiv_latex(conn):
    """Inject papers into arxiv_latex.papers."""
    with conn.cursor() as cur:
        for p in PAPERS:
            md = p["markdown_content"]
            sections = []
            for line in md.split("\n"):
                stripped = line.strip()
                if stripped.startswith("#"):
                    level = 0
                    for ch in stripped:
                        if ch == "#":
                            level += 1
                        else:
                            break
                    title = stripped[level:].strip()
                    if title:
                        sections.append(title)

            cur.execute("""
                INSERT INTO arxiv_latex.papers
                (id, title, abstract, full_prompt, sections, raw_latex, processed_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    abstract = EXCLUDED.abstract,
                    full_prompt = EXCLUDED.full_prompt,
                    sections = EXCLUDED.sections,
                    raw_latex = EXCLUDED.raw_latex,
                    processed_at = NOW()
            """, (
                p["arxiv_id"], p["title"], p["abstract"],
                md, json.dumps(sections), p["latex_content"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into arxiv_latex.papers")


def ensure_email_folder(conn):
    """Ensure INBOX folder exists."""
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
        inject_arxiv_papers(conn)
        inject_scholar_papers(conn)
        inject_arxiv_latex(conn)
        ensure_email_folder(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
