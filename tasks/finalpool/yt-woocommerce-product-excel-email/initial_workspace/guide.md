# Task Guide: Tech Video Marketing Opportunities

## Overview
Identify online store products that match trending tech topics from top Fireship YouTube videos.

## Step 1: Get Top 10 Fireship Videos (2024+)
Filter videos published from 2024-01-01 onwards, sort by view_count DESC, take top 10.

## Step 2: Classify Topics
Rules for Main_Topic classification:
- "AI": title contains DeepSeek, AI, OpenAI, GPT, Grok, Claude, or vibe
- "Linux": title contains Linux
- "Windows": title contains Windows
- "JavaScript/Web": title contains JavaScript, CSS, TypeScript, React, Node, or Deno
- "Python": title contains Python
- "Security": title contains security, hack, Hackers, or encrypted
- "Tech/General": everything else

## Step 3: Match Products
Product keywords to search: laptop, usb, hub, adapter, TV, monitor, tablet, watch, headphone, camera

## Deliverable: Marketing_Opportunity_Report.xlsx

Sheet 1: Video_Topics
Columns: Rank (1-10), Title, View_Count, Publish_Date (YYYY-MM-DD), Main_Topic
Sort: Rank ASC

Sheet 2: Product_Matches
Columns: Video_Title, Product_ID, Product_Name, Product_Price, Match_Keyword

Sheet 3: Summary (3 rows)
Row 1: Total_Videos_Analyzed | 10
Row 2: Total_Product_Matches | [count]
Row 3: Most_Common_Topic | [topic name]

## Email
- To: marketing@company.com
- Subject: "Tech Video Marketing Opportunities"
- Body: Describe top 3 video-product matches (video title + product name)
