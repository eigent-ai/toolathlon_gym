# Training ROI Framework

## Overview
This document describes the methodology for calculating the Return on Investment (ROI) of internal training programs.

## ROI Formula
ROI is calculated as the ratio of performance improvement to the expected improvement threshold, expressed as a percentage:

ROI (%) = (Average Performance Improvement / 0.25) * 100

Where:
- Average Performance Improvement = mean of (current_avg_rating - baseline_rating) across all departments
- 0.25 is the standard improvement threshold representing a meaningful performance gain

## Performance Improvement Calculation
For each department:
1. Retrieve current average performance rating from HR data warehouse
2. Compare against pre-training baseline (from department_benchmarks.csv)
3. Compute delta = current_avg - baseline

## Interpretation
- ROI > 100%: Training exceeds expectations
- ROI 50-100%: Training meets expectations
- ROI < 50%: Training underperforms, consider restructuring

## Decision Rules
- If average improvement < 0.15 rating points: Recommend restructuring the program
- If average improvement >= 0.15 rating points: Recommend expanding to other departments
