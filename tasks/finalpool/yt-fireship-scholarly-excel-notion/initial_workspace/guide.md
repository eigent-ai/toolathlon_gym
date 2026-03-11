# Guide: Mapping Fireship Videos to Academic Papers

## Overview
This task maps the top 8 most-viewed Fireship YouTube videos to related academic papers found via scholarly search. The output is an Excel workbook and a Notion page summarizing the findings.

## Excel Output Format

### Sheet: Video_Paper_Mapping
This sheet provides a one-row-per-video summary linking each video to its best matching academic paper.

Columns:
- Video_Rank: Integer 1-8 (1 = most viewed)
- Video_Title: Full title of the YouTube video
- Video_Views: View count at time of analysis
- Tech_Topic: Inferred technology topic category (e.g., AI/LLM, DevOps, WebDev)
- Paper_Count: Number of relevant papers found for this topic
- Top_Paper_Title: Title of the highest-cited paper found
- Top_Paper_Year: Publication year of the top paper
- Top_Paper_Citations: Citation count of the top paper

### Sheet: All_Papers
This sheet lists all papers found across all topics.

Columns:
- Tech_Topic: Category this paper was found under
- Paper_Title: Full paper title
- Authors: Author names (comma-separated)
- Year: Publication year
- Citations: Citation count
- Abstract_Snippet: First 200 characters of the abstract

## Notion Page Structure
Create a Notion page titled "Fireship Top Videos - Academic Paper Mapping" with:
1. Introduction paragraph describing the analysis
2. A table matching each video to its top paper
3. Observations section noting any interesting patterns
