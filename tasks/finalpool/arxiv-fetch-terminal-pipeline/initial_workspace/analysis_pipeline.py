"""
Paper analysis pipeline.
Reads paper_data.json, computes statistics, and writes analysis_results.json.
"""
import json
import os
import sys

def main():
    workspace = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(workspace, "paper_data.json")
    output_path = os.path.join(workspace, "analysis_results.json")

    if not os.path.exists(input_path):
        print(f"ERROR: {input_path} not found. Please create paper_data.json first.")
        sys.exit(1)

    with open(input_path, "r") as f:
        papers = json.load(f)

    if not isinstance(papers, list) or len(papers) == 0:
        print("ERROR: paper_data.json should contain a non-empty list of papers.")
        sys.exit(1)

    # Compute statistics
    total_papers = len(papers)
    citation_counts = [p.get("citation_count", 0) for p in papers]
    total_citations = sum(citation_counts)
    avg_citations = total_citations / total_papers if total_papers > 0 else 0
    max_citations = max(citation_counts) if citation_counts else 0
    min_citations = min(citation_counts) if citation_counts else 0

    # Find most cited paper
    most_cited = max(papers, key=lambda p: p.get("citation_count", 0))

    # Compute average abstract length
    abstract_lengths = [len(p.get("abstract", "")) for p in papers]
    avg_abstract_length = sum(abstract_lengths) / total_papers if total_papers > 0 else 0

    # Compute author count stats
    author_counts = [len(p.get("authors", [])) for p in papers]
    avg_authors = sum(author_counts) / total_papers if total_papers > 0 else 0

    results = {
        "total_papers": total_papers,
        "total_citations": total_citations,
        "average_citations": round(avg_citations, 1),
        "max_citations": max_citations,
        "min_citations": min_citations,
        "most_cited_paper": most_cited.get("title", ""),
        "most_cited_arxiv_id": most_cited.get("arxiv_id", ""),
        "average_abstract_length": round(avg_abstract_length, 1),
        "average_authors": round(avg_authors, 1),
        "paper_titles": [p.get("title", "") for p in papers],
        "paper_arxiv_ids": [p.get("arxiv_id", "") for p in papers],
    }

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Analysis complete. Results written to {output_path}")
    print(f"  Total papers: {total_papers}")
    print(f"  Total citations: {total_citations}")
    print(f"  Most cited: {most_cited.get('title', 'N/A')}")


if __name__ == "__main__":
    main()
