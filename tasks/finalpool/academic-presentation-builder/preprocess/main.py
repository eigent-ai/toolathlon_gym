"""
Preprocess for academic-presentation-builder task.
- Clears and injects 5 LLM reasoning papers into scholarly.arxiv_papers,
  scholarly.scholar_papers, and arxiv_latex.papers tables.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import os
import argparse
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PAPERS = [
    {
        "arxiv_id": "2201.11903",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": [
            {"name": "Jason Wei"}, {"name": "Xuezhi Wang"},
            {"name": "Dale Schuurmans"}, {"name": "Maarten Bosma"},
            {"name": "Brian Ichter"}, {"name": "Fei Xia"},
            {"name": "Ed Chi"}, {"name": "Quoc Le"}, {"name": "Denny Zhou"}
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We explore how generating a chain of thought, a series of intermediate reasoning steps, "
            "significantly improves the ability of large language models to perform complex reasoning. "
            "We show that chain-of-thought prompting improves performance on a range of arithmetic, "
            "commonsense, and symbolic reasoning tasks."
        ),
        "published": "2022-01-28",
        "pub_year": 2022,
        "venue": "NeurIPS 2022",
        "citation_count": 5200,
        "latex_content": r"""# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

## Introduction

Large language models (LLMs) have demonstrated impressive capabilities across a wide range of NLP tasks. However, their ability to perform complex reasoning remains limited when using standard prompting methods. In this work, we investigate how generating a chain of thought -- a series of intermediate natural language reasoning steps -- can significantly enhance the reasoning abilities of LLMs.

Previous prompting methods typically provide input-output pairs as demonstrations. Our approach augments these demonstrations with intermediate reasoning steps, which we call chain-of-thought prompting. This simple modification enables LLMs to decompose complex problems into manageable steps.

## Method

Chain-of-thought prompting works by providing the model with exemplars that include step-by-step reasoning traces. Given a question, instead of directly mapping to an answer, the model generates intermediate reasoning steps that lead to the final answer. For example, for a math word problem, the model would first identify relevant quantities, then set up equations, solve them step by step, and arrive at the answer.

The key insight is that chain-of-thought prompting is a simple and general technique that requires no fine-tuning or architectural changes. It can be applied to any sufficiently large language model by simply modifying the few-shot exemplars to include reasoning chains.

## Experiments

We evaluate chain-of-thought prompting on three categories of reasoning tasks: arithmetic reasoning, commonsense reasoning, and symbolic reasoning.

For arithmetic reasoning, we use the following benchmarks:
- GSM8K: A dataset of grade school math word problems. Chain-of-thought prompting with PaLM 540B achieves 56.6% accuracy, compared to 17.9% with standard prompting.
- SVAMP: A challenging set of math word problems. Chain-of-thought prompting achieves 79.0% accuracy.
- ASDiv: Another arithmetic word problem dataset where chain-of-thought prompting shows significant improvements.

The results demonstrate that chain-of-thought prompting is an emergent ability of model scale -- it primarily helps models with approximately 100B parameters or more, while providing little benefit to smaller models.

## Conclusion

We have shown that chain-of-thought prompting is a simple and broadly applicable method for enhancing the reasoning capabilities of large language models. By augmenting few-shot exemplars with intermediate reasoning steps, we observe significant performance gains across arithmetic, commonsense, and symbolic reasoning benchmarks. This work opens up new avenues for improving LLM reasoning through better prompting strategies.
""",
    },
    {
        "arxiv_id": "2203.11171",
        "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
        "authors": [
            {"name": "Xuezhi Wang"}, {"name": "Jason Wei"},
            {"name": "Dale Schuurmans"}, {"name": "Quoc Le"},
            {"name": "Ed Chi"}, {"name": "Sharan Narang"},
            {"name": "Aakanksha Chowdhery"}, {"name": "Denny Zhou"}
        ],
        "categories": ["cs.CL"],
        "primary_category": "cs.CL",
        "abstract": (
            "We introduce self-consistency, a new decoding strategy that samples multiple diverse "
            "reasoning paths and selects the most consistent answer. Self-consistency improves "
            "chain-of-thought prompting on arithmetic and commonsense reasoning benchmarks."
        ),
        "published": "2022-03-21",
        "pub_year": 2022,
        "venue": "ICLR 2023",
        "citation_count": 2800,
        "latex_content": r"""# Self-Consistency Improves Chain of Thought Reasoning in Language Models

## Introduction

