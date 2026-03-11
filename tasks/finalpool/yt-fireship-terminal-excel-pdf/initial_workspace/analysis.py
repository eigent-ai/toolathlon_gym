"""
Template analysis script for Fireship video analytics.
This script reads fireship_raw.csv and computes quarterly statistics.
Adapt and run this script to generate quarterly_stats.json.
"""
import csv
import json
from collections import defaultdict

INPUT_CSV = "fireship_raw.csv"
OUTPUT_JSON = "quarterly_stats.json"


def get_quarter(date_str):
    """Convert YYYY-MM-DD to YYYY-Qn format."""
    year, month, day = date_str.split("-")
    q = (int(month) - 1) // 3 + 1
    return f"{year}-Q{q}"


def main():
    quarters = defaultdict(lambda: {"count": 0, "total_views": 0, "total_likes": 0})

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            quarter = get_quarter(row["published_date"])
            quarters[quarter]["count"] += 1
            quarters[quarter]["total_views"] += int(row["view_count"])
            quarters[quarter]["total_likes"] += int(row["like_count"])

    results = []
    for q in sorted(quarters.keys()):
        d = quarters[q]
        avg_engagement = round(d["total_likes"] / d["total_views"] * 100, 3) if d["total_views"] > 0 else 0.0
        results.append({
            "Quarter": q,
            "Video_Count": d["count"],
            "Total_Views": d["total_views"],
            "Avg_Engagement_Rate": avg_engagement,
        })

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Written {len(results)} quarters to {OUTPUT_JSON}")
    for r in results:
        print(f"  {r['Quarter']}: {r['Video_Count']} videos, {r['Total_Views']} views, {r['Avg_Engagement_Rate']}% engagement")


if __name__ == "__main__":
    main()
