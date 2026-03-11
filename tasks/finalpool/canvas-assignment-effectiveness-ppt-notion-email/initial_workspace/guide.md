# Assignment Effectiveness Analysis Guide

## Overview
This guide explains how to compute Discrimination Index (DI) and other effectiveness metrics for course assignments.

## Step-by-Step Process

### 1. Identify Target Courses
Focus on courses from a specific term (e.g., Fall 2014). Look for course codes ending in '2014J' to identify Fall 2014 courses.

### 2. Gather Submission Data
For each course, collect all graded submissions with non-null scores. You need:
- Assignment ID, name, and points_possible
- Student user_id and score
- Only include submissions where workflow_state = 'graded'

### 3. Determine Enrolled Students
Count enrolled students as the number of unique students who have at least one graded submission in the course.

### 4. Rank Students by Overall Performance
For each course independently:
1. Compute each student's overall course average (mean of all their assignment scores)
2. Sort students by this average from lowest to highest
3. Identify the top 27% and bottom 27% of students

### 5. Compute Discrimination Index
For each assignment:
1. Get the average score of the top 27% group on that assignment
2. Get the average score of the bottom 27% group on that assignment
3. DI = (top_27_avg - bottom_27_avg) / points_possible

### 6. Compute Other Metrics
- **Completion Rate** = (number of submissions / enrolled count) × 100
- **Mean Score** = average of all scores for the assignment
- **Score Std Dev** = population standard deviation of scores

### 7. Classify Effectiveness
- DI > 0.3 → "Good"
- 0.15 ≤ DI ≤ 0.3 → "Acceptable"
- DI < 0.15 → "Poor"

### 8. Flag for Revision
An assignment needs revision if:
- It is rated "Poor" (DI < 0.15), OR
- Its completion rate is below 70%

Priority:
- "High" if BOTH conditions are true
- "Medium" if only ONE condition is true
