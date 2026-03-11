# Item Analysis Methodology

## Overview
This guide describes how to compute quiz item difficulty from learning management system data.

## Computing Difficulty from Quiz Submissions
1. Query all quiz submissions for a given quiz
2. Calculate the average score across all submissions
3. Since scores are recorded on a 0-100 percentage scale, compute difficulty as: avg_score / 100
4. Classify: Easy (>0.7), Optimal (0.3-0.7), Hard (<0.3)

## Per-Question Analysis
When per-question scores are not available, use the quiz-level difficulty as a proxy for all questions in that quiz. This assumes uniform question difficulty within a quiz.

## Quality Rating
Count the percentage of questions in the optimal range. Rate: Excellent (>70%), Good (50-70%), Needs Review (<50%).