Chain-of-thought prompting has shown remarkable improvements in the reasoning capabilities of large language models. However, the standard approach of greedy decoding generates only a single reasoning path, which may not always lead to the correct answer. In this paper, we propose self-consistency, a simple yet effective decoding strategy that significantly improves reasoning performance.

The intuition behind self-consistency is that complex reasoning tasks typically admit multiple valid reasoning paths that all converge to the correct answer. By sampling diverse reasoning paths and aggregating the answers, we can identify the most consistent and likely correct solution.

## Method

Self-consistency replaces the naive greedy decoding used in chain-of-thought prompting with a sample-and-marginalize procedure. The algorithm consists of three steps:

1. Sample multiple diverse reasoning paths from the language model using chain-of-thought prompting with temperature sampling.
2. Extract the final answer from each reasoning path.
3. Select the most frequent answer through majority voting.

This approach is unsupervised and does not require any additional training or fine-tuning. It leverages the observation that correct reasoning paths tend to converge on the same answer, while incorrect paths are more likely to produce diverse wrong answers.

## Experiments

We evaluate self-consistency on multiple reasoning benchmarks:

- GSM8K: Self-consistency with PaLM 540B achieves 74.4% accuracy, a significant improvement over the 56.6% achieved by standard chain-of-thought prompting. This represents a 17.8 percentage point improvement.
- SVAMP: Self-consistency improves accuracy from 79.0% to 86.6%.
- AQuA: Self-consistency shows consistent improvements across different model scales.

The results demonstrate that self-consistency provides complementary gains on top of chain-of-thought prompting, without requiring any model modifications.

## Conclusion

Self-consistency is a simple, unsupervised decoding strategy that substantially improves the reasoning performance of chain-of-thought prompting. By sampling multiple reasoning paths and selecting the most consistent answer, we achieve state-of-the-art results on several reasoning benchmarks. This work highlights the importance of decoding strategies in unlocking the reasoning potential of large language models.
""",
    },
    {
        "arxiv_id": "2305.10601",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "authors": [
            {"name": "Shunyu Yao"}, {"name": "Dian Yu"},
            {"name": "Jeffrey Zhao"}, {"name": "Izhak Shafran"},
            {"name": "Thomas Griffiths"}, {"name": "Yuan Cao"},
            {"name": "Karthik Narasimhan"}
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We introduce Tree of Thoughts (ToT), a framework that generalizes chain-of-thought "
            "prompting by allowing exploration of multiple reasoning paths. ToT enables systematic "
            "search through a tree of possible thoughts using BFS or DFS strategies."
        ),
        "published": "2023-05-17",
        "pub_year": 2023,
        "venue": "NeurIPS 2023",
        "citation_count": 1900,
        "latex_content": r"""# Tree of Thoughts: Deliberate Problem Solving with Large Language Models

## Introduction

While chain-of-thought prompting has significantly improved the reasoning abilities of large language models, it still follows a linear reasoning path from left to right. This limitation prevents LLMs from exploring alternative reasoning strategies, backtracking from errors, or making deliberate planning decisions. In this work, we propose Tree of Thoughts (ToT), a framework that enables LLMs to engage in deliberate problem solving by exploring multiple reasoning paths organized as a tree structure.

## Background

Chain-of-thought prompting generates reasoning as a sequential chain of thoughts. Self-consistency samples multiple chains but processes them independently. Neither approach allows for systematic exploration of a reasoning space with lookahead and backtracking. Tree of Thoughts addresses this gap by enabling tree-structured reasoning where the model can explore, evaluate, and backtrack through different thought paths.

## Method

The Tree of Thoughts framework consists of four key components:

1. Thought Decomposition: Breaking down a problem into intermediate thought steps of appropriate granularity.
2. Thought Generation: Generating candidate thoughts at each step, either independently (sampling) or sequentially (proposing).
3. State Evaluation: Evaluating the promise of different partial solutions using the LLM itself as a heuristic evaluator.
4. Search Algorithm: Using either breadth-first search (BFS) or depth-first search (DFS) to systematically explore the tree of thoughts.

BFS explores all nodes at the current depth before moving deeper, maintaining a fixed number of the most promising candidates. DFS explores each branch to its full depth before backtracking, which is more memory-efficient for problems with deep solution paths.

## Experiments

We evaluate ToT on three novel tasks that require non-trivial planning and search:

- Game of 24: Given four numbers, find a mathematical expression that equals 24 using basic arithmetic operations. ToT with BFS achieves a 74% success rate, compared to 4% with chain-of-thought prompting. The task is effectively solved by the tree-based exploration strategy.
- Creative Writing: Generating coherent passages with constraint satisfaction. ToT produces significantly more coherent and creative outputs as judged by GPT-4 evaluation.
- Mini Crosswords: Solving 5x5 crossword puzzles. ToT with DFS achieves substantially higher word-level and letter-level success rates compared to baseline approaches.

