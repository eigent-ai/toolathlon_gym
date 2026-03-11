"""
Preprocess for terminal-arxiv-latex-pdf-gsheet-word task.

Clears arxiv_latex and gsheet schemas. Injects 6 papers (4 target + 2 noise) into arxiv_latex.papers.
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
    # 4 target papers
    {
        "id": "2401.00101",
        "title": "Neural Architecture Search with Differentiable Topology Optimization",
        "abstract": "We propose a novel neural architecture search framework that incorporates differentiable topology optimization. Our method formulates NAS as a continuous optimization problem over both network weights and architectural topology, enabling gradient-based search through the space of network structures. We introduce a topology loss function that encourages efficient connectivity patterns. Experiments on CIFAR-10 and ImageNet demonstrate that our approach discovers architectures achieving 97.8% and 79.2% top-1 accuracy respectively, while requiring 3x fewer search GPU-hours than existing methods.",
        "full_prompt": "\\documentclass{article}\n\\title{Neural Architecture Search with Differentiable Topology Optimization}\n\\author{Alice Chen, Bob Zhang, Carol Wang}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nWe propose a novel NAS framework with differentiable topology optimization. Our topology loss $\\mathcal{L}_{topo} = \\sum_{e \\in E} \\alpha_e \\cdot \\text{cost}(e)$ enables gradient-based architecture search. We achieve 97.8\\% on CIFAR-10 and 79.2\\% on ImageNet with 3x fewer GPU-hours.\n\\end{abstract}\n\\section{Introduction}\nNeural Architecture Search (NAS) has emerged as a powerful paradigm for automating network design. However, existing methods suffer from prohibitive search costs. We address this by formulating NAS as continuous topology optimization.\n\\section{Related Work}\nDARTS (Liu et al., 2019) introduced differentiable NAS but ignored topological constraints. ProxylessNAS (Cai et al., 2019) reduced search cost but limited the search space.\n\\section{Method}\nWe define the topology-aware search space $\\mathcal{S} = (V, E, \\alpha)$ where $V$ is the set of operations, $E$ the edges, and $\\alpha$ the architecture parameters. The topology loss is:\n$\\mathcal{L}_{topo} = \\sum_{e \\in E} \\alpha_e \\cdot \\text{cost}(e) + \\lambda \\|\\alpha\\|_1$\nOptimization proceeds via alternating gradient descent on weights $w$ and architecture parameters $\\alpha$.\n\\section{Experiments}\nWe evaluate on CIFAR-10 (97.8\\% accuracy), ImageNet (79.2\\% top-1), and compare search cost. Our method requires 0.3 GPU-days vs 1.0 for DARTS.\n\\subsection{Ablation Studies}\nRemoving the topology loss degrades accuracy by 0.5\\%. The $\\ell_1$ regularization is crucial for sparse architectures.\n\\section{Conclusion}\nDifferentiable topology optimization enables efficient and effective NAS.\n\\end{document}",
        "sections": [
            {"title": "Introduction", "content": "Neural Architecture Search (NAS) has emerged as a powerful paradigm for automating network design. However, existing methods suffer from prohibitive search costs. We address this by formulating NAS as continuous topology optimization."},
            {"title": "Related Work", "content": "DARTS (Liu et al., 2019) introduced differentiable NAS but ignored topological constraints. ProxylessNAS (Cai et al., 2019) reduced search cost but limited the search space."},
            {"title": "Method", "content": "We define the topology-aware search space S = (V, E, alpha) where V is the set of operations, E the edges, and alpha the architecture parameters. The topology loss is L_topo = sum alpha_e * cost(e) + lambda ||alpha||_1. Optimization proceeds via alternating gradient descent on weights w and architecture parameters alpha."},
            {"title": "Experiments", "content": "We evaluate on CIFAR-10 (97.8% accuracy), ImageNet (79.2% top-1), and compare search cost. Our method requires 0.3 GPU-days vs 1.0 for DARTS."},
            {"title": "Ablation Studies", "content": "Removing the topology loss degrades accuracy by 0.5%. The l1 regularization is crucial for sparse architectures."},
            {"title": "Conclusion", "content": "Differentiable topology optimization enables efficient and effective NAS."}
        ],
    },
    {
        "id": "2401.00102",
        "title": "Contrastive Pre-training with Syntactic Augmentation for Low-Resource NLP",
        "abstract": "We present a contrastive pre-training approach that leverages syntactic structure for data augmentation in low-resource NLP settings. By generating syntax-aware positive pairs through dependency tree transformations, our method creates diverse training examples that preserve semantic meaning while varying surface form. Evaluation on four low-resource language benchmarks shows improvements of 3-7% F1 over standard contrastive baselines, with particularly strong gains on morphologically rich languages.",
        "full_prompt": "\\documentclass{article}\n\\title{Contrastive Pre-training with Syntactic Augmentation for Low-Resource NLP}\n\\author{David Kim, Eva Mueller, Frank Li}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nWe present a contrastive pre-training approach using syntactic augmentation for low-resource NLP. Syntax-aware positive pairs via dependency tree transformations yield 3-7\\% F1 improvements.\n\\end{abstract}\n\\section{Introduction}\nLow-resource NLP remains challenging due to limited training data. Contrastive learning has shown promise but relies on surface-level augmentations that may not preserve semantic structure.\n\\section{Method}\nGiven a sentence $x$, we parse its dependency tree $T(x)$ and apply subtree rotation and sibling swap operations to generate augmented examples $x'$. The contrastive loss is:\n$\\mathcal{L} = -\\log \\frac{\\exp(\\text{sim}(z, z')/\\tau)}{\\sum_j \\exp(\\text{sim}(z, z_j)/\\tau)}$\nwhere $z = f(x)$ and $z' = f(x')$ are encoded representations.\n\\section{Experiments}\nWe evaluate on Swahili NER (73.2 F1), Welsh POS tagging (89.1), Basque dependency parsing (81.4 UAS), and Tagalog sentiment (78.6 F1).\n\\section{Analysis}\nSyntactic augmentation is most effective for morphologically rich languages where word order is flexible.\n\\section{Conclusion}\nSyntax-aware contrastive pre-training improves low-resource NLP significantly.\n\\end{document}",
        "sections": [
            {"title": "Introduction", "content": "Low-resource NLP remains challenging due to limited training data. Contrastive learning has shown promise but relies on surface-level augmentations that may not preserve semantic structure."},
            {"title": "Method", "content": "Given a sentence x, we parse its dependency tree T(x) and apply subtree rotation and sibling swap operations to generate augmented examples x'. The contrastive loss uses cosine similarity with temperature scaling."},
            {"title": "Experiments", "content": "We evaluate on Swahili NER (73.2 F1), Welsh POS tagging (89.1), Basque dependency parsing (81.4 UAS), and Tagalog sentiment (78.6 F1)."},
            {"title": "Analysis", "content": "Syntactic augmentation is most effective for morphologically rich languages where word order is flexible."},
            {"title": "Conclusion", "content": "Syntax-aware contrastive pre-training improves low-resource NLP significantly."}
        ],
    },
    {
        "id": "2401.00103",
        "title": "Graph-Augmented Reasoning Networks for Multi-Hop Question Answering",
        "abstract": "We introduce Graph-Augmented Reasoning Networks (GARN), a framework for multi-hop question answering that constructs dynamic reasoning graphs from passage entities. Our attention-based graph reasoning module iteratively refines entity representations through message passing, enabling complex multi-step inference. GARN achieves 74.8 F1 on HotpotQA and 71.2 F1 on MultiRC, outperforming previous graph-based approaches by 2-4 points.",
        "full_prompt": "\\documentclass{article}\n\\title{Graph-Augmented Reasoning Networks for Multi-Hop Question Answering}\n\\author{Grace Park, Henry Adams, Iris Chen}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nWe introduce GARN for multi-hop QA using dynamic reasoning graphs. Attention-based graph reasoning achieves 74.8 F1 on HotpotQA and 71.2 F1 on MultiRC.\n\\end{abstract}\n\\section{Introduction}\nMulti-hop question answering requires reasoning over multiple passages. Graph-based approaches can capture inter-entity relationships but existing methods use static graphs.\n\\section{Method}\nGARN constructs a dynamic entity graph $G = (V_E, E_R)$ where nodes are entity mentions and edges represent co-occurrence and coreference relations. The graph reasoning module applies $K$ rounds of message passing:\n$h_i^{(k+1)} = \\text{GRU}(h_i^{(k)}, \\sum_{j \\in \\mathcal{N}(i)} \\alpha_{ij} W h_j^{(k)})$\nwith attention weights $\\alpha_{ij} = \\text{softmax}(q^T [h_i; h_j; e_{ij}])$.\n\\section{Experiments}\nHotpotQA: 74.8 F1 (distractor setting). MultiRC: 71.2 F1. Ablation shows graph reasoning contributes +3.1 F1.\n\\section{Conclusion}\nDynamic graph construction with attention-based reasoning improves multi-hop QA.\n\\end{document}",
        "sections": [
            {"title": "Introduction", "content": "Multi-hop question answering requires reasoning over multiple passages. Graph-based approaches can capture inter-entity relationships but existing methods use static graphs."},
            {"title": "Method", "content": "GARN constructs a dynamic entity graph G = (V_E, E_R) where nodes are entity mentions and edges represent co-occurrence and coreference relations. The graph reasoning module applies K rounds of message passing with GRU updates and attention weights."},
            {"title": "Experiments", "content": "HotpotQA: 74.8 F1 (distractor setting). MultiRC: 71.2 F1. Ablation shows graph reasoning contributes +3.1 F1."},
            {"title": "Conclusion", "content": "Dynamic graph construction with attention-based reasoning improves multi-hop QA."}
        ],
    },
    {
        "id": "2401.00104",
        "title": "Sparse Mixture-of-Experts for Efficient Transformer Inference",
        "abstract": "We propose a sparse Mixture-of-Experts (MoE) approach for efficient transformer inference. Our method introduces a learned routing mechanism that dynamically activates only a subset of expert modules for each input token, reducing computational cost by approximately 3x while maintaining 98.5% of the original model's accuracy. We validate our approach on machine translation (WMT14 En-De) and language modeling (WikiText-103) tasks.",
        "full_prompt": "\\documentclass{article}\n\\title{Sparse Mixture-of-Experts for Efficient Transformer Inference}\n\\author{Jack Wilson, Karen Liu, Leo Martinez}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nWe propose sparse MoE for efficient transformer inference. Learned routing activates $k$ of $N$ experts per token, achieving 3x speedup with 98.5\\% accuracy retention.\n\\end{abstract}\n\\section{Introduction}\nTransformer models have grown dramatically in size. Efficient inference is critical for deployment. Mixture-of-Experts offers conditional computation but existing routing is suboptimal.\n\\section{Method}\nOur routing function selects top-$k$ experts: $g(x) = \\text{TopK}(\\text{softmax}(W_g x + \\epsilon), k)$ where $\\epsilon \\sim \\mathcal{N}(0, \\sigma^2)$ adds noise for load balancing. The output is:\n$y = \\sum_{i \\in \\text{TopK}} g_i(x) \\cdot E_i(x)$\nWe use an auxiliary load balancing loss $\\mathcal{L}_{bal} = N \\sum_{i=1}^N f_i \\cdot P_i$.\n\\section{Experiments}\nWMT14 En-De: 28.1 BLEU (vs 28.4 baseline), 3.1x speedup. WikiText-103: 18.2 perplexity (vs 17.9 baseline), 2.8x speedup.\n\\section{Conclusion}\nSparse MoE enables practical efficient inference for large transformers.\n\\end{document}",
        "sections": [
            {"title": "Introduction", "content": "Transformer models have grown dramatically in size. Efficient inference is critical for deployment. Mixture-of-Experts offers conditional computation but existing routing is suboptimal."},
            {"title": "Method", "content": "Our routing function selects top-k experts with softmax gating and Gaussian noise for load balancing. The output combines selected expert outputs weighted by gate values. An auxiliary load balancing loss ensures even expert utilization."},
            {"title": "Experiments", "content": "WMT14 En-De: 28.1 BLEU (vs 28.4 baseline), 3.1x speedup. WikiText-103: 18.2 perplexity (vs 17.9 baseline), 2.8x speedup."},
            {"title": "Conclusion", "content": "Sparse MoE enables practical efficient inference for large transformers."}
        ],
    },
    # 2 noise papers
    {
        "id": "2401.00201",
        "title": "Federated Learning with Differential Privacy for Medical Imaging",
        "abstract": "We study federated learning with differential privacy guarantees for medical image classification. Our approach combines secure aggregation with gradient clipping to achieve (epsilon, delta)-differential privacy while training on distributed hospital datasets.",
        "full_prompt": "\\documentclass{article}\n\\title{Federated Learning with Differential Privacy for Medical Imaging}\n\\author{Noah Brown, Olivia Davis}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nFederated learning with differential privacy for medical imaging.\n\\end{abstract}\n\\section{Introduction}\nMedical imaging data is sensitive and distributed across hospitals.\n\\section{Method}\nSecure aggregation with gradient clipping for (epsilon, delta)-DP.\n\\section{Experiments}\nChest X-ray classification with 5 hospital sites.\n\\section{Conclusion}\nPrivacy-preserving federated learning is feasible for medical imaging.\n\\end{document}",
        "sections": [
            {"title": "Introduction", "content": "Medical imaging data is sensitive and distributed across hospitals."},
            {"title": "Method", "content": "Secure aggregation with gradient clipping for differential privacy."},
            {"title": "Experiments", "content": "Chest X-ray classification with 5 hospital sites."},
            {"title": "Conclusion", "content": "Privacy-preserving federated learning is feasible for medical imaging."}
        ],
    },
    {
        "id": "2401.00202",
        "title": "Reinforcement Learning for Robotic Manipulation with Tactile Feedback",
        "abstract": "We present a reinforcement learning framework for robotic manipulation that incorporates tactile sensor feedback. Our reward shaping approach based on tactile contact patterns improves grasping success rate from 72% to 91% on a set of 50 household objects.",
        "full_prompt": "\\documentclass{article}\n\\title{Reinforcement Learning for Robotic Manipulation with Tactile Feedback}\n\\author{Paul Green, Quinn Harris}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\nRL for robotic manipulation with tactile feedback improves grasping from 72\\% to 91\\%.\n\\end{abstract}\n\\section{Introduction}\nRobotic grasping remains challenging for deformable and fragile objects.\n\\section{Method}\nTactile reward shaping: $r_t = r_{task} + \\beta \\cdot r_{tactile}$.\n\\section{Experiments}\n50 household objects, 91\\% grasp success rate.\n\\section{Conclusion}\nTactile feedback significantly improves RL-based manipulation.\n\\end{document}",
        "sections": [
            {"title": "Introduction", "content": "Robotic grasping remains challenging for deformable and fragile objects."},
            {"title": "Method", "content": "Tactile reward shaping combines task reward with tactile contact reward."},
            {"title": "Experiments", "content": "50 household objects, 91% grasp success rate."},
            {"title": "Conclusion", "content": "Tactile feedback significantly improves RL-based manipulation."}
        ],
    },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear writable schemas
        cur.execute("DELETE FROM arxiv_latex.papers")
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        conn.commit()
        print("[preprocess] Cleared arxiv_latex and gsheet tables.")

        # Inject papers
        for p in PAPERS:
            cur.execute("""
                INSERT INTO arxiv_latex.papers (id, title, abstract, full_prompt, sections)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    abstract = EXCLUDED.abstract,
                    full_prompt = EXCLUDED.full_prompt,
                    sections = EXCLUDED.sections
            """, (
                p["id"], p["title"], p["abstract"],
                p["full_prompt"], json.dumps(p["sections"]),
            ))
        conn.commit()
        print(f"[preprocess] Injected {len(PAPERS)} papers into arxiv_latex.papers")

    finally:
        cur.close()
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
