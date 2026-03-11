# Sales Trip Planning Guide: Beijing to Shanghai

## Overview
This guide explains how to combine train travel data with CRM customer data to plan a sales trip and produce the required outputs.

## Customer Prioritization Methodology
1. Query the CRM system for all customers located in Shanghai
2. Calculate each customer's total historical order value (sum of all closed-won opportunities)
3. Rank customers by total order value in descending order
4. Select the top 5 customers for visit scheduling
5. Schedule meetings starting at 14:00 on arrival day, with 1.5 hours per meeting

## Excel Sheet Structure

### Sheet: Travel_Details
Columns:
- Train_Number: Selected train identifier
- Departure_Date: 2026-03-10
- Departure_Time: HH:MM
- Arrival_Time: HH:MM
- Duration_Minutes: Journey duration
- Class: Selected travel class
- Price_CNY: Ticket price
- Departure_Station: Full station name
- Arrival_Station: Full station name

### Sheet: Customer_Priority
Columns:
- Rank: 1 to 5 (1 = highest value customer)
- Customer_Name: Company or contact name
- Total_Order_Value_CNY: Sum of all historical orders
- Contact_Person: Primary contact
- Address: Shanghai address
- Scheduled_Meeting_Time: HH:MM on arrival day

### Sheet: Summary
Columns:
- Metric, Value, Notes
Rows: Selected train, total travel cost, total customer value to be visited, number of meetings scheduled

## Word Document Sections

### Section 1: Trip Overview
Dates, route, selected train, travel class, ticket cost.

### Section 2: Customer Visit Plan
Table of the top 5 customers with rank, name, total order value, and scheduled meeting time. Include a brief paragraph explaining the selection methodology.

### Section 3: Meeting Schedule
Chronological timeline of the day's meetings with customer name, time, and address.

### Section 4: Budget and Logistics
Total trip cost breakdown and any logistical notes.
