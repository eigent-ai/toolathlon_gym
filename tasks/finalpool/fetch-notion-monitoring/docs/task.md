I manage the infrastructure team and need a full availability report for our three critical services. The raw monitoring data is in service_status_log.json in the workspace. This file contains 504 hourly status checks covering three services over seven days, from February 27 through March 5, 2026. Each entry has a timestamp, service_name, status (which is one of up, down, or degraded), response_time_ms, and error_message (null when the service is up).

Please analyze this data and create an Excel file called Service_Availability_Report.xlsx in the workspace with two sheets.

The first sheet should be called "Availability Summary" and have the following columns: Service_Name, Total_Checks, Up_Count, Down_Count, Degraded_Count, Uptime_Pct, and Avg_Response_Time_Ms. Uptime_Pct should be calculated as the number of up checks divided by total checks times 100, rounded to one decimal place. Avg_Response_Time_Ms should be rounded to two decimal places. There should be one row per service, so three rows total.

The second sheet should be called "Incidents" and list every continuous period where a service was in a down or degraded state. The columns should be Service_Name, Start_Time, End_Time, Duration_Minutes, Status, and Error_Message. A new incident row should be created each time a service transitions from up to down or degraded, and the incident ends when the service returns to up. Duration_Minutes should reflect how many minutes the incident lasted based on the timestamps.

Next, create a page in the knowledge base titled "Service Monitoring Dashboard - March 2026" that summarizes the findings. The page should describe the overall availability of each service, highlight any services with downtime or degraded performance, and note the specific incident windows.

For each service that experienced any downtime during the monitoring period, create a calendar event on March 7, 2026 from 10:00 to 10:30. Title the event "Incident Review: [Service_Name]" where you replace [Service_Name] with the actual service name. In the event description, include a brief summary of the downtime incidents for that service.

Finally, send an email from monitoring@company.com to devops-team@company.com with the subject "Service Availability Report - Week of Feb 27" that lists each service whose uptime was below 99 percent, along with their actual uptime percentage and a note about the incidents observed.
