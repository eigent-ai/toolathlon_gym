# Trip Planning Guide: Beijing to Qufu with Meal Planning

## Overview
This guide defines the structure for combining train travel planning with meal planning for a cultural trip to Qufu (Confucius birthplace).

## Word Document Structure

The Word document should contain the following sections in order:

### Section 1: Trip Overview
- Destination, dates, purpose
- Selected train details (outbound and return)
- Total travel cost

### Section 2: Outbound Journey
- Train number, departure and arrival times
- Journey duration
- Station information

### Section 3: Daily Meal Plan
For each day of the trip (2026-03-12 through 2026-03-15), list:
- Breakfast: dish name, estimated prep time, key ingredients
- Lunch: dish name, estimated prep time, key ingredients
- Dinner: dish name, estimated prep time, key ingredients
- Daily estimated food cost (CNY)

### Section 4: Return Journey
- Train number, departure and arrival times
- Journey duration

### Section 5: Budget Summary
- Train costs (outbound + return)
- Estimated total food cost for trip
- Grand total

## Calendar Event Requirements

Create the following calendar events:

1. Outbound train event
   - Title: "Train to Qufu - [Train Number]"
   - Date/Time: outbound departure datetime to arrival datetime
   - Location: Beijing departure station

2. Return train event
   - Title: "Return Train to Beijing - [Train Number]"
   - Date/Time: return departure datetime to arrival datetime
   - Location: Qufu station

3. One meal reminder event per day at 08:00
   - Title: "Meal Plan Day [N] - [Breakfast dish name]"
   - Duration: 30 minutes
