"""
Evaluation script for arxiv-fetch-terminal-pipeline task.

Checks:
1. Memory has entities for papers and research session
2. analysis_results.json exists with correct statistics
3. paper_data.json was created with correct paper data

Usage:
    python -m evaluation.main --agent_workspace <path> --groundtruth_workspace <path>
"""
import argparse
import json
import os
import sys

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def float_close(a, b, tol=50.0):
    """Compare two numeric values with tolerance."""
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


EXPECTED_PAPER_IDS = {"2107.03374", "2002.08155", "2203.07814", "2305.06161"}
EXPECTED_TOTAL_CITATIONS = 9000


def check_memory(agent_workspace):
    """Check that memory.json has entities for papers and research session."""
    print("\n=== Checking Memory ===")

    memory_path = os.path.join(agent_workspace, "memory", "memory.json")
    if not os.path.isfile(memory_path):
        check("memory.json exists", False, f"Not found: {memory_path}")
        return

    check("memory.json exists", True)

    with open(memory_path, "r") as f:
        content = f.read().strip()

    if not content or content == "{}":
        check("Memory has content", False, "memory.json is empty")
        return

    check("Memory has content", True)

    # Memory format from @modelcontextprotocol/server-memory is a knowledge graph
    # with entities and relations
    try:
        memory_data = json.loads(content)
    except json.JSONDecodeError:
        check("Memory is valid JSON", False, "Cannot parse memory.json")
        return

    check("Memory is valid JSON", True)

    # Check for entities
    entities = memory_data.get("entities", [])
    if isinstance(memory_data, list):
        entities = memory_data

    entity_names = []
    entity_text = ""
    for ent in entities:
        if isinstance(ent, dict):
            name = ent.get("name", "")
            entity_names.append(name.lower())
            entity_text += json.dumps(ent).lower() + " "

    # Check for paper entities (at least 3 of 4)
    paper_keywords = ["codex", "codebert", "alphacode", "starcoder",
                       "2107.03374", "2002.08155", "2203.07814", "2305.06161",
                       "code generation", "evaluating large"]
    paper_entity_count = 0
    for kw in paper_keywords:
        if kw in entity_text:
            paper_entity_count += 1

    check("Memory has paper entities (at least 3 keywords found)",
          paper_entity_count >= 3,
          f"Found {paper_entity_count} paper-related keywords in memory entities")

    # Check for research session entity
    has_session = ("research_session" in entity_text or "research session" in entity_text
                   or "session" in entity_text or "code generation" in entity_text)
    check("Memory has research session entity",
          has_session,
          "No research_session entity found")


def check_analysis_results(agent_workspace, groundtruth_workspace):
    """Check analysis_results.json against groundtruth."""
    print("\n=== Checking Analysis Results ===")

    agent_file = os.path.join(agent_workspace, "analysis_results.json")
    gt_file = os.path.join(groundtruth_workspace, "analysis_results.json")

    if not os.path.isfile(agent_file):
        check("analysis_results.json exists", False, f"Not found: {agent_file}")
        return

    check("analysis_results.json exists", True)

    with open(agent_file, "r") as f:
        agent_results = json.load(f)

    check("analysis_results.json is valid JSON", True)

    # Check total papers
    check("Total papers is 4",
          agent_results.get("total_papers") == 4,
          f"Got {agent_results.get('total_papers')}")

    # Check total citations (with tolerance)
    total_cit = agent_results.get("total_citations", 0)
    check("Total citations close to expected",
          float_close(total_cit, EXPECTED_TOTAL_CITATIONS, tol=500),
          f"Got {total_cit}, expected ~{EXPECTED_TOTAL_CITATIONS}")

    # Check most cited paper
    most_cited = (agent_results.get("most_cited_paper", "") or "").lower()
    check("Most cited paper is Codex/Evaluating LLMs",
          "evaluating" in most_cited or "codex" in most_cited or "code" in most_cited,
          f"Got '{most_cited}'")

    # Check paper IDs present
    paper_ids = set(agent_results.get("paper_arxiv_ids", []))
    overlap = paper_ids & EXPECTED_PAPER_IDS
    check("At least 3 of 4 expected paper IDs in results",
          len(overlap) >= 3,
          f"Found {len(overlap)} matching IDs: {overlap}")

    # Check paper titles present
    titles = agent_results.get("paper_titles", [])
    check("At least 3 paper titles in results",
          len(titles) >= 3,
          f"Found {len(titles)} titles")


def check_paper_data(agent_workspace):
    """Check paper_data.json was created."""
    print("\n=== Checking paper_data.json ===")

    paper_data_path = os.path.join(agent_workspace, "paper_data.json")
    if not os.path.isfile(paper_data_path):
        check("paper_data.json exists", False, f"Not found: {paper_data_path}")
        return

    check("paper_data.json exists", True)

    with open(paper_data_path, "r") as f:
        papers = json.load(f)

    check("paper_data.json contains a list", isinstance(papers, list),
          f"Type: {type(papers)}")

    if isinstance(papers, list):
        check("paper_data.json has 4 papers",
              len(papers) == 4,
              f"Found {len(papers)} papers")

        # Check each paper has required fields
        required_fields = ["title", "arxiv_id", "authors", "citation_count", "abstract"]
        for i, paper in enumerate(papers):
            for field in required_fields:
                if field not in paper:
                    check(f"Paper {i+1} has '{field}' field", False, "Missing field")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    task_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    gt_dir = args.groundtruth_workspace or os.path.join(task_root, "groundtruth_workspace")

    check_memory(args.agent_workspace)
    check_analysis_results(args.agent_workspace, gt_dir)
    check_paper_data(args.agent_workspace)

    total = PASS_COUNT + FAIL_COUNT
    print(f"\n=== SUMMARY ===")
    print(f"Results: {PASS_COUNT}/{total} passed, {FAIL_COUNT} failed")

    sys.exit(0 if FAIL_COUNT == 0 else 1)


if __name__ == "__main__":
    main()
