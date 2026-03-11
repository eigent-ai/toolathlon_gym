# Research-Teaching Integration Scoring Rubric

## Alignment Score Calculation

The alignment score measures how well a faculty member's research publications relate to the courses they teach.

1. Extract topic keywords from course syllabus content (minimum 3 characters, exclude common stop words and HTML tags).
2. For each faculty member, retrieve their scholarly publications based on their research area.
3. Count how many of the course keywords appear in at least one paper abstract (case-insensitive matching).
4. Compute the alignment score as: (matched keywords / total course keywords) * 100, rounded to one decimal place.

## Thresholds

- 30% or above: "Aligned" - Faculty research is sufficiently integrated with teaching.
- Below 30%: "Review Needed" - Faculty should consider updating curriculum to better reflect their research, or adjusting research focus.

## Department Aggregation

Department-level scores are the arithmetic mean of all faculty alignment scores within that department, rounded to one decimal place.
