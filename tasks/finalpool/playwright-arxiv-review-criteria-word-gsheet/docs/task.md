You are a professor serving as a peer reviewer for a machine learning conference. You have been assigned three papers to review. The conference review portal is available at http://localhost:30214/review_criteria.html and contains the official scoring rubric, including criteria for technical soundness, novelty, clarity, and overall recommendation.

Read the Review_Guidelines.pdf in your workspace for additional context about how to structure your reviews and what the conference expects from reviewers.

First, browse the conference review portal and study the scoring rubric carefully. Note the rating scales and what each score level means.

Then retrieve information about the three assigned papers from the research paper database. The papers are titled "Scaling Laws for Neural Language Models", "Training language models to follow instructions with human feedback", and "OPT: Open Pre-trained Transformer Language Models". Read each paper's full content and abstract. Additionally, examine the LaTeX source of each paper to analyze the methodology sections in more detail, looking at equations, experimental setup, and section structure.

Create three separate Word documents in your workspace, one for each paper review.

The first document should be called "Review_Scaling_Laws.docx". It should contain a heading with the paper title and authors. Then include sections for Summary (2-3 sentences describing the paper's contribution), Technical Soundness (score 1-5 with justification based on the rubric), Novelty (score 1-5 with justification), Clarity (score 1-5 with justification), and Overall Recommendation (Accept, Weak Accept, Borderline, Weak Reject, or Reject with a brief rationale). For this paper, assign Technical Soundness a score of 5, Novelty a score of 4, and Clarity a score of 4. The overall recommendation should be Accept.

The second document should be called "Review_InstructGPT.docx" for the RLHF paper. Follow the same structure. Assign Technical Soundness 5, Novelty 5, and Clarity 4. The overall recommendation should be Accept.

The third document should be called "Review_OPT.docx" for the OPT paper. Follow the same structure. Assign Technical Soundness 4, Novelty 3, and Clarity 5. The overall recommendation should be Weak Accept.

Create a Google Sheet spreadsheet titled "Conference Review Tracker" with a single sheet called "Reviews". The sheet should have columns: Paper_ID, Paper_Title, Technical_Soundness, Novelty, Clarity, Average_Score, Recommendation, Review_Status. Include one row for each of the three papers. Paper_ID should be the arxiv ID. Average_Score is the mean of the three scores rounded to 1 decimal. Review_Status should be "Completed" for all three. Sort rows by Average_Score descending.

When you are finished, call claim_done.
