I am a teaching assistant for the course "Applied Analytics and Algorithms" and I need to organize office hours for the upcoming week of March 9 through 13, 2026. Please help me with the following.

First, look up the course "Applied Analytics and Algorithms" in the learning management system. Find the course and retrieve the list of enrolled students, collecting their names and email addresses.

Second, check the form titled "Office Hours Booking" where students have already submitted their preferred office hour slots. The form collects each student's name, email, preferred date from March 9 to March 13, preferred time slot, and the topic they want to discuss.

Third, create an Excel file called Office_Hours_Schedule.xlsx in the workspace with two sheets. The first sheet should be named "Bookings" with one row per form response, containing columns for Student_Name, Student_Email, Preferred_Date, Preferred_Time_Slot, and Topic, with rows sorted by Preferred_Date and then by Preferred_Time_Slot. The second sheet should be named "Summary" with one row per date that has bookings, containing columns for Date, Total_Bookings, and Time_Slots where Time_Slots is a comma-separated list of the distinct time slots booked on that date, with rows sorted by Date.

Fourth, for each unique combination of date and time slot from the form responses, create a calendar event on that date during that time slot. Each event should last 30 minutes. Title each event "Office Hours: " followed by one of the topics for that slot. If multiple bookings share the same date and time slot, pick any one topic for the title. Use the timezone America/New_York. In the event description, list all student names who booked that slot.

Fifth, send a confirmation email to each student who submitted a booking. Send from ta@university.edu with the subject "Office Hours Confirmation". In the email body, include the student's name, their booked date, time slot, and topic, along with a brief confirmation message.
