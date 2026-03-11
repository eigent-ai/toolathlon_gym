"""
Preprocess for academic-literature-review task.
- Clears and injects 5 RAG papers into scholarly.arxiv_papers,
  scholarly.scholar_papers, arxiv.papers, and arxiv_latex.papers tables.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import os
import argparse
import json
import psycopg2
import psycopg2.extras

DB_CONN = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PAPERS = [
    {
        "arxiv_id": "2005.11401",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "authors": [
            {"name": "Patrick Lewis"}, {"name": "Ethan Perez"},
            {"name": "Aleksandra Piktus"}, {"name": "Fabio Petroni"},
            {"name": "Vladimir Karpukhin"}, {"name": "Naman Goyal"},
            {"name": "Heinrich Kuttler"}, {"name": "Mike Lewis"},
            {"name": "Wen-tau Yih"}, {"name": "Tim Rocktaschel"},
            {"name": "Sebastian Riedel"}, {"name": "Douwe Kiela"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "Large pre-trained language models have been shown to store factual knowledge in their parameters "
            "and achieve state-of-the-art results when fine-tuned on downstream NLP tasks. However, their "
            "ability to access and precisely manipulate knowledge is still limited. We explore a general-purpose "
            "fine-tuning recipe for retrieval-augmented generation (RAG) models that combine pre-trained parametric "
            "and non-parametric memory for language generation. We introduce RAG models where the parametric "
            "memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of "
            "Wikipedia, accessed with a pre-trained neural retriever."
        ),
        "published": "2020-05-22",
        "pub_year": 2020,
        "venue": "NeurIPS 2020",
        "citation_count": 4800,
        "markdown_content": (
            "# Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks\n\n"
            "## Abstract\n\n"
            "Large pre-trained language models store factual knowledge in their parameters but their ability "
            "to access and manipulate knowledge is limited. We explore retrieval-augmented generation (RAG) "
            "models that combine parametric and non-parametric memory for language generation.\n\n"
            "## Introduction\n\n"
            "Knowledge-intensive NLP tasks such as question answering, fact verification, and dialogue "
            "require accessing large amounts of world knowledge. Traditional approaches rely on structured "
            "knowledge bases, but these are expensive to build and maintain. We propose RAG, which combines "
            "a pre-trained sequence-to-sequence model with a dense retrieval component.\n\n"
            "## Methodology\n\n"
            "RAG models combine a pre-trained retriever (DPR) with a pre-trained generator (BART). "
            "The retriever uses a bi-encoder architecture to retrieve relevant documents from a knowledge "
            "source. We propose two variants: RAG-Sequence, which uses the same retrieved document for "
            "the entire generated sequence, and RAG-Token, which can use different documents for each token. "
            "The model is trained end-to-end by marginalizing over the retrieved documents.\n\n"
            "## Experiments\n\n"
            "We evaluate RAG on open-domain question answering, abstractive question answering, Jeopardy "
            "question generation, and fact verification. RAG achieves state-of-the-art results on three "
            "open-domain QA tasks, outperforming parametric seq2seq models and task-specific retrieve-and-extract "
            "architectures. On the Natural Questions dataset, RAG achieves 44.5 exact match, a new state-of-the-art."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks}\n"
            "\\begin{document}\n"
            "\\maketitle\n\n"
            "\\begin{abstract}\n"
            "Large pre-trained language models store factual knowledge in their parameters but their ability "
            "to access and manipulate knowledge is limited. We explore retrieval-augmented generation (RAG) "
            "models that combine parametric and non-parametric memory for language generation.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Knowledge-intensive NLP tasks require accessing large amounts of world knowledge. Traditional "
            "approaches rely on structured knowledge bases. We propose RAG, which combines a pre-trained "
            "sequence-to-sequence model with a dense retrieval component to access external knowledge.\n\n"
            "\\section{Methodology}\n"
            "RAG combines a pre-trained retriever (DPR) with a pre-trained generator (BART). The retriever "
            "uses a bi-encoder architecture. We propose two variants: RAG-Sequence and RAG-Token. "
            "RAG-Sequence uses the same retrieved document for the entire output, while RAG-Token can use "
            "different documents per token. Training marginalizes over the latent retrieved documents.\n\n"
            "\\section{Experiments}\n"
            "We evaluate on open-domain QA, abstractive QA, Jeopardy question generation, and fact verification. "
            "RAG achieves state-of-the-art on three open-domain QA tasks with 44.5 EM on Natural Questions.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2312.10997",
        "title": "Retrieval-Augmented Generation for Large Language Models: A Survey",
        "authors": [
            {"name": "Yunfan Gao"}, {"name": "Yun Xiong"},
            {"name": "Xinyu Gao"}, {"name": "Kangxiang Jia"},
            {"name": "Jinliu Pan"}, {"name": "Yuxi Bi"},
            {"name": "Yi Dai"}, {"name": "Jiawei Sun"},
            {"name": "Haofen Wang"},
        ],
        "categories": ["cs.CL", "cs.AI", "cs.IR"],
        "primary_category": "cs.CL",
        "abstract": (
            "Large language models (LLMs) demonstrate remarkable capabilities but face challenges including "
            "hallucination, outdated knowledge, and non-transparent reasoning processes. Retrieval-Augmented "
            "Generation (RAG) has emerged as a promising solution by incorporating knowledge from external "
            "databases. This survey provides a comprehensive overview of the RAG paradigm, covering naive RAG, "
            "advanced RAG, and modular RAG frameworks, along with the RAG infrastructure and evaluation methods."
        ),
        "published": "2023-12-18",
        "pub_year": 2023,
        "venue": "arXiv preprint",
        "citation_count": 1200,
        "markdown_content": (
            "# Retrieval-Augmented Generation for Large Language Models: A Survey\n\n"
            "## Abstract\n\n"
            "LLMs face challenges including hallucination, outdated knowledge, and non-transparent reasoning. "
            "RAG has emerged as a promising solution by incorporating external knowledge. This survey provides "
            "a comprehensive overview of the RAG paradigm.\n\n"
            "## Introduction\n\n"
            "The rapid development of large language models has transformed natural language processing. "
            "However, LLMs suffer from generating factually incorrect content (hallucination) and cannot "
            "update their knowledge after training. RAG addresses these limitations by retrieving relevant "
            "information from external sources at inference time.\n\n"
            "## Methodology\n\n"
            "We categorize RAG approaches into three paradigms: Naive RAG follows a simple retrieve-then-read "
            "pipeline. Advanced RAG introduces pre-retrieval and post-retrieval optimizations including query "
            "rewriting, re-ranking, and context compression. Modular RAG provides a flexible framework where "
            "retrieval, generation, and augmentation modules can be composed in various configurations.\n\n"
            "## Experiments\n\n"
            "We survey evaluation benchmarks for RAG systems including RGB, RECALL, and CRUD. Key evaluation "
            "dimensions include relevance, faithfulness, and answer correctness. We analyze 50+ recent papers "
            "and compare their approaches across retrieval strategies, augmentation methods, and generation quality."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Retrieval-Augmented Generation for Large Language Models: A Survey}\n"
            "\\begin{document}\n"
            "\\maketitle\n\n"
            "\\begin{abstract}\n"
            "LLMs face challenges including hallucination, outdated knowledge, and non-transparent reasoning. "
            "RAG has emerged as a promising solution by incorporating external knowledge.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "The rapid development of LLMs has transformed NLP but they suffer from hallucination and "
            "knowledge staleness. RAG addresses these limitations by retrieving relevant information from "
            "external sources at inference time.\n\n"
            "\\section{Methodology}\n"
            "We categorize RAG into three paradigms: Naive RAG (retrieve-then-read), Advanced RAG "
            "(pre-retrieval and post-retrieval optimizations), and Modular RAG (flexible composition of "
            "retrieval, generation, and augmentation modules). We also survey chunking strategies, "
            "embedding models, and vector databases.\n\n"
            "\\section{Experiments}\n"
            "We survey evaluation benchmarks for RAG including RGB, RECALL, and CRUD. Key evaluation "
            "dimensions include relevance, faithfulness, and answer correctness across 50+ papers.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2402.19473",
        "title": "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
        "authors": [
            {"name": "Akari Asai"}, {"name": "Zeqiu Wu"},
            {"name": "Yizhong Wang"}, {"name": "Avirup Sil"},
            {"name": "Hannaneh Hajishirzi"},
        ],
        "categories": ["cs.CL", "cs.AI"],
        "primary_category": "cs.CL",
        "abstract": (
            "Despite their remarkable capabilities, large language models often produce responses containing "
            "inaccurate factual information, which limits their applicability. We introduce Self-RAG, a new "
            "framework that trains a single arbitrary LM to adaptively retrieve passages on-demand, generate "
            "text informed by retrieved passages, and reflect on its own generation using special reflection "
            "tokens. Self-RAG significantly outperforms existing LLMs and RAG models on diverse tasks."
        ),
        "published": "2024-02-29",
        "pub_year": 2024,
        "venue": "ICLR 2024",
        "citation_count": 680,
        "markdown_content": (
            "# Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection\n\n"
            "## Abstract\n\n"
            "We introduce Self-RAG, a framework that trains an LM to adaptively retrieve passages on-demand, "
            "generate text informed by retrieved passages, and reflect on its own generation using special "
            "reflection tokens.\n\n"
            "## Introduction\n\n"
            "Existing RAG approaches indiscriminately retrieve passages regardless of whether retrieval is "
            "necessary, which can degrade generation quality when retrieved passages are irrelevant. Self-RAG "
            "addresses this by training the model to decide when to retrieve, what to retrieve, and how to "
            "use retrieved information through learned self-reflection capabilities.\n\n"
            "## Methodology\n\n"
            "Self-RAG introduces four types of reflection tokens: Retrieve decides whether retrieval is needed, "
            "ISREL assesses the relevance of retrieved passages, ISSUP checks whether the generation is supported "
            "by the passage, and ISUSE evaluates the overall utility of the response. The model is trained using "
            "a critic model to generate reflection tokens and then fine-tuned with these annotations. At inference "
            "time, reflection tokens enable adaptive retrieval and self-assessment without additional models.\n\n"
            "## Experiments\n\n"
            "Self-RAG significantly outperforms existing models on six tasks including open-domain QA, reasoning, "
            "and fact verification. On PopQA, Self-RAG achieves 54.9 accuracy compared to 44.0 for ChatGPT "
            "and 51.2 for standard RAG. The reflection mechanism allows selective retrieval, improving efficiency."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection}\n"
            "\\begin{document}\n"
            "\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We introduce Self-RAG, a framework that trains an LM to adaptively retrieve passages on-demand "
            "and reflect on its own generation using special reflection tokens.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Existing RAG approaches retrieve passages indiscriminately. Self-RAG addresses this by training "
            "the model to decide when and what to retrieve through learned self-reflection.\n\n"
            "\\section{Methodology}\n"
            "Self-RAG introduces four reflection tokens: Retrieve (decide if retrieval is needed), ISREL "
            "(relevance assessment), ISSUP (support verification), and ISUSE (utility evaluation). A critic "
            "model generates reflection token annotations used for training. At inference, these tokens enable "
            "adaptive retrieval without additional models.\n\n"
            "\\section{Experiments}\n"
            "Self-RAG outperforms existing models on six tasks. On PopQA, it achieves 54.9 accuracy vs 44.0 "
            "for ChatGPT. The reflection mechanism enables selective retrieval for improved efficiency.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2310.11511",
        "title": "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval",
        "authors": [
            {"name": "Parth Sarthi"}, {"name": "Salman Abdullah"},
            {"name": "Aditi Tuli"}, {"name": "Shubh Khanna"},
            {"name": "Anna Goldie"}, {"name": "Christopher D. Manning"},
        ],
        "categories": ["cs.CL", "cs.IR"],
        "primary_category": "cs.CL",
        "abstract": (
            "Retrieval-augmented language models typically retrieve only short contiguous text chunks, limiting "
            "holistic understanding of entire documents. We introduce RAPTOR, a novel tree-based retrieval "
            "system that recursively embeds, clusters, and summarizes chunks of text, constructing a tree with "
            "differing levels of summarization from the bottom up. At inference time, RAPTOR retrieves from "
            "this tree, offering context at various levels of abstraction."
        ),
        "published": "2024-01-15",
        "pub_year": 2024,
        "venue": "ICLR 2024",
        "citation_count": 420,
        "markdown_content": (
            "# RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval\n\n"
            "## Abstract\n\n"
            "We introduce RAPTOR, a tree-based retrieval system that recursively embeds, clusters, and "
            "summarizes text chunks, constructing a tree with differing levels of summarization.\n\n"
            "## Introduction\n\n"
            "Standard retrieval approaches chunk documents into fixed-size segments and retrieve the most "
            "similar ones to a query. This approach fails to capture high-level themes and document structure. "
            "RAPTOR addresses this by building a hierarchical tree of summaries that enables retrieval at "
            "multiple levels of abstraction.\n\n"
            "## Methodology\n\n"
            "RAPTOR operates in two phases. In the tree construction phase, leaf nodes are formed from text "
            "chunks which are then embedded and clustered using Gaussian Mixture Models. Each cluster is "
            "summarized by an LLM to form parent nodes. This process repeats recursively until the root "
            "level is reached. In the retrieval phase, RAPTOR supports two strategies: tree traversal "
            "(top-down search through the tree) and collapsed tree (flat search across all tree levels).\n\n"
            "## Experiments\n\n"
            "RAPTOR outperforms traditional retrieval methods on question answering benchmarks including "
            "NarrativeQA and QASPER. On NarrativeQA, RAPTOR with GPT-4 achieves a METEOR score of 30.87 "
            "compared to 23.52 for standard chunk retrieval, demonstrating the value of multi-level abstraction."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval}\n"
            "\\begin{document}\n"
            "\\maketitle\n\n"
            "\\begin{abstract}\n"
            "We introduce RAPTOR, a tree-based retrieval system that recursively embeds, clusters, and "
            "summarizes text chunks for multi-level retrieval.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Standard retrieval chunks documents into fixed-size segments, missing high-level themes. "
            "RAPTOR builds a hierarchical tree of summaries for multi-level abstraction retrieval.\n\n"
            "\\section{Methodology}\n"
            "RAPTOR has two phases: tree construction (embed, cluster with GMMs, summarize recursively) "
            "and retrieval (tree traversal or collapsed tree search). Leaf nodes are text chunks, parent "
            "nodes are LLM-generated summaries of clusters.\n\n"
            "\\section{Experiments}\n"
            "RAPTOR outperforms traditional retrieval on NarrativeQA (METEOR 30.87 vs 23.52) and QASPER, "
            "demonstrating value of hierarchical multi-level abstraction.\n\n"
            "\\end{document}"
        ),
    },
    {
        "arxiv_id": "2404.10981",
        "title": "From RAG to Rich: Building Robust Retrieval-Augmented Generation Systems",
        "authors": [
            {"name": "Wenqi Chen"}, {"name": "Jialin Wu"},
            {"name": "Dawei Zhu"}, {"name": "Xiaoguang Li"},
            {"name": "Shuaiyi Nie"},
        ],
        "categories": ["cs.CL", "cs.SE"],
        "primary_category": "cs.CL",
        "abstract": (
            "As retrieval-augmented generation (RAG) systems move from research prototypes to production "
            "deployments, practitioners face numerous engineering challenges including chunking strategies, "
            "embedding selection, retrieval pipeline design, and evaluation methodology. This paper presents "
            "a systematic framework for building robust RAG systems, covering the full lifecycle from data "
            "ingestion to deployment and monitoring. We provide practical guidelines and empirical analysis "
            "of design choices that significantly impact RAG system quality."
        ),
        "published": "2024-04-16",
        "pub_year": 2024,
        "venue": "arXiv preprint",
        "citation_count": 190,
        "markdown_content": (
            "# From RAG to Rich: Building Robust Retrieval-Augmented Generation Systems\n\n"
            "## Abstract\n\n"
            "As RAG systems move to production, practitioners face engineering challenges in chunking, "
            "embedding, retrieval design, and evaluation. We present a systematic framework for building "
            "robust RAG systems covering the full lifecycle.\n\n"
            "## Introduction\n\n"
            "The success of RAG in research settings has led to widespread adoption in industry. However, "
            "production RAG systems require careful engineering decisions that are not well documented in "
            "the literature. This paper bridges the gap between academic RAG research and practical system "
            "building by providing a comprehensive engineering guide.\n\n"
            "## Methodology\n\n"
            "We organize RAG system design into five pillars: data ingestion (document parsing, chunking "
            "strategies, metadata extraction), indexing (embedding model selection, vector database design, "
            "hybrid search with BM25), retrieval pipeline (query understanding, multi-stage retrieval, "
            "re-ranking), generation (prompt engineering, context window management, citation generation), "
            "and evaluation (automated metrics, human evaluation, regression testing). We conduct ablation "
            "studies on each component to quantify their impact.\n\n"
            "## Experiments\n\n"
            "Our experiments across three domains (legal, medical, technical documentation) show that "
            "chunking strategy has the largest impact on retrieval quality (up to 23% improvement), "
            "followed by embedding model choice (15% improvement) and re-ranking (12% improvement). "
            "Hybrid search combining dense and sparse retrieval consistently outperforms either alone."
        ),
        "latex_content": (
            "\\documentclass{article}\n"
            "\\title{From RAG to Rich: Building Robust Retrieval-Augmented Generation Systems}\n"
            "\\begin{document}\n"
            "\\maketitle\n\n"
            "\\begin{abstract}\n"
            "As RAG systems move to production, practitioners face engineering challenges. We present "
            "a systematic framework covering the full RAG lifecycle.\n"
            "\\end{abstract}\n\n"
            "\\section{Introduction}\n"
            "Production RAG systems require careful engineering decisions not well documented in literature. "
            "This paper bridges the gap between academic RAG research and practical system building.\n\n"
            "\\section{Methodology}\n"
            "We organize design into five pillars: data ingestion (parsing, chunking, metadata), indexing "
            "(embeddings, vector DBs, hybrid search), retrieval pipeline (query understanding, multi-stage, "
            "re-ranking), generation (prompt engineering, context management, citations), and evaluation "
            "(automated metrics, human eval, regression testing).\n\n"
            "\\section{Experiments}\n"
            "Across legal, medical, and technical domains, chunking strategy has the largest impact (23%), "
            "followed by embedding choice (15%) and re-ranking (12%). Hybrid search consistently wins.\n\n"
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
        cur.execute("DELETE FROM arxiv.papers")
    conn.commit()
    print("Cleared scholarly.arxiv_papers, scholarly.scholar_papers, arxiv_latex.papers, arxiv.papers")


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
                p["markdown_content"],
                True,
            ))
    conn.commit()
    print(f"Injected {len(PAPERS)} papers into arxiv.papers")


def inject_arxiv_latex(conn):
    """Inject papers into arxiv_latex.papers.

    full_prompt uses markdown-style headers (# / ##) because the pg_adapter's
    list_sections / extract_section parse '#' headers.  raw_latex keeps the
    original LaTeX source.
    """
    with conn.cursor() as cur:
        for p in PAPERS:
            # Use the markdown_content for full_prompt (# headers)
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
        inject_scholarly_arxiv(conn)
        inject_scholarly_scholar(conn)
        inject_arxiv_papers(conn)
        inject_arxiv_latex(conn)
    finally:
        conn.close()

    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    main()
