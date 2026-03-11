You are an accreditation coordinator preparing a comprehensive curriculum review for an upcoming university accreditation visit. Your job is to audit the institution's courses against accreditation requirements, find supporting scholarly literature, and document everything in a structured compliance matrix and an accreditation report.

Start by fetching the accreditation requirements from the accreditation portal at http://localhost:30238/api/accreditation_requirements.json. This document specifies minimum thresholds for course counts, faculty ratios, assessment types, and scholarly integration that the institution must meet.

Next, connect to the learning management system and retrieve a list of all courses offered by the institution. For each course, gather the course name, the number of enrolled students, the number of assignments, whether the course has quizzes, and the number of discussion topics. Also determine how many faculty members (teachers and teaching assistants combined) are associated with each course.

Using this data, evaluate each course against the accreditation requirements. A course is considered compliant if it has at least one assignment, the student to faculty ratio does not exceed the maximum specified in the requirements, and the course has at least one form of assessment (quiz or assignment). Note which courses are compliant and which are not.

Then search the scholarly literature for research supporting the pedagogical approaches used in the curriculum. Search for papers on the following topics: active learning in higher education, assessment best practices in education, online learning effectiveness, curriculum design frameworks, and student engagement strategies. For each topic, find at least one relevant paper and note its title, authors, and relevance to the curriculum.

Create an Excel file called Curriculum_Review.xlsx in your workspace with three sheets. The first sheet should be called "Course Compliance" with columns for Course_Name, Assignment_Count, Quiz_Count, Discussion_Count, Student_Count, Faculty_Count, Student_Faculty_Ratio, and Compliant (Yes or No based on whether the course meets the accreditation criteria). Include all courses.

The second sheet should be called "Literature Support" with columns for Search_Topic, Paper_Title, Authors, and Relevance_Note. Include at least five rows covering the five pedagogical topics listed above.

The third sheet should be called "Summary" with columns for Metric and Value. Include rows for total courses, compliant courses, non-compliant courses, compliance rate (as a percentage), total faculty across all courses, average student to faculty ratio, and the number of supporting papers found.

Finally, create a page in the team's knowledge base (Notion) titled "Accreditation Review Report" that summarizes the curriculum audit findings. The page should mention the overall compliance rate, highlight any courses that fail to meet requirements, reference the scholarly literature that supports the institution's pedagogical approach, and note any recommendations for improvement before the accreditation visit.

When you have completed all tasks, call claim_done.
