"""
Preprocess for arxiv-research-report task.
- Clears and injects 5 target papers + 3 noise papers into
  scholarly.arxiv_papers, scholarly.scholar_papers, arxiv.papers,
  and arxiv_latex.papers tables.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import os
import argparse
import json
import psycopg2

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

# ── Target papers (agent should find and include) ────────────────────────────

TARGET_PAPERS = [
    {
        "arxiv_id": "2401.00001",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": [{"name": "Jason Wei"}, {"name": "Xuezhi Wang"}],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We explore how generating a chain of thought, a series of intermediate "
            "reasoning steps, significantly improves the ability of large language models "
            "to perform complex reasoning. We show that chain-of-thought prompting enables "
            "sufficiently large language models to solve challenging arithmetic, commonsense, "
            "and symbolic reasoning tasks that are otherwise difficult with standard prompting. "
            "Experiments on three large language model families demonstrate that chain-of-thought "
            "prompting improves performance on a range of arithmetic, commonsense, and symbolic "
            "reasoning benchmarks."
        ),
        "published": "2024-01-01",
        "pub_year": 2024,
        "venue": "NeurIPS",
        "citation_count": 850,
        "markdown_content": (
            "# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models\n\n"
            "## Abstract\n\n"
            "We explore how generating a chain of thought significantly improves the ability "
            "of large language models to perform complex reasoning.\n\n"
            "## Introduction\n\n"
            "Large language models have demonstrated impressive capabilities across a wide range "
            "of NLP tasks. However, their ability to perform multi-step reasoning remains a key "
            "challenge. Prior work has shown that scaling model size alone does not reliably improve "
            "reasoning performance. In this paper, we propose chain-of-thought (CoT) prompting, a "
            "simple method that elicits reasoning by providing exemplars with intermediate reasoning "
            "steps in the prompt.\n\n"
            "## Methodology\n\n"
            "Chain-of-thought prompting augments few-shot exemplars with a series of intermediate "
            "natural language reasoning steps that lead to the final answer. Rather than providing "
            "input-output pairs alone, each exemplar includes a chain of thought that decomposes "
            "the problem into sequential steps. We evaluate this approach using standard few-shot "
            "prompting with manually written chain-of-thought annotations. The key insight is that "
            "the model learns to decompose problems by imitating the reasoning patterns shown in "
            "the exemplars. We test on arithmetic tasks (GSM8K, SVAMP, ASDiv, AQuA, MAWPS), "
            "commonsense reasoning (CSQA, StrategyQA), and symbolic reasoning (last letter "
            "concatenation, coin flip).\n\n"
            "## Experiments\n\n"
            "Chain-of-thought prompting improves performance across all benchmarks tested. On "
            "GSM8K, PaLM 540B with chain-of-thought achieves 56.9% accuracy compared to 17.9% "
            "with standard prompting. The improvement is more pronounced for larger models, "
            "suggesting an emergent ability. On commonsense reasoning benchmarks, chain-of-thought "
            "prompting achieves new state-of-the-art results without any task-specific fine-tuning.\n\n"
            "## Conclusion\n\n"
            "Chain-of-thought prompting is a simple and broadly applicable method that significantly "
            "improves the reasoning abilities of large language models across arithmetic, commonsense, "
            "and symbolic reasoning tasks."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Chain-of-Thought Prompting Elicits Reasoning in Large Language Models}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We explore how generating a chain of thought significantly improves the ability "
            "of large language models to perform complex reasoning.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Large language models have impressive capabilities but multi-step reasoning remains "
            "challenging. We propose chain-of-thought prompting that elicits reasoning by providing "
            "exemplars with intermediate reasoning steps.\n\n"
            "\\section{Methodology}\n"
            "Chain-of-thought prompting augments few-shot exemplars with intermediate natural language "
            "reasoning steps. Each exemplar includes a chain of thought decomposing the problem into "
            "sequential steps. We test on arithmetic (GSM8K, SVAMP), commonsense (CSQA, StrategyQA), "
            "and symbolic reasoning tasks.\n\n"
            "\\section{Experiments}\n"
            "On GSM8K, PaLM 540B with CoT achieves 56.9% vs 17.9% with standard prompting. "
            "Improvements are more pronounced for larger models. CoT achieves SOTA on commonsense "
            "reasoning without task-specific fine-tuning.\n\n"
            "\\section{Conclusion}\n"
            "Chain-of-thought prompting is a simple method that significantly improves reasoning "
            "across arithmetic, commonsense, and symbolic tasks.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2401.00002",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "authors": [{"name": "Shunyu Yao"}, {"name": "Dian Yu"}],
        "categories": ["cs.AI", "cs.CL"],
        "primary_category": "cs.AI",
        "abstract": (
            "Language models are increasingly being deployed for general problem solving across "
            "a wide range of tasks, but are still confined to token-level, left-to-right decision "
            "making during inference. We introduce Tree of Thoughts (ToT), a framework that generalizes "
            "over chain-of-thought prompting and enables exploration over coherent units of text "
            "(thoughts) that serve as intermediate steps toward problem solving. ToT allows language "
            "models to perform deliberate decision making by considering multiple different reasoning "
            "paths and self-evaluating choices to decide the next course of action, as well as looking "
            "ahead or backtracking when necessary."
        ),
        "published": "2024-01-02",
        "pub_year": 2024,
        "venue": "NeurIPS",
        "citation_count": 420,
        "markdown_content": (
            "# Tree of Thoughts: Deliberate Problem Solving with Large Language Models\n\n"
            "## Abstract\n\n"
            "We introduce Tree of Thoughts (ToT), a framework that generalizes chain-of-thought "
            "prompting and enables exploration over coherent units of text as intermediate reasoning steps.\n\n"
            "## Introduction\n\n"
            "While chain-of-thought prompting has shown promise for improving reasoning, it still "
            "generates reasoning in a linear, left-to-right fashion without the ability to explore "
            "alternative paths or backtrack. Human problem-solving often involves considering multiple "
            "approaches, evaluating partial solutions, and revising strategy. Tree of Thoughts brings "
            "these capabilities to language models by structuring the reasoning process as a search "
            "over a tree of possible thought sequences.\n\n"
            "## Methodology\n\n"
            "Tree of Thoughts frames problem solving as a search over a tree, where each node represents "
            "a partial solution (a thought). The framework consists of four components: (1) thought "
            "decomposition that breaks problems into coherent thought steps, (2) thought generation that "
            "proposes candidate next thoughts using either sampling or proposal prompting, (3) state "
            "evaluation that uses the LM to assess the promise of partial solutions via value prompting "
            "or voting, and (4) search algorithms (BFS or DFS) that navigate the tree to find solutions. "
            "Unlike chain-of-thought which produces a single linear reasoning chain, ToT explores multiple "
            "reasoning paths in parallel and can backtrack from unpromising branches.\n\n"
            "## Experiments\n\n"
            "We evaluate ToT on three novel tasks requiring deliberate planning: Game of 24, Creative "
            "Writing, and Mini Crosswords. On Game of 24, GPT-4 with ToT achieves a 74% success rate "
            "compared to 4% with chain-of-thought. On Creative Writing, human evaluators preferred ToT "
            "generations 41% of the time versus 21% for CoT outputs.\n\n"
            "## Conclusion\n\n"
            "Tree of Thoughts provides a principled framework for deliberate problem solving that "
            "significantly extends the reasoning capabilities of large language models beyond linear "
            "chain-of-thought."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Tree of Thoughts: Deliberate Problem Solving with Large Language Models}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We introduce Tree of Thoughts (ToT), a framework that generalizes chain-of-thought "
            "prompting and enables exploration over coherent text units as reasoning steps.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Chain-of-thought generates reasoning linearly without exploring alternatives. ToT "
            "structures reasoning as a search over a tree of possible thought sequences.\n\n"
            "\\section{Methodology}\n"
            "ToT frames problem solving as tree search with four components: thought decomposition, "
            "thought generation (sampling or proposal prompting), state evaluation (value prompting "
            "or voting), and search algorithms (BFS or DFS). Unlike CoT, ToT explores multiple "
            "paths and can backtrack.\n\n"
            "\\section{Experiments}\n"
            "On Game of 24, GPT-4 with ToT achieves 74% vs 4% with CoT. On Creative Writing, "
            "human evaluators preferred ToT 41% vs 21% for CoT.\n\n"
            "\\section{Conclusion}\n"
            "ToT provides a principled framework for deliberate problem solving extending LM "
            "reasoning beyond linear chain-of-thought.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2401.00003",
        "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
        "authors": [{"name": "Xuezhi Wang"}, {"name": "Jason Wei"}],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "Chain-of-thought prompting combined with pre-trained large language models has achieved "
            "encouraging results on complex reasoning tasks. In this paper, we propose a new decoding "
            "strategy called self-consistency to replace the naive greedy decoding used in chain-of-thought "
            "prompting. It first samples a diverse set of reasoning paths instead of only taking the greedy "
            "one, and then selects the most consistent answer by marginalizing out the sampled reasoning "
            "paths. Self-consistency leverages the intuition that a complex reasoning problem typically "
            "admits multiple different ways of thinking leading to its unique correct answer."
        ),
        "published": "2024-01-03",
        "pub_year": 2024,
        "venue": "ICLR",
        "citation_count": 650,
        "markdown_content": (
            "# Self-Consistency Improves Chain of Thought Reasoning in Language Models\n\n"
            "## Abstract\n\n"
            "We propose self-consistency, a new decoding strategy that samples diverse reasoning paths "
            "and selects the most consistent answer by marginalizing out the sampled reasoning paths.\n\n"
            "## Introduction\n\n"
            "Chain-of-thought prompting has shown remarkable success in enabling language models to "
            "perform step-by-step reasoning. However, the standard approach uses greedy decoding, which "
            "selects only the most likely token at each step. This can lead to suboptimal reasoning "
            "paths. We observe that complex reasoning problems often have multiple valid solution paths "
            "that all arrive at the same correct answer. Self-consistency exploits this property by "
            "sampling multiple reasoning paths and aggregating their answers.\n\n"
            "## Methodology\n\n"
            "Self-consistency operates in three steps: (1) prompt the language model with chain-of-thought "
            "exemplars as in standard CoT prompting, (2) sample multiple diverse reasoning paths from the "
            "language model by using a sampling temperature instead of greedy decoding, and (3) aggregate "
            "the answers by taking a majority vote across all sampled reasoning paths. The key insight is "
            "that correct reasoning paths tend to converge on the right answer while incorrect paths are "
            "more likely to diverge, so majority voting naturally filters out errors. This method is "
            "fully unsupervised and requires no additional training or fine-tuning.\n\n"
            "## Experiments\n\n"
            "Self-consistency significantly improves over chain-of-thought prompting on a range of "
            "arithmetic and commonsense reasoning benchmarks. On GSM8K, self-consistency boosts PaLM "
            "540B from 56.9% to 74.4% accuracy. On ARC-challenge, performance improves from 85.2% to "
            "89.2%. The improvements are consistent across different model families (GPT-3, Codex, PaLM, "
            "UL2) and scale with the number of sampled paths.\n\n"
            "## Conclusion\n\n"
            "Self-consistency is a simple, unsupervised decoding strategy that significantly improves "
            "chain-of-thought reasoning by sampling diverse reasoning paths and aggregating via majority vote."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Self-Consistency Improves Chain of Thought Reasoning in Language Models}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We propose self-consistency, a decoding strategy that samples diverse reasoning paths "
            "and selects the most consistent answer via marginalization.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Standard CoT uses greedy decoding which can lead to suboptimal reasoning. Complex "
            "problems often have multiple valid solution paths converging to the correct answer.\n\n"
            "\\section{Methodology}\n"
            "Self-consistency: (1) prompt with CoT exemplars, (2) sample multiple reasoning paths "
            "with temperature sampling, (3) aggregate via majority vote. Correct paths converge on "
            "right answers; incorrect paths diverge. No additional training required.\n\n"
            "\\section{Experiments}\n"
            "On GSM8K, self-consistency boosts PaLM 540B from 56.9% to 74.4%. On ARC-challenge, "
            "85.2% to 89.2%. Consistent across GPT-3, Codex, PaLM, UL2.\n\n"
            "\\section{Conclusion}\n"
            "Self-consistency is a simple unsupervised strategy that significantly improves CoT "
            "reasoning via diverse sampling and majority voting.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2401.00004",
        "title": "Process Supervision for Mathematical Reasoning",
        "authors": [{"name": "Hunter Lightman"}, {"name": "Vineet Kosaraju"}],
        "categories": ["cs.LG", "cs.AI"],
        "primary_category": "cs.LG",
        "abstract": (
            "Recent work has shown that rewarding language models for each correct step of reasoning "
            "(process supervision) leads to significant improvements over rewarding only the final "
            "answer (outcome supervision). We conduct a detailed investigation of process supervision "
            "for improving mathematical reasoning in large language models. We train process reward "
            "models (PRMs) that score each step of a mathematical solution and use them to search over "
            "many candidate solutions at test time. Our best model solves 78.2% of problems from a "
            "representative subset of the MATH benchmark."
        ),
        "published": "2024-01-04",
        "pub_year": 2024,
        "venue": "ICML",
        "citation_count": 280,
        "markdown_content": (
            "# Process Supervision for Mathematical Reasoning\n\n"
            "## Abstract\n\n"
            "We investigate process supervision for improving mathematical reasoning in LLMs, "
            "training process reward models that score each step of a solution.\n\n"
            "## Introduction\n\n"
            "Large language models have shown remarkable progress on mathematical reasoning tasks "
            "but still make frequent errors in multi-step solutions. A key question is how to most "
            "effectively provide training signal for improving reasoning: should we reward only "
            "correct final answers (outcome supervision) or should we reward each correct reasoning "
            "step (process supervision)? This paper presents a thorough comparison of these two "
            "approaches and demonstrates the superiority of process supervision.\n\n"
            "## Methodology\n\n"
            "We train process reward models (PRMs) that assign a correctness score to each step in "
            "a mathematical solution. The training data is collected by having human labelers annotate "
            "each step of model-generated solutions as correct, incorrect, or neutral. At test time, "
            "we generate multiple candidate solutions and use the PRM to rank them via best-of-N "
            "sampling. We also compare against outcome reward models (ORMs) that only score the final "
            "answer. The PRM provides fine-grained supervision that helps identify exactly where "
            "reasoning goes wrong, enabling more targeted correction.\n\n"
            "## Experiments\n\n"
            "On the MATH benchmark, our PRM-based approach achieves 78.2% accuracy using best-of-1860 "
            "sampling, compared to 72.4% for the ORM approach and 52.9% for the base model. Process "
            "supervision is more sample-efficient: with only 100 samples, the PRM achieves 71.5% while "
            "the ORM reaches 67.8%. We also find that PRMs produce better-calibrated confidence scores "
            "and more interpretable feedback about solution quality.\n\n"
            "## Conclusion\n\n"
            "Process supervision significantly outperforms outcome supervision for mathematical "
            "reasoning, providing more sample-efficient training and more interpretable feedback."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Process Supervision for Mathematical Reasoning}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We investigate process supervision for improving mathematical reasoning in LLMs, "
            "training process reward models that score each step.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "LLMs make frequent errors in multi-step mathematical solutions. We compare outcome "
            "supervision (rewarding final answers) vs process supervision (rewarding each step).\n\n"
            "\\section{Methodology}\n"
            "We train process reward models (PRMs) assigning correctness scores to each solution "
            "step. Human labelers annotate steps as correct/incorrect/neutral. At test time, we use "
            "best-of-N sampling with PRM ranking. We compare against outcome reward models (ORMs).\n\n"
            "\\section{Experiments}\n"
            "On MATH benchmark: PRM achieves 78.2% (best-of-1860) vs ORM 72.4% vs base 52.9%. "
            "With 100 samples: PRM 71.5% vs ORM 67.8%. PRMs provide better calibration.\n\n"
            "\\section{Conclusion}\n"
            "Process supervision significantly outperforms outcome supervision for mathematical "
            "reasoning with more efficient training and interpretable feedback.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2401.00005",
        "title": "Scaling LLM Reasoning with Reinforcement Learning",
        "authors": [{"name": "Alex Chen"}, {"name": "Sarah Miller"}],
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "abstract": (
            "We present a comprehensive study on scaling reasoning capabilities in large language "
            "models through reinforcement learning. Building on recent advances in reward modeling "
            "and policy optimization, we demonstrate that RL-based training can substantially improve "
            "multi-step reasoning across mathematical, scientific, and logical domains. We propose a "
            "novel curriculum learning strategy combined with proximal policy optimization that achieves "
            "state-of-the-art results on challenging reasoning benchmarks. Our analysis reveals key "
            "scaling laws governing the relationship between model size, RL training compute, and "
            "reasoning performance."
        ),
        "published": "2024-01-05",
        "pub_year": 2024,
        "venue": "AAAI",
        "citation_count": 190,
        "markdown_content": (
            "# Scaling LLM Reasoning with Reinforcement Learning\n\n"
            "## Abstract\n\n"
            "We study scaling reasoning capabilities in LLMs through reinforcement learning, "
            "proposing a novel curriculum learning strategy with PPO.\n\n"
            "## Introduction\n\n"
            "While prompting-based methods like chain-of-thought and tree of thoughts have shown "
            "promise for improving reasoning, they do not fundamentally change the model's reasoning "
            "capabilities. Reinforcement learning offers a path to genuinely improving the model's "
            "internal reasoning abilities through iterative training with reward signals. This paper "
            "explores how RL can be effectively scaled to train strong reasoning models.\n\n"
            "## Methodology\n\n"
            "Our approach combines three key components: (1) a reward model trained on human "
            "preferences over reasoning traces that provides step-level feedback, (2) proximal policy "
            "optimization (PPO) for stable policy updates that prevent catastrophic forgetting, and "
            "(3) a curriculum learning strategy that gradually increases problem difficulty during "
            "training. The curriculum starts with simple single-step problems and progressively "
            "introduces more complex multi-step reasoning tasks. We also employ rejection sampling "
            "to generate high-quality training trajectories and use a KL penalty to maintain "
            "generation diversity.\n\n"
            "## Experiments\n\n"
            "On the MATH benchmark, our RL-trained model achieves 67.3% accuracy compared to 52.9% "
            "for the supervised fine-tuned baseline. On ARC-challenge, we achieve 92.1% accuracy, "
            "surpassing prior state-of-the-art. Our scaling analysis reveals that RL training compute "
            "follows a log-linear relationship with reasoning performance improvement, and that larger "
            "models benefit more from RL training in terms of absolute performance gains.\n\n"
            "## Conclusion\n\n"
            "Reinforcement learning provides a powerful framework for scaling reasoning capabilities "
            "in LLMs, with curriculum learning and careful optimization being key to success."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Scaling LLM Reasoning with Reinforcement Learning}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We study scaling reasoning in LLMs through RL, proposing curriculum learning with PPO.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Prompting methods don't change model's internal reasoning. RL offers a path to "
            "genuinely improving reasoning capabilities through iterative training.\n\n"
            "\\section{Methodology}\n"
            "Three components: (1) step-level reward model from human preferences, (2) PPO for "
            "stable updates preventing catastrophic forgetting, (3) curriculum learning from simple "
            "to complex problems. We use rejection sampling and KL penalty for diversity.\n\n"
            "\\section{Experiments}\n"
            "MATH benchmark: 67.3% vs 52.9% supervised baseline. ARC-challenge: 92.1% SOTA. "
            "RL compute follows log-linear scaling with reasoning improvement.\n\n"
            "\\section{Conclusion}\n"
            "RL provides a powerful framework for scaling LLM reasoning with curriculum learning "
            "and careful optimization as key ingredients.\n\n"
            "\\end{document}"
        ),
    },
]

# ── Noise papers (should NOT be included in the survey) ──────────────────────

NOISE_PAPERS = [
    {
        "arxiv_id": "2401.00010",
        "title": "Efficient Image Classification with Vision Transformers",
        "authors": [{"name": "Maria Lopez"}, {"name": "David Kim"}],
        "categories": ["cs.CV"],
        "primary_category": "cs.CV",
        "abstract": (
            "We propose an efficient architecture for image classification using vision transformers. "
            "Our approach reduces computational cost by 40% while maintaining accuracy on ImageNet. "
            "We introduce adaptive token pruning and hierarchical attention mechanisms."
        ),
        "published": "2024-01-10",
        "pub_year": 2024,
        "venue": "CVPR",
        "citation_count": 95,
    },
    {
        "arxiv_id": "2401.00011",
        "title": "Federated Learning for Privacy-Preserving NLP",
        "authors": [{"name": "James Smith"}, {"name": "Anna Zhang"}],
        "categories": ["cs.CR", "cs.CL"],
        "primary_category": "cs.CR",
        "abstract": (
            "We present a federated learning framework for training NLP models while preserving "
            "user privacy. Our approach uses differential privacy guarantees and secure aggregation "
            "to train language models without exposing individual data points. We demonstrate "
            "competitive performance on text classification and named entity recognition tasks."
        ),
        "published": "2024-01-11",
        "pub_year": 2024,
        "venue": "ACL",
        "citation_count": 45,
    },
    {
        "arxiv_id": "2401.00012",
        "title": "Protein Structure Prediction Using Deep Learning",
        "authors": [{"name": "Emily Brown"}, {"name": "Michael Johnson"}],
        "categories": ["q-bio.BM", "cs.LG"],
        "primary_category": "q-bio.BM",
        "abstract": (
            "We develop a deep learning model for protein structure prediction that achieves "
            "state-of-the-art accuracy on CASP15 targets. Our model combines graph neural networks "
            "with attention mechanisms to predict 3D protein structures from amino acid sequences. "
            "The approach outperforms existing methods in both accuracy and computational efficiency."
        ),
        "published": "2024-01-12",
        "pub_year": 2024,
        "venue": "Nature Methods",
        "citation_count": 120,
    },
]


def clear_tables(conn):
    """Clear existing data from all relevant tables."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("Cleared scholarly.arxiv_papers, scholarly.scholar_papers, arxiv_latex.papers, arxiv.papers")


