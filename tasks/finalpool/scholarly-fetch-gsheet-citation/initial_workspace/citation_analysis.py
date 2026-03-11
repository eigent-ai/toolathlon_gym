#!/usr/bin/env python3
"""Analyze citation data and compute author impact metrics.
Usage: python citation_analysis.py papers.json
Outputs author statistics as JSON to stdout.
"""
import json, sys

def main():
    with open(sys.argv[1]) as f:
        papers = json.load(f)
    author_stats = {}
    for p in papers:
        for a in p.get("authors", []):
            name = a.get("name", "Unknown")
            if name not in author_stats:
                author_stats[name] = {"total_citations": 0, "paper_count": 0}
            author_stats[name]["total_citations"] += p.get("citation_count", 0)
            author_stats[name]["paper_count"] += 1
    for name, stats in author_stats.items():
        stats["avg_citations"] = round(stats["total_citations"] / max(stats["paper_count"], 1), 1)
    # Sort by total citations desc
    ranked = sorted(author_stats.items(), key=lambda x: x[1]["total_citations"], reverse=True)
    print(json.dumps([{"author": name, **stats} for name, stats in ranked], indent=2))

if __name__ == "__main__":
    main()
