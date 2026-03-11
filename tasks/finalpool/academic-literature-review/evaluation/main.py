"""
Evaluation script for academic-literature-review task.
Checks that Literature_Review.docx exists and contains the expected content.

Usage:
  python -m evaluation.main --agent_workspace <path> --groundtruth_workspace <path> --launch_time <time>
"""
import argparse
import os
import re
import sys


PASS_COUNT = 0
FAIL_COUNT = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_truncated = (detail[:200] + "...") if len(detail) > 200 else detail
        print(f"  [FAIL] {name}: {detail_truncated}")


def normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, collapse whitespace."""
    return re.sub(r'\s+', ' ', text.lower().strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=True)
    parser.add_argument("--groundtruth_workspace", type=str, required=True)
    parser.add_argument("--launch_time", type=str, required=False)
    parser.add_argument("--res_log_file", type=str, required=False)
    args = parser.parse_args()

    docx_path = os.path.join(args.agent_workspace, "Literature_Review.docx")

    # Check 1: File exists
    check("Literature_Review.docx exists", os.path.exists(docx_path),
          f"File not found at {docx_path}")

    if not os.path.exists(docx_path):
        print(f"\nResults: {PASS_COUNT}/{PASS_COUNT + FAIL_COUNT} passed, {FAIL_COUNT} failed")
        sys.exit(1)

    # Read the Word document
    try:
        from docx import Document
        doc = Document(docx_path)
        full_text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        check("Word document readable", False, str(e))
        print(f"\nResults: {PASS_COUNT}/{PASS_COUNT + FAIL_COUNT} passed, {FAIL_COUNT} failed")
        sys.exit(1)

    normalized = normalize(full_text)

    # Check 2: Minimum content length
    check("Document has at least 500 characters",
          len(full_text.strip()) >= 500,
          f"Document has {len(full_text.strip())} characters")

    # Check 3: All 5 paper titles appear (case-insensitive partial match)
    # These papers must match the papers injected by preprocess/main.py
    # into arxiv/scholarly schemas.
    paper_titles = [
        "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "Retrieval-Augmented Generation for Large Language Models: A Survey",
        "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
        "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval",
        "From RAG to Rich",
    ]
    for title in paper_titles:
        title_lower = title.lower()
        check(f"Paper title present: {title[:60]}...",
              title_lower in normalized,
              "Title not found in document text")

    # Check 4: All 5 first authors appear
    # These authors must match the papers injected by preprocess/main.py
    # into arxiv/scholarly schemas.
    first_authors = ["Lewis", "Gao", "Asai", "Sarthi", "Chen"]
    for author in first_authors:
        check(f"Author present: {author}",
              author.lower() in normalized,
              f"Author '{author}' not found in document text")

    # Check 5: Key domain terms present
    key_terms = ["retrieval", "generation", "augmented"]
    for term in key_terms:
        check(f"Key term present: {term}",
              term.lower() in normalized,
              f"Term '{term}' not found")

    # Check 6: Document has structure (introduction/conclusion indicators)
    has_intro = "introduction" in normalized
    has_conclusion = "conclusion" in normalized or "summary" in normalized or "synthesis" in normalized
    check("Document has introduction section", has_intro,
          "No 'introduction' found in text")
    check("Document has conclusion/summary section", has_conclusion,
          "No 'conclusion' or 'summary' found in text")

    # Summary
    total = PASS_COUNT + FAIL_COUNT
    print(f"\nResults: {PASS_COUNT}/{total} passed, {FAIL_COUNT} failed")

    sys.exit(0 if FAIL_COUNT == 0 else 1)


if __name__ == "__main__":
    main()
