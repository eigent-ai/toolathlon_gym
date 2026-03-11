"""Evaluation for wc-product-catalog-word."""
import argparse
import os
import sys
from docx import Document


# Expected catalog items and their match status
# When doing case-insensitive substring match against WC products:
EXPECTED_MATCHING = [
    "Canon M50 Mark II",
    "JBL Flip 4 Portable Wireless Speaker",
    "Boult Audio Powerbuds",
    "AmazonBasics Expanding File Folder",
    "CraftDev A500MB Portable Paper Trimmer",
    "AGARO Adjustable Camera Tripod Stand",
    "Ambrane Mobile Holding Tabletop Stand",
]

EXPECTED_MISSING = [
    "Belkin Ultra HD High Speed HDMI Cable",
    "Sony WH-1000XM5 Wireless Headphones",
    "Logitech MX Master 3S Mouse",
    "Samsung T7 Shield Portable SSD 1TB",
    "Anker PowerCore 26800mAh Battery Pack",
]

TOTAL_CATALOG = 12


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    all_errors = []

    agent_doc = os.path.join(args.agent_workspace, "Product_Comparison.docx")
    if not os.path.exists(agent_doc):
        print("FAIL: Agent output Product_Comparison.docx not found")
        sys.exit(1)

    doc = Document(agent_doc)

    # Extract all text
    all_text = ""
    headings = []
    paragraphs_by_section = {}
    current_section = ""
    for para in doc.paragraphs:
        text = para.text.strip()
        all_text += text.lower() + " "
        if para.style.name.startswith("Heading"):
            current_section = text.lower()
            headings.append(text.lower())
            paragraphs_by_section[current_section] = []
        elif current_section and text:
            paragraphs_by_section.setdefault(current_section, []).append(text)

    # Check document structure
    print("  Checking document structure...")
    has_matching = any("matching" in h for h in headings)
    has_missing = any("missing" in h for h in headings)
    has_summary = any("summary" in h for h in headings)

    if not has_matching:
        all_errors.append("Missing 'Matching Products' heading")
    if not has_missing:
        all_errors.append("Missing 'Missing Products' heading")
    if not has_summary:
        all_errors.append("Missing 'Summary' heading")

    # Check matching products section
    print("  Checking matching products...")
    matching_text = ""
    for key, paras in paragraphs_by_section.items():
        if "matching" in key:
            matching_text = " ".join(paras).lower()
            break

    found_matching = 0
    for product in EXPECTED_MATCHING:
        # Check if product name appears (case-insensitive) in the matching section
        if product.lower() in matching_text:
            found_matching += 1
        else:
            # Also check entire document in case section detection is off
            if product.lower() in all_text:
                found_matching += 1
            else:
                all_errors.append(f"Matching product not found: {product}")

    # Allow some tolerance - at least 5 of 7 matching products
    if found_matching < 5:
        all_errors.append(f"Only {found_matching}/7 matching products found")
    else:
        print(f"    {found_matching}/7 matching products found")

    # Check missing products section
    print("  Checking missing products...")
    missing_text = ""
    for key, paras in paragraphs_by_section.items():
        if "missing" in key:
            missing_text = " ".join(paras).lower()
            break

    found_missing = 0
    for product in EXPECTED_MISSING:
        if product.lower() in missing_text or product.lower() in all_text:
            found_missing += 1
        else:
            all_errors.append(f"Missing product not listed: {product}")

    # Allow tolerance - at least 3 of 5 missing products
    if found_missing < 3:
        all_errors.append(f"Only {found_missing}/5 missing products found")
    else:
        print(f"    {found_missing}/5 missing products found")

    # Check summary section
    print("  Checking summary...")
    summary_text = ""
    for key, paras in paragraphs_by_section.items():
        if "summary" in key:
            summary_text = " ".join(paras).lower()
            break

    if not summary_text:
        summary_text = all_text  # fallback

    if "12" not in summary_text:
        all_errors.append("Summary should mention 12 total catalog products")

    if all_errors:
        print(f"\n=== RESULT: FAIL ({len(all_errors)} errors) ===")
        for e in all_errors[:15]:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("\n=== RESULT: PASS ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
