I am a research lab manager preparing an annual citation impact report. I need you to gather academic paper data, run an analysis script, and compile the results into a Google Sheet.

First, search the academic database for papers by researchers working in AI and machine learning. Look through the scholarly database to find all available papers. Collect the title, authors, citation count, and year for each paper you find.

Second, identify all unique authors across the papers and calculate each author's total citation count, paper count, and average citations per paper. To do this, save the collected paper data as a JSON file called papers.json in your workspace. Each entry should have the keys "title", "authors" (a list of objects with "name" key), "citation_count" (integer), and "year" (integer).

Third, there is a script called citation_analysis.py already in your workspace. Run it with the papers.json file as input to compute per-author statistics. The script reads the JSON file and outputs author statistics as JSON to stdout. Capture this output for use in the spreadsheet.

Fourth, create a Google Sheet spreadsheet titled "Citation Impact Analysis" with two sheets. The first sheet should be named "Author Rankings" with columns Author Name, Total Citations, Paper Count, and Avg Citations Per Paper. Populate it with the author statistics sorted by total citations in descending order. The second sheet should be named "Paper Details" with columns Paper Title, Authors, Citation Count, and Year. Populate it with all the papers sorted by citation count in descending order. For the Authors column in Paper Details, join the author names with a comma and space.

Make sure all data is accurate and properly sorted.
