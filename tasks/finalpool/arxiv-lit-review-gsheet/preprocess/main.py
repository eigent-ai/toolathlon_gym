"""
Preprocess for arxiv-lit-review-gsheet task.

Clears arxiv, scholarly, arxiv_latex, and gsheet schemas, then injects
8 papers (5 prompt engineering + 3 noise word embedding papers) into
arxiv.papers, scholarly.arxiv_papers, scholarly.scholar_papers, and
arxiv_latex.papers with matching IDs and titles across all schemas.

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
        "arxiv_id": "2201.11903",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": [
            {"name": "Jason Wei"}, {"name": "Xuezhi Wang"},
            {"name": "Dale Schuurmans"}, {"name": "Maarten Bosma"},
            {"name": "Brian Ichter"}, {"name": "Fei Xia"},
            {"name": "Ed Chi"}, {"name": "Quoc Le"},
            {"name": "Denny Zhou"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We explore how generating a chain of thought, a series of intermediate reasoning steps, "
            "significantly improves the ability of large language models to perform complex reasoning. "
            "We show that chain-of-thought prompting, where a few chain of thought demonstrations are "
            "provided as exemplars in prompting, is a simple and broadly applicable method for improving "
            "reasoning in language models. Experiments on three large language models show that chain-of-thought "
            "prompting improves performance on a range of arithmetic, commonsense, and symbolic reasoning tasks."
        ),
        "published": "2022-01-28",
        "pub_year": 2022,
        "venue": "NeurIPS 2022",
        "citation_count": 6500,
        "is_noise": False,
        "markdown_content": (
            "# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models\n\n"
            "## Abstract\n\n"
            "We explore how generating a chain of thought improves complex reasoning in LLMs.\n\n"
            "## Introduction\n\n"
            "LLMs struggle with multi-step reasoning tasks. We propose chain-of-thought prompting.\n\n"
            "## Methodology\n\n"
            "Chain-of-thought prompting augments few-shot exemplars with intermediate reasoning steps. "
            "Instead of providing just input-output pairs, each exemplar includes a step-by-step reasoning "
            "chain that leads to the final answer. The model then generates its own chain of thought before "
            "arriving at the answer. This is a few-shot prompting approach that requires no model fine-tuning. "
            "We experiment with PaLM 540B, GPT-3, and LaMDA 137B across arithmetic (GSM8K, SVAMP, ASDiv, "
            "AQuA, MAWPS), commonsense (CSQA, StrategyQA), and symbolic reasoning (last letter, coin flip) tasks.\n\n"
            "## Experiments\n\n"
            "Chain-of-thought prompting improves PaLM 540B from 17.9% to 58.1% on GSM8K. It is an emergent "
            "ability that only works with sufficiently large models (100B+ parameters)."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Chain-of-Thought Prompting Elicits Reasoning in Large Language Models}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We explore how chain of thought improves complex reasoning in LLMs.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "LLMs struggle with multi-step reasoning. We propose chain-of-thought prompting.\n\n"
            "\\section{Methodology}\n"
            "Few-shot exemplars augmented with intermediate reasoning steps. No fine-tuning required. "
            "Tested on arithmetic, commonsense, and symbolic reasoning.\n\n"
            "\\section{Experiments}\n"
            "PaLM 540B improves from 17.9% to 58.1% on GSM8K with chain-of-thought prompting.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2203.11171",
        "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
        "authors": [
            {"name": "Xuezhi Wang"}, {"name": "Jason Wei"},
            {"name": "Dale Schuurmans"}, {"name": "Quoc Le"},
            {"name": "Ed Chi"}, {"name": "Sharan Narang"},
            {"name": "Aakanksha Chowdhery"}, {"name": "Denny Zhou"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We introduce self-consistency, a new decoding strategy that significantly improves chain-of-thought "
            "prompting. The key idea is to sample multiple diverse reasoning paths from the language model and "
            "then select the most consistent answer by marginalizing over the sampled reasoning paths. "
            "Self-consistency leverages the intuition that a complex reasoning problem typically admits multiple "
            "different ways of thinking leading to its unique correct answer."
        ),
        "published": "2022-03-21",
        "pub_year": 2022,
        "venue": "ICLR 2023",
        "citation_count": 3200,
        "is_noise": False,
        "markdown_content": (
            "# Self-Consistency Improves Chain of Thought Reasoning in Language Models\n\n"
            "## Abstract\n\n"
            "We introduce self-consistency, a decoding strategy that improves chain-of-thought prompting.\n\n"
            "## Introduction\n\n"
            "Chain-of-thought prompting uses greedy decoding, which may not find the best reasoning path.\n\n"
            "## Methodology\n\n"
            "Self-consistency replaces greedy decoding with sampling multiple reasoning paths and selecting "
            "the most consistent answer via majority voting. Given a prompt with chain-of-thought exemplars, "
            "we sample k different reasoning paths from the language model using temperature-based sampling. "
            "Each path produces a final answer. We then take the majority vote across all sampled answers. "
            "This requires no additional training, fine-tuning, or auxiliary models. The approach works with "
            "any chain-of-thought prompting setup and is complementary to other improvements.\n\n"
            "## Experiments\n\n"
            "Self-consistency improves CoT accuracy on GSM8K from 56.5% to 74.4% with GPT-3 code-davinci-002."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Self-Consistency Improves Chain of Thought Reasoning in Language Models}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We introduce self-consistency to improve chain-of-thought prompting.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Greedy decoding may not find the best reasoning path.\n\n"
            "\\section{Methodology}\n"
            "Sample multiple reasoning paths, majority vote on final answers. No additional training.\n\n"
            "\\section{Experiments}\n"
            "Improves CoT on GSM8K from 56.5% to 74.4% with GPT-3.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2210.03493",
        "title": "Automatic Chain of Thought Prompting in Large Language Models",
        "authors": [
            {"name": "Zhuosheng Zhang"}, {"name": "Aston Zhang"},
            {"name": "Mu Li"}, {"name": "Alex Smola"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "Chain-of-thought (CoT) prompting can improve the reasoning ability of large language models. "
            "However, the current CoT methods rely on carefully hand-crafted demonstrations. We propose "
            "Auto-CoT, which automatically constructs demonstrations for chain-of-thought prompting. "
            "Auto-CoT uses clustering to select diverse questions and then generates reasoning chains "
            "using zero-shot CoT (Let's think step by step). This eliminates the need for manual "
            "demonstration design while maintaining competitive performance."
        ),
        "published": "2022-10-07",
        "pub_year": 2022,
        "venue": "ICLR 2023",
        "citation_count": 1800,
        "is_noise": False,
        "markdown_content": (
            "# Automatic Chain of Thought Prompting in Large Language Models\n\n"
            "## Abstract\n\n"
            "We propose Auto-CoT, which automatically constructs demonstrations for CoT prompting.\n\n"
            "## Introduction\n\n"
            "Manual CoT demonstration design is costly. We automate it.\n\n"
            "## Methodology\n\n"
            "Auto-CoT has two steps. First, questions are partitioned into clusters using sentence "
            "embeddings and k-means clustering to ensure diversity. Second, for each cluster, a representative "
            "question is selected and its reasoning chain is generated using zero-shot CoT (appending "
            "'Let's think step by step' to the question). These automatically generated demonstrations "
            "are concatenated to form the final few-shot prompt. The key insight is that diversity in "
            "demonstrations is critical, and clustering helps achieve this without manual selection.\n\n"
            "## Experiments\n\n"
            "Auto-CoT matches or exceeds manual CoT on 10 benchmark reasoning tasks including GSM8K, "
            "AQuA, and MultiArith with GPT-3."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Automatic Chain of Thought Prompting in Large Language Models}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We propose Auto-CoT to automatically construct CoT demonstrations.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Manual CoT demonstration design is costly. We automate it with clustering.\n\n"
            "\\section{Methodology}\n"
            "Cluster questions for diversity, generate reasoning chains with zero-shot CoT.\n\n"
            "\\section{Experiments}\n"
            "Matches manual CoT on 10 benchmark reasoning tasks.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2205.11916",
        "title": "Large Language Models are Zero-Shot Reasoners",
        "authors": [
            {"name": "Takeshi Kojima"}, {"name": "Shixiang Shane Gu"},
            {"name": "Machel Reid"}, {"name": "Yutaka Matsuo"},
            {"name": "Yusuke Iwasawa"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "We show that large language models are decent zero-shot reasoners by simply adding 'Let's think "
            "step by step' before each answer. This zero-shot chain of thought (Zero-shot-CoT) significantly "
            "outperforms zero-shot LLM performance on diverse benchmark reasoning tasks without requiring "
            "hand-crafted few-shot examples. Zero-shot-CoT is versatile and task-agnostic, unlike prior "
            "chain-of-thought prompting that requires crafting task-specific step-by-step examples."
        ),
        "published": "2022-05-24",
        "pub_year": 2022,
        "venue": "NeurIPS 2022",
        "citation_count": 4100,
        "is_noise": False,
        "markdown_content": (
            "# Large Language Models are Zero-Shot Reasoners\n\n"
            "## Abstract\n\n"
            "We show that adding 'Let's think step by step' enables zero-shot reasoning in LLMs.\n\n"
            "## Introduction\n\n"
            "Prior CoT prompting requires hand-crafted examples. We propose a zero-shot alternative.\n\n"
            "## Methodology\n\n"
            "Zero-shot-CoT uses a two-stage prompting process. In the first stage, the input question is "
            "augmented with 'Let's think step by step' to elicit a reasoning chain from the model. In the "
            "second stage, the generated reasoning chain is concatenated with the original question and "
            "a prompt asking for the final answer (e.g., 'Therefore, the answer is'). This approach requires "
            "no task-specific demonstrations and works across different reasoning domains including arithmetic, "
            "symbolic, commonsense, and other logical reasoning tasks.\n\n"
            "## Experiments\n\n"
            "Zero-shot-CoT with text-davinci-002 achieves 40.7% on MultiArith (vs 17.7% standard zero-shot) "
            "and competitive results on GSM8K, SVAMP, and commonsense reasoning benchmarks."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Large Language Models are Zero-Shot Reasoners}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "Adding 'Let's think step by step' enables zero-shot reasoning.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Prior CoT requires hand-crafted examples. We propose zero-shot alternative.\n\n"
            "\\section{Methodology}\n"
            "Two-stage prompting: elicit reasoning with trigger phrase, then extract answer.\n\n"
            "\\section{Experiments}\n"
            "40.7% on MultiArith vs 17.7% standard zero-shot.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2305.10601",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "authors": [
            {"name": "Shunyu Yao"}, {"name": "Dian Yu"},
            {"name": "Jeffrey Zhao"}, {"name": "Izhak Shafran"},
            {"name": "Thomas L. Griffiths"}, {"name": "Yuan Cao"},
            {"name": "Karthik Narasimhan"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "Language models are increasingly capable of performing reasoning tasks, yet their autoregressive "
            "token-level left-to-right decision-making process is insufficient for tasks requiring exploration, "
            "strategic lookahead, or where initial decisions play a pivotal role. We introduce Tree of Thoughts "
            "(ToT), a framework that generalizes over chain of thought prompting and enables exploration over "
            "coherent units of text (thoughts) that serve as intermediate steps toward problem solving. ToT "
            "allows the LM to self-evaluate choices, use search algorithms such as BFS and DFS, and look "
            "ahead or backtrack when necessary."
        ),
        "published": "2023-05-17",
        "pub_year": 2023,
        "venue": "NeurIPS 2023",
        "citation_count": 2400,
        "is_noise": False,
        "markdown_content": (
            "# Tree of Thoughts: Deliberate Problem Solving with Large Language Models\n\n"
            "## Abstract\n\n"
            "We introduce Tree of Thoughts (ToT), a framework that enables exploration over coherent "
            "units of text for problem solving.\n\n"
            "## Introduction\n\n"
            "Chain-of-thought prompting follows a single reasoning path. Many problems require exploring "
            "multiple possibilities and backtracking.\n\n"
            "## Methodology\n\n"
            "Tree of Thoughts generalizes chain-of-thought prompting by maintaining a tree of reasoning "
            "states. Each node represents a partial solution (a thought). The framework has four key components: "
            "(1) Thought decomposition: breaking the problem into intermediate thought steps. "
            "(2) Thought generation: proposing multiple candidate thoughts at each step using either "
            "sampling or sequential generation. (3) State evaluation: using the LM to evaluate the promise "
            "of each thought (e.g., rate it as sure/maybe/impossible). (4) Search algorithm: using BFS or "
            "DFS to explore the tree of thoughts, with the ability to backtrack from unpromising paths. "
            "This enables deliberate planning and exploration for complex reasoning tasks.\n\n"
            "## Experiments\n\n"
            "ToT significantly outperforms CoT on Game of 24 (74% vs 4%), Creative Writing, and Mini Crosswords."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Tree of Thoughts: Deliberate Problem Solving with Large Language Models}\n"
            "\\begin{document}\n\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We introduce ToT for exploration-based problem solving.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "CoT follows a single path. Many problems need exploration and backtracking.\n\n"
            "\\section{Methodology}\n"
            "Tree of thoughts with thought decomposition, generation, evaluation, and search (BFS/DFS).\n\n"
            "\\section{Experiments}\n"
            "74% vs 4% (CoT) on Game of 24.\n\n"
            "\\end{document}"
        ),
    },
    # Noise papers (word embeddings - not prompt engineering)
    {
        "arxiv_id": "1301.03781",
        "title": "Efficient Estimation of Word Representations in Vector Space",
        "authors": [
            {"name": "Tomas Mikolov"}, {"name": "Kai Chen"},
            {"name": "Greg Corrado"}, {"name": "Jeffrey Dean"},
        ],
        "categories": ["cs.CL"],
        "primary_category": "cs.CL",
        "abstract": (
            "We propose two novel model architectures for computing continuous vector representations of words "
            "from very large data sets. The quality of these representations is measured in a word similarity "
            "task, and the results are compared to the previously best performing techniques based on different "
            "types of neural networks. We observe large improvements in accuracy at much lower computational cost."
        ),
        "published": "2013-01-16",
        "pub_year": 2013,
        "venue": "ICLR 2013 Workshop",
        "citation_count": 35000,
        "is_noise": True,
        "markdown_content": (
            "# Efficient Estimation of Word Representations in Vector Space\n\n"
            "## Abstract\n\nWe propose Word2Vec for computing word vectors.\n\n"
            "## Methodology\n\nCBOW and Skip-gram architectures for word embeddings.\n\n"
            "## Experiments\n\nLarge improvements in word similarity tasks.\n\n"
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Efficient Estimation of Word Representations in Vector Space}\n"
            "\\begin{document}\n\\maketitle\n"
            "\\section{Methodology}\nCBOW and Skip-gram for word embeddings.\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "1310.04546",
        "title": "Distributed Representations of Words and Phrases and their Compositionality",
        "authors": [
            {"name": "Tomas Mikolov"}, {"name": "Ilya Sutskever"},
            {"name": "Kai Chen"}, {"name": "Greg Corrado"},
            {"name": "Jeffrey Dean"},
        ],
        "categories": ["cs.CL"],
        "primary_category": "cs.CL",
        "abstract": (
            "The recently introduced continuous Skip-gram model is an efficient method for learning "
            "high-quality distributed vector representations that capture a large number of precise "
            "syntactic and semantic word relationships. In this paper we present several extensions that "
            "improve both the quality of the vectors and the training speed."
        ),
        "published": "2013-10-16",
        "pub_year": 2013,
        "venue": "NeurIPS 2013",
        "citation_count": 28000,
        "is_noise": True,
        "markdown_content": (
            "# Distributed Representations of Words and Phrases\n\n"
            "## Abstract\n\nExtensions to Skip-gram for better word vectors.\n\n"
            "## Methodology\n\nNegative sampling and subsampling techniques.\n\n"
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Distributed Representations of Words and Phrases}\n"
            "\\begin{document}\n\\maketitle\n"
            "\\section{Methodology}\nNegative sampling and subsampling.\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "1405.01512",
        "title": "GloVe: Global Vectors for Word Representation",
        "authors": [
            {"name": "Jeffrey Pennington"}, {"name": "Richard Socher"},
            {"name": "Christopher Manning"},
        ],
        "categories": ["cs.CL"],
        "primary_category": "cs.CL",
        "abstract": (
            "Recent methods for learning vector space representations of words have succeeded in capturing "
            "fine-grained semantic and syntactic regularities using vector arithmetic, but the origin of "
            "these regularities has remained opaque. We analyze and make explicit the model properties "
            "needed for such regularities to emerge in word vectors."
        ),
        "published": "2014-05-05",
        "pub_year": 2014,
        "venue": "EMNLP 2014",
        "citation_count": 25000,
        "is_noise": True,
        "markdown_content": (
            "# GloVe: Global Vectors for Word Representation\n\n"
            "## Abstract\n\nWe propose GloVe for word vector learning.\n\n"
            "## Methodology\n\nCo-occurrence matrix factorization for word embeddings.\n\n"
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{GloVe: Global Vectors for Word Representation}\n"
            "\\begin{document}\n\\maketitle\n"
            "\\section{Methodology}\nCo-occurrence matrix factorization.\n"
            "\\end{document}"
        ),
    },
]


def clear_tables(conn):
    """Clear relevant tables."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM scholarly.arxiv_papers")
        cur.execute("DELETE FROM scholarly.scholar_papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
        cur.execute("DELETE FROM arxiv.papers")
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
    conn.commit()
    print("[preprocess] Cleared arxiv, scholarly, arxiv_latex, and gsheet tables.")


def inject_scholarly_arxiv(conn):
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
                    abstract = EXCLUDED.abstract
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]), p["primary_category"],
                p["published"], p["published"], None, p.get("venue"),
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                f"http://arxiv.org/abs/{p['arxiv_id']}", None,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into scholarly.arxiv_papers")


def inject_scholarly_scholar(conn):
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


def inject_arxiv_papers(conn):
    """Inject papers into arxiv.papers (for arxiv_local MCP)."""
    with conn.cursor() as cur:
        for p in PAPERS:
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
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]), p["primary_category"],
                p["published"], p["published"], None, p.get("venue"), None,
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                json.dumps([]), p["markdown_content"], True,
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into arxiv.papers")


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_scholarly_arxiv(conn)
        inject_scholarly_scholar(conn)
        inject_arxiv_papers(conn)
        inject_arxiv_latex(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
