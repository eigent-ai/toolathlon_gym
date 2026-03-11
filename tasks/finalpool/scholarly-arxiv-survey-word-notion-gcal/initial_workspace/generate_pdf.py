"""Generate Survey_Guidelines.pdf for initial_workspace."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Survey_Guidelines.pdf")


def main():
    doc = SimpleDocTemplate(OUTPUT, pagesize=letter,
                            leftMargin=1*inch, rightMargin=1*inch,
                            topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=18, spaceAfter=20)
    heading_style = ParagraphStyle("HeadingCustom", parent=styles["Heading2"], fontSize=14, spaceAfter=10, spaceBefore=16)
    body_style = ParagraphStyle("BodyCustom", parent=styles["Normal"], fontSize=11, spaceAfter=8, leading=15)

    story = []

    story.append(Paragraph("Literature Survey Writing Guide", title_style))
    story.append(Paragraph("LLM Reasoning Methods", heading_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Survey Scope</b>", heading_style))
    story.append(Paragraph(
        "This survey should cover reasoning methods for large language models, including but not limited to: "
        "chain-of-thought prompting, tree-of-thought reasoning, self-consistency decoding, process supervision "
        "and step-by-step verification, and automatic chain-of-thought generation. The goal is to provide a "
        "comprehensive overview of techniques that enable LLMs to perform multi-step reasoning.",
        body_style))

    story.append(Paragraph("<b>Required Sections</b>", heading_style))
    sections = [
        "Abstract: A 150-200 word summary of the survey scope, methods covered, and key findings.",
        "Introduction: Motivation for studying LLM reasoning, the scope of this survey, and its contributions.",
        "Background: Fundamentals of large language models, in-context learning, and prompting paradigms.",
        "Taxonomy of Methods: Organized subsections for each reasoning approach. Group methods by category "
        "(prompting-based, search-based, verification-based). Each subsection should cover one specific method.",
        "Comparative Analysis: A structured comparison of all methods. Include a table with columns for method name, "
        "source paper, accuracy improvement over baseline, computational cost, and task generality.",
        "Open Challenges: Current limitations, unsolved problems, and promising future research directions.",
        "Conclusion: Summary of key findings, practical recommendations, and outlook for the field.",
    ]
    for s in sections:
        story.append(Paragraph(f"&bull; {s}", body_style))

    story.append(Paragraph("<b>Per-Paper Requirements</b>", heading_style))
    story.append(Paragraph(
        "For each paper covered in the survey, you should summarize: (1) the key contribution and novelty, "
        "(2) the methodology and approach, (3) the main experimental results and benchmarks used. "
        "Reference the paper by title and authors.",
        body_style))

    story.append(Paragraph("<b>Comparative Table Format</b>", heading_style))
    story.append(Paragraph(
        "The comparative analysis section must include a table with the following columns: "
        "Method Name, Paper Title, Accuracy Improvement (percentage or qualitative), "
        "Computational Cost (e.g., number of samples, API calls), and Task Generality "
        "(narrow vs. broad applicability).",
        body_style))

    story.append(Paragraph("<b>Minimum Coverage</b>", heading_style))
    story.append(Paragraph(
        "The survey must cover at least 5 distinct reasoning methods from at least 5 different papers. "
        "Each method should be discussed in its own subsection within the Taxonomy of Methods section.",
        body_style))

    doc.build(story)
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()
