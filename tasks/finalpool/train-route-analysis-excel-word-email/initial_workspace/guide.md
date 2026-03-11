# Route Analysis Guide: Beijing Train Routes

## Overview
This guide defines the structure for analyzing Beijing train routes on 2026-03-10 and producing an Excel report and Word document.

## Excel Sheet Structure

### Sheet: Routes
Columns:
- Train_Number: Train identifier (e.g., G1, G3, D101)
- Origin: Departure city/station
- Destination: Arrival city/station
- Departure_Time: HH:MM format
- Arrival_Time: HH:MM format
- Duration_Minutes: Integer travel time
- Distance_KM: Route distance in kilometers
- Second_Class_Price: CNY price for second class
- First_Class_Price: CNY price for first class
- Business_Class_Price: CNY price for business class (if available)
- Train_Type: G (high-speed), D (EMU), K (conventional), etc.

### Sheet: Summary
Columns:
- Metric: Name of the metric being summarized
- Value: Computed value
- Notes: Explanation or context

Summary rows to include:
- Total routes analyzed
- Fastest route (train number + duration)
- Cheapest route (train number + second class price)
- Most expensive route (train number + business class price)
- Average journey duration (minutes)
- Average second class price (CNY)

## Word Report Structure

### Section 1: Executive Summary
2-3 paragraphs summarizing the analysis date, number of routes found, key findings, and overall recommendation.

### Section 2: Route Details
A table listing all routes with columns: Train Number, Departure, Arrival, Duration, Second Class Price.

### Section 3: Recommendation
Recommended route with justification based on balance of speed and cost. State the specific train number and explain why it is preferred.

### Section 4: Cost Comparison
A comparison table showing the cost difference between classes (second, first, business) for the top 3 recommended trains.