## Conclusion

Tree of Thoughts represents a significant advance in enabling deliberate problem-solving with large language models. By organizing reasoning as a tree and applying systematic search strategies, ToT dramatically improves performance on tasks requiring exploration and planning. The framework is general and can be adapted to various problem types by adjusting the thought decomposition, generation, evaluation, and search components.
""",
    },
    {
        "arxiv_id": "2305.14992",
        "title": "Reasoning with Language Model is Planning with World Model",
        "authors": [
            {"name": "Shibo Hao"}, {"name": "Yi Gu"},
            {"name": "Haodi Ma"}, {"name": "Joshua Hong"},
            {"name": "Zhen Wang"}, {"name": "Daisy Wang"},
            {"name": "Zhiting Hu"}
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We propose RAP (Reasoning via Planning), which repurposes the LLM as both a world model "
            "and a reasoning agent, and incorporates Monte Carlo Tree Search for strategic exploration "
            "in the reasoning space."
        ),
        "published": "2023-05-24",
        "pub_year": 2023,
        "venue": "ICML 2023",
        "citation_count": 850,
        "latex_content": r"""# Reasoning with Language Model is Planning with World Model

## Introduction

Large language models have shown remarkable reasoning capabilities, yet they still struggle with complex tasks that require strategic planning and exploration. Existing methods like chain-of-thought prompting follow a linear autoregressive generation process, which limits their ability to plan ahead and consider multiple possibilities. In this paper, we propose Reasoning via Planning (RAP), a novel framework that repurposes the LLM as both a world model and a reasoning agent.

## Related Work

Prior work on improving LLM reasoning includes chain-of-thought prompting, self-consistency, and tree of thoughts. While these methods have shown improvements, they either lack systematic exploration (chain-of-thought), treat reasoning paths independently (self-consistency), or rely on heuristic evaluation (tree of thoughts). RAP addresses these limitations by incorporating principled planning algorithms from the reinforcement learning literature.

## Method

RAP consists of two main components:

1. World Model: The LLM serves as a world model that predicts the outcomes of different reasoning actions. Given the current reasoning state, the LLM generates possible next states by simulating the effects of different reasoning steps.

2. Reasoning Agent with MCTS: We use Monte Carlo Tree Search (MCTS) to strategically explore the reasoning space. MCTS balances exploration and exploitation through its UCB (Upper Confidence Bound) selection strategy. The search process involves:
   - Selection: Choosing promising nodes to expand based on UCB scores.
   - Expansion: Generating new reasoning states using the world model.
   - Simulation: Estimating the value of new states through rollouts.
   - Backpropagation: Updating node statistics based on simulation results.

The integration of MCTS with the LLM world model enables principled exploration of the reasoning space with lookahead and backtracking capabilities.

## Experiments

We evaluate RAP on multiple reasoning benchmarks:

- Blocksworld: A classical planning task requiring multi-step block manipulation. RAP achieves 64% accuracy, significantly outperforming chain-of-thought prompting (28%) and demonstrating the value of planning-based reasoning.
- GSM8K: RAP achieves 48.3% accuracy on this math reasoning benchmark, showing improvements over standard prompting approaches.
- Logical Reasoning: RAP demonstrates strong performance on tasks requiring multi-step logical deductions.

The results show that incorporating planning algorithms into LLM reasoning leads to substantial improvements, especially on tasks requiring strategic exploration and long-horizon reasoning.

## Conclusion

RAP demonstrates that framing LLM reasoning as planning with a world model leads to significant improvements in reasoning capabilities. By combining the LLM's ability to simulate reasoning states with MCTS's principled exploration strategy, RAP achieves strong performance across diverse reasoning tasks. This work opens up exciting possibilities for integrating classical planning algorithms with modern language models.
""",
    },
    {
        "arxiv_id": "2305.20050",
        "title": "Let's Verify Step by Step",
        "authors": [
            {"name": "Hunter Lightman"}, {"name": "Vineet Kosaraju"},
            {"name": "Yura Burda"}, {"name": "Harri Edwards"},
            {"name": "Bowen Baker"}, {"name": "Teddy Lee"},
            {"name": "Jan Leike"}, {"name": "John Schulman"}
        ],
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "abstract": (
            "We investigate process-based supervision for training reward models to verify each step "
            "of a reasoning chain. Our process-supervised reward model (PRM) solves 78.2% of problems "
            "from MATH benchmark, significantly outperforming outcome-based supervision."
        ),
        "published": "2023-05-31",
        "pub_year": 2023,
        "venue": "arXiv preprint",
        "citation_count": 1500,
        "latex_content": r"""# Let's Verify Step by Step

