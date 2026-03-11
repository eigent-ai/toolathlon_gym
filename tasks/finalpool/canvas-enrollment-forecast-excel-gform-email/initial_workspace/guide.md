# Enrollment Forecast Guide

## Data Source
Course and enrollment data is stored in the learning management system. Each course has a name that includes the semester and year in parentheses, e.g., "Applied Analytics & Algorithms (Fall 2013)".

## Semester Naming Convention
- Course codes use a suffix: J = Fall, B = Spring
- Example: AAA-2013J = Applied Analytics & Algorithms, Fall 2013
- Example: BBB-2014B = Biochemistry & Bioinformatics, Spring 2014

## Extracting Base Course Name
Remove the semester/year parenthetical from the full course name:
- "Applied Analytics & Algorithms (Fall 2013)" -> "Applied Analytics & Algorithms"
- "Biochemistry & Bioinformatics (Spring 2014)" -> "Biochemistry & Bioinformatics"

## Enrollment Types
- StudentEnrollment: Regular students enrolled in the course
- TeacherEnrollment: Faculty/instructors assigned to the course
- TaEnrollment: Teaching assistants assigned to the course

## Forecasting Methodology
1. Collect all offerings of the same base course sorted chronologically
2. Use linear regression on the student counts to project the next offering
3. If only one data point exists, use that as the projection
4. Round projections to whole numbers

## Sorting
- Sort by Course_Base_Name alphabetically
- Within the same course, sort by Year ascending, then Semester (Spring before Fall)
