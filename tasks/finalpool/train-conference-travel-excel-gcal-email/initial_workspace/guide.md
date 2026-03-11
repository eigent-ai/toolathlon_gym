# Conference Travel Planning Guide

## Overview
This guide defines the output format requirements for planning conference travel for 3 attendees traveling to Qufu.

## Excel Output Format

### Sheet: Outbound
Columns: Attendee_Name, Origin, Destination, Train_Number, Departure_Date, Departure_Time, Arrival_Time, Duration_Minutes, Class, Price_CNY

### Sheet: Return
Columns: Attendee_Name, Origin, Destination, Train_Number, Departure_Date, Departure_Time, Arrival_Time, Duration_Minutes, Class, Price_CNY

### Sheet: Summary
Columns: Attendee_Name, Outbound_Train, Outbound_Departure, Return_Train, Return_Departure, Total_Cost_CNY, Notes

## Calendar Event Requirements
- Create one calendar event per attendee per journey (outbound and return)
- Title format: "[Attendee Name] - [Origin] to [Destination] - [Train Number]"
  Example: "Dr. Zhang Wei - Beijing to Qufu - G191"
- Event start time: Train departure time
- Event end time: Train arrival time
- Location field: Departure station name
- Description: Include seat class and ticket price

## Email Requirements
- Send a single summary email to all 3 attendees (CC list)
- Subject: "Conference Travel Arrangements - [Conference Name]"
- Body must include: selected train numbers, departure times, total cost per person, and a reminder to bring ID for ticket collection
- Attach the completed Excel file as an attachment reference (note the filename in the email body)