def inject_arxiv_papers(conn, papers):
    """Inject papers into arxiv.papers."""
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO arxiv.papers
                (id, title, authors, summary, categories, primary_category,
                 published, updated, doi, journal_ref, comment, pdf_url,
                 links, markdown_content, is_downloaded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary,
                    categories = EXCLUDED.categories,
                    primary_category = EXCLUDED.primary_category,
                    published = EXCLUDED.published,
                    markdown_content = EXCLUDED.markdown_content,
                    is_downloaded = EXCLUDED.is_downloaded
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
                None,
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                json.dumps([]),
                p.get("markdown_content", ""),
                bool(p.get("markdown_content")),
            ))
    conn.commit()
    print(f"Injected {len(papers)} papers into arxiv.papers")


def inject_scholarly_arxiv(conn, papers):
    """Inject papers into scholarly.arxiv_papers."""
    with conn.cursor() as cur:
        for p in papers:
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
    print(f"Injected {len(papers)} papers into scholarly.arxiv_papers")


def inject_scholarly_scholar(conn, papers):
    """Inject papers into scholarly.scholar_papers."""
    with conn.cursor() as cur:
        for p in papers:
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
    print(f"Injected {len(papers)} papers into scholarly.scholar_papers")


def inject_arxiv_latex(conn, papers):
    """Inject papers into arxiv_latex.papers (only for papers with LaTeX content)."""
    count = 0
    with conn.cursor() as cur:
        for p in papers:
            if "latex_content" not in p:
                continue
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
                p["arxiv_id"],
                p["title"],
                p["abstract"],
                md,
                json.dumps(sections),
                p["latex_content"],
            ))
            count += 1
    conn.commit()
    print(f"Injected {count} papers into arxiv_latex.papers")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONN)
    try:
        clear_tables(conn)

        # Inject all papers (target + noise) into arxiv.papers and scholarly
        all_papers = TARGET_PAPERS + NOISE_PAPERS
        inject_arxiv_papers(conn, all_papers)
        inject_scholarly_arxiv(conn, all_papers)
        inject_scholarly_scholar(conn, all_papers)

        # Inject only target papers into arxiv_latex (noise papers have no LaTeX)
        inject_arxiv_latex(conn, TARGET_PAPERS)
    finally:
        conn.close()

    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    main()