## Introduction

As large language models are increasingly used for complex mathematical reasoning, ensuring the correctness of their reasoning chains becomes critical. In this work, we investigate two approaches to training reward models for verifying mathematical reasoning: outcome-based supervision and process-based supervision. We find that process supervision, which provides feedback on each individual reasoning step, leads to significantly better performance than outcome supervision, which only evaluates the final answer.

## Related Work

Previous work on improving mathematical reasoning in LLMs has focused on techniques such as chain-of-thought prompting, self-consistency, and majority voting. While these methods improve answer accuracy, they do not directly address the quality of intermediate reasoning steps. Our work is complementary to these approaches, as process supervision can be combined with any generation method to improve reasoning quality.

## Method

We compare two types of reward models:

1. Outcome-Supervised Reward Model (ORM): The ORM is trained to evaluate complete solutions by predicting whether the final answer is correct. It receives supervision only at the solution level, without any information about the correctness of individual steps.

2. Process-Supervised Reward Model (PRM): The PRM is trained to evaluate each step of a reasoning chain independently. It receives step-level supervision indicating whether each reasoning step is correct, neutral, or incorrect. This fine-grained feedback allows the PRM to identify exactly where reasoning goes wrong.

We train both types of reward models on a large dataset of mathematical problem solutions generated by GPT-4. For the PRM, we collect human annotations labeling each step as positive, neutral, or negative.

## Experiments

We evaluate our reward models on the MATH benchmark, a challenging dataset of competition-level mathematics problems:

- Process-Supervised Reward Model (PRM): Achieves 78.2% accuracy on MATH, representing a significant improvement in mathematical reasoning performance.
- Outcome-Supervised Reward Model (ORM): Achieves 72.4% accuracy on MATH, which is strong but substantially below the PRM.
- The 5.8 percentage point gap between PRM and ORM demonstrates the value of step-level supervision.

We also find that the PRM produces more interpretable evaluations, as it can pinpoint specific steps where reasoning errors occur. This makes PRM-based verification more useful for human oversight and debugging of LLM reasoning.

## Conclusion

Our results demonstrate that process supervision is a more effective strategy than outcome supervision for training reward models to verify mathematical reasoning. The process-supervised reward model achieves state-of-the-art performance on the MATH benchmark while providing more interpretable evaluations. This work highlights the importance of fine-grained supervision for improving the reliability of LLM reasoning and supports the broader goal of aligning AI systems through scalable oversight.
""",
    },
]


def clear_tables(conn):
    """Clear existing data from all relevant tables."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
    conn.commit()
    print("Cleared scholarly.arxiv_papers, scholarly.scholar_papers, arxiv_latex.papers")


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
                p["arxiv_id"],
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                json.dumps(p["categories"]),
                p["primary_category"],
                p["published"],
                p["published"],
                None,
                p.get("venue"),
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                None,
            ))
    conn.commit()
    print(f"Injected {len(PAPERS)} papers into scholarly.arxiv_papers")


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
                p["title"],
                json.dumps(p["authors"]),
                p["abstract"],
                p["pub_year"],
                p.get("venue"),
                p.get("citation_count", 0),
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}",
                json.dumps({"title": p["title"], "year": p["pub_year"]}),
            ))
    conn.commit()
    print(f"Injected {len(PAPERS)} papers into scholarly.scholar_papers")


def inject_arxiv_latex(conn):
    """Inject papers into arxiv_latex.papers with full LaTeX content."""
    with conn.cursor() as cur:
        for p in PAPERS:
            # Extract section titles from the markdown-style LaTeX content
            sections = []
            for line in p["latex_content"].split("\n"):
                stripped = line.strip()
                if stripped.startswith("## "):
                    sections.append(stripped[3:].strip())
                elif stripped.startswith("# ") and not stripped.startswith("# " + p["title"][:20]):
                    sections.append(stripped[2:].strip())

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
                p["arxiv_id"],
                p["title"],
                p["abstract"],
                p["latex_content"],
                json.dumps(sections),
                p["latex_content"],
            ))
    conn.commit()
    print(f"Injected {len(PAPERS)} papers into arxiv_latex.papers")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_tables(conn)
        inject_arxiv_papers(conn)
        inject_scholar_papers(conn)
        inject_arxiv_latex(conn)
    finally:
        conn.close()

    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    main()
