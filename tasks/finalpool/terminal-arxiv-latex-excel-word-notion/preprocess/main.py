"""
Preprocess for terminal-arxiv-latex-excel-word-notion task.

Injects 5 transformer papers + 3 noise papers into arxiv and arxiv_latex schemas.
Clears notion tables.
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
    # 5 transformer papers
    {
        "arxiv_id": "1706.03762",
        "title": "Attention Is All You Need",
        "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}, {"name": "Niki Parmar"}],
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. The Transformer achieves 28.4 BLEU on the WMT 2014 English-to-German translation task.",
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "published": "2017-06-12",
        "markdown_content": "# Attention Is All You Need\n\n## Introduction\nWe propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output.\n\n## Model Architecture\nThe Transformer follows an encoder-decoder structure using stacked self-attention and point-wise fully connected layers. Multi-head attention allows the model to jointly attend to information from different representation subspaces.\n\n## Experiments\nOn WMT 2014 English-to-German, the big transformer achieves 28.4 BLEU, establishing a new state of the art. Training took 3.5 days on 8 P100 GPUs.\n\n## Conclusion\nThe Transformer is the first transduction model relying entirely on self-attention, replacing recurrent layers. It can be trained significantly faster than architectures based on recurrent or convolutional layers.",
        "latex_content": "\\documentclass{article}\n\\title{Attention Is All You Need}\n\\author{Ashish Vaswani et al.}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nWe propose a new network architecture, the Transformer, based solely on attention mechanisms.\n\\end{abstract}\n\\section{Introduction}\nThe Transformer eschews recurrence, relying entirely on self-attention.\n\\section{Model Architecture}\nMulti-head attention: $\\text{MultiHead}(Q,K,V) = \\text{Concat}(head_1,...,head_h)W^O$. Positional encoding uses sinusoidal functions.\n\\section{Experiments}\n28.4 BLEU on WMT 2014 en-de. Training: 3.5 days on 8 P100 GPUs.\n\\section{Conclusion}\nFirst transduction model based entirely on self-attention.\n\\end{document}",
        "sections": ["Introduction", "Model Architecture", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": [{"name": "Jacob Devlin"}, {"name": "Ming-Wei Chang"}, {"name": "Kenton Lee"}],
        "abstract": "We introduce BERT, which stands for Bidirectional Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context. The pre-trained BERT model can be fine-tuned with just one additional output layer to create state-of-the-art models for a wide range of tasks.",
        "categories": ["cs.CL"],
        "primary_category": "cs.CL",
        "published": "2018-10-11",
        "markdown_content": "# BERT: Pre-training of Deep Bidirectional Transformers\n\n## Introduction\nWe introduce BERT, pre-trained bidirectional representations from unlabeled text.\n\n## Method\nBERT uses two pre-training objectives: Masked Language Model (MLM) randomly masks 15% of tokens and predicts them, and Next Sentence Prediction (NSP) determines if two sentences are consecutive.\n\n## Experiments\nBERT obtains new state-of-the-art results on eleven NLP tasks including GLUE (80.5%), SQuAD 1.1 (93.2 F1), and SQuAD 2.0 (83.1 F1).\n\n## Conclusion\nBidirectional pre-training is crucial for language understanding. BERT advances the state of the art for eleven NLP tasks.",
        "latex_content": "\\documentclass{article}\n\\title{BERT: Pre-training of Deep Bidirectional Transformers}\n\\author{Jacob Devlin et al.}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nWe introduce BERT for pre-training bidirectional representations. Fine-tuning BERT achieves SOTA on 11 NLP tasks.\n\\end{abstract}\n\\section{Introduction}\nBERT pre-trains bidirectional representations by conditioning on both left and right context.\n\\section{Method}\nMLM: randomly mask 15\\% of tokens. NSP: predict if two sentences are consecutive. Architecture based on Transformer encoder (Vaswani et al., 2017).\n\\section{Experiments}\nGLUE: 80.5\\%, SQuAD 1.1: 93.2 F1, SQuAD 2.0: 83.1 F1.\n\\section{Conclusion}\nBidirectional pre-training advances SOTA for 11 NLP tasks.\n\\end{document}",
        "sections": ["Introduction", "Method", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2005.14165",
        "title": "Language Models are Few-Shot Learners",
        "authors": [{"name": "Tom Brown"}, {"name": "Benjamin Mann"}, {"name": "Nick Ryder"}],
        "abstract": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes reaching competitiveness with prior state-of-the-art fine-tuning approaches. GPT-3, an autoregressive language model with 175 billion parameters, achieves strong performance on many NLP datasets without any gradient updates or fine-tuning.",
        "categories": ["cs.CL"],
        "primary_category": "cs.CL",
        "published": "2020-05-28",
        "markdown_content": "# Language Models are Few-Shot Learners\n\n## Introduction\nWe train GPT-3, a 175B parameter autoregressive transformer language model, and evaluate its few-shot performance.\n\n## Approach\nGPT-3 uses a standard transformer decoder architecture (Vaswani et al., 2017) scaled to 175B parameters. We evaluate in three settings: few-shot, one-shot, and zero-shot, compared to BERT (Devlin et al., 2018) and other fine-tuned models.\n\n## Results\nGPT-3 achieves strong few-shot results on NLP benchmarks. On SuperGLUE, few-shot GPT-3 approaches fine-tuned BERT performance. On translation, it achieves competitive BLEU scores.\n\n## Conclusion\nScaling improves in-context learning. Few-shot GPT-3 is competitive with fine-tuned approaches.",
        "latex_content": "\\documentclass{article}\n\\title{Language Models are Few-Shot Learners}\n\\author{Tom Brown et al.}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nGPT-3, a 175B parameter autoregressive LM, achieves strong few-shot performance without fine-tuning.\n\\end{abstract}\n\\section{Introduction}\nWe train GPT-3 using the Transformer decoder architecture scaled to 175B parameters.\n\\section{Approach}\nAutoregressive LM with Transformer decoder (Vaswani et al., 2017). Comparison with BERT (Devlin et al., 2018).\n\\section{Results}\nCompetitive with fine-tuned BERT on SuperGLUE in few-shot setting.\n\\section{Conclusion}\nScaling dramatically improves in-context learning abilities.\n\\end{document}",
        "sections": ["Introduction", "Approach", "Results", "Conclusion"],
    },
    {
        "arxiv_id": "2010.11929",
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        "authors": [{"name": "Alexey Dosovitskiy"}, {"name": "Lucas Beyer"}, {"name": "Alexander Kolesnikov"}],
        "abstract": "While the Transformer architecture has become the de-facto standard for NLP tasks, its applications to computer vision remain limited. We show that a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks, attaining state-of-the-art results when pre-trained on large datasets.",
        "categories": ["cs.CV", "cs.LG"],
        "primary_category": "cs.CV",
        "published": "2020-10-22",
        "markdown_content": "# An Image is Worth 16x16 Words\n\n## Introduction\nWe apply the Transformer architecture (Vaswani et al., 2017) directly to image recognition. Following pre-training approaches similar to BERT (Devlin et al., 2018), we show pure transformers achieve excellent results.\n\n## Method\nViT splits an image into fixed-size 16x16 patches, linearly embeds them, adds position embeddings, and feeds the sequence to a standard Transformer encoder.\n\n## Experiments\nViT-Large/16 achieves 87.76% on ImageNet when pre-trained on JFT-300M. This is competitive with state-of-the-art CNNs while being more computationally efficient.\n\n## Conclusion\nTransformers can replace CNNs for image recognition when pre-trained at sufficient scale.",
        "latex_content": "\\documentclass{article}\n\\title{An Image is Worth 16x16 Words}\n\\author{Alexey Dosovitskiy et al.}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nA pure transformer applied to image patches performs very well on image classification.\n\\end{abstract}\n\\section{Introduction}\nWe apply the Transformer (Vaswani et al., 2017) to images, using pre-training like BERT (Devlin et al., 2018).\n\\section{Method}\nViT: split image into 16x16 patches, embed, add positions, feed to Transformer encoder.\n\\section{Experiments}\nViT-L/16: 87.76\\% on ImageNet (pre-trained on JFT-300M).\n\\section{Conclusion}\nTransformers can replace CNNs for vision with sufficient pre-training.\n\\end{document}",
        "sections": ["Introduction", "Method", "Experiments", "Conclusion"],
    },
    {
        "arxiv_id": "2301.07041",
        "title": "Scaling Laws for Neural Language Models",
        "authors": [{"name": "Jared Kaplan"}, {"name": "Sam McCandlish"}, {"name": "Tom Henighan"}],
        "abstract": "We study empirical scaling laws for language model performance on cross-entropy loss. The loss scales as a power-law with model size, dataset size, and compute. Using the Transformer architecture (Vaswani et al., 2017) and models at the scale studied in GPT-3 (Brown et al., 2020), we find consistent scaling behavior.",
        "categories": ["cs.LG", "cs.CL"],
        "primary_category": "cs.LG",
        "published": "2023-01-17",
        "markdown_content": "# Scaling Laws for Neural Language Models\n\n## Introduction\nWe study scaling laws for Transformer language models (Vaswani et al., 2017) at scales up to those used in GPT-3 (Brown et al., 2020).\n\n## Scaling Laws\nCross-entropy loss L follows power laws: L(N) = (N_c/N)^alpha_N with alpha_N = 0.076. Similar laws hold for dataset size and compute.\n\n## Experiments\nOver 1000 models trained spanning 3 orders of magnitude confirm power-law scaling.\n\n## Conclusion\nScaling laws predict performance and guide optimal compute allocation.",
        "latex_content": "\\documentclass{article}\n\\title{Scaling Laws for Neural Language Models}\n\\author{Jared Kaplan et al.}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nWe study scaling laws for Transformer (Vaswani et al., 2017) language models at GPT-3 scale (Brown et al., 2020).\n\\end{abstract}\n\\section{Introduction}\nScaling laws for neural language models using Transformer architecture.\n\\section{Scaling Laws}\nL(N) = (N_c/N)^{0.076}. Power-law relationships govern loss vs model size, data, compute.\n\\section{Experiments}\nOver 1000 models confirm power-law scaling.\n\\section{Conclusion}\nPredictable scaling guides optimal compute allocation.\n\\end{document}",
        "sections": ["Introduction", "Scaling Laws", "Experiments", "Conclusion"],
    },
    # 3 noise papers (non-transformer)
    {
        "arxiv_id": "1901.02860",
        "title": "Adversarial Examples Are Not Bugs, They Are Features",
        "authors": [{"name": "Andrew Ilyas"}, {"name": "Shibani Santurkar"}],
        "abstract": "We demonstrate that adversarial examples arise from features rather than bugs in the models.",
        "categories": ["cs.LG", "cs.CV"],
        "primary_category": "cs.LG",
        "published": "2019-01-09",
        "markdown_content": "# Adversarial Examples\n\n## Introduction\nAdversarial examples represent features, not bugs.\n\n## Method\nWe construct robust and non-robust feature datasets.\n\n## Results\nModels trained on non-robust features are vulnerable.\n\n## Conclusion\nAdversarial vulnerability is a feature, not a bug.",
        "latex_content": "\\documentclass{article}\n\\title{Adversarial Examples Are Not Bugs}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\nAdversarial features.\n\\section{Method}\nRobust vs non-robust features.\n\\end{document}",
        "sections": ["Introduction", "Method", "Results", "Conclusion"],
    },
    {
        "arxiv_id": "2002.05709",
        "title": "A Survey on Knowledge Graphs: Representation, Acquisition and Applications",
        "authors": [{"name": "Shaoxiong Ji"}, {"name": "Shirui Pan"}],
        "abstract": "We survey knowledge graph representations, acquisition methods, and downstream applications.",
        "categories": ["cs.AI"],
        "primary_category": "cs.AI",
        "published": "2020-02-13",
        "markdown_content": "# Knowledge Graph Survey\n\n## Introduction\nKnowledge graphs have become important.\n\n## Representation\nTriple-based, graph-based, and embedding-based.\n\n## Applications\nQuestion answering, recommendation, reasoning.",
        "latex_content": "\\documentclass{article}\n\\title{Knowledge Graph Survey}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\nKG survey.\n\\section{Representation}\nTriples and embeddings.\n\\end{document}",
        "sections": ["Introduction", "Representation", "Applications"],
    },
    {
        "arxiv_id": "2106.09685",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "authors": [{"name": "Edward Hu"}, {"name": "Yelong Shen"}],
        "abstract": "We propose Low-Rank Adaptation for efficient fine-tuning of large language models by freezing the pre-trained weights and injecting trainable low-rank decomposition matrices.",
        "categories": ["cs.CL", "cs.LG"],
        "primary_category": "cs.CL",
        "published": "2021-06-17",
        "markdown_content": "# LoRA\n\n## Introduction\nFine-tuning large models is expensive. We propose LoRA.\n\n## Method\nInject low-rank matrices into transformer layers. Freeze original weights.\n\n## Results\nLoRA matches full fine-tuning with 10000x fewer parameters.",
        "latex_content": "\\documentclass{article}\n\\title{LoRA}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\nEfficient adaptation.\n\\section{Method}\nLow-rank decomposition in attention layers.\n\\end{document}",
        "sections": ["Introduction", "Method", "Results"],
    },
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM arxiv.papers")
        cur.execute("DELETE FROM arxiv_latex.papers")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
    conn.commit()
    print("[preprocess] Cleared arxiv, arxiv_latex, and notion tables.")


def inject_arxiv_papers(conn):
    with conn.cursor() as cur:
        for p in PAPERS:
            cur.execute("""
                INSERT INTO arxiv.papers
                (id, title, authors, summary, categories, primary_category,
                 pdf_url, published, is_downloaded, markdown_content)
                VALUES (%s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    summary = EXCLUDED.summary,
                    markdown_content = EXCLUDED.markdown_content
            """, (
                p["arxiv_id"], p["title"], json.dumps(p["authors"]),
                p["abstract"], json.dumps(p["categories"]), p["primary_category"],
                f"http://arxiv.org/pdf/{p['arxiv_id']}",
                p["published"], True, p["markdown_content"],
            ))
    conn.commit()
    print(f"[preprocess] Injected {len(PAPERS)} papers into arxiv.papers")


def inject_arxiv_latex(conn):
    with conn.cursor() as cur:
        for p in PAPERS:
            cur.execute("""
                INSERT INTO arxiv_latex.papers
                (id, title, abstract, full_prompt, sections, raw_latex, processed_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    abstract = EXCLUDED.abstract,
                    full_prompt = EXCLUDED.full_prompt,
                    sections = EXCLUDED.sections,
                    raw_latex = EXCLUDED.raw_latex,
                    processed_at = NOW()
            """, (
                p["arxiv_id"], p["title"], p["abstract"],
                p["markdown_content"], json.dumps(p["sections"]),
                p["latex_content"],
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
        inject_arxiv_papers(conn)
        inject_arxiv_latex(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
