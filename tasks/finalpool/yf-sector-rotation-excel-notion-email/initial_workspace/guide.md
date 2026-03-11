# Sector Rotation Momentum Methodology

## Overview
This document details the momentum calculation and signal generation methodology for sector rotation analysis. Each tracked stock represents its sector.

## Stocks and Sectors
- AMZN: Consumer Cyclical
- GOOGL: Communication Services
- JNJ: Healthcare
- JPM: Financial Services
- XOM: Energy
- Benchmark: ^DJI (Dow Jones Industrial Average)
- Excluded from analysis: GC=F (Gold Futures)

## Momentum Calculation

### Period Returns
For each stock, calculate percentage returns over three lookback periods from the latest available trading date:
- 1-Month Return: (latest_price / price_1_month_ago - 1) * 100
- 3-Month Return: (latest_price / price_3_months_ago - 1) * 100
- 6-Month Return: (latest_price / price_6_months_ago - 1) * 100

Where "N months ago" means the latest available price on or before the date that is 30/90/180 calendar days before the latest date.

### Composite Momentum Score
Weighted average of period returns:
- Composite = 1M_Return * 0.2 + 3M_Return * 0.3 + 6M_Return * 0.5

The 6-month return gets the highest weight to capture the dominant trend.

## Signal Generation

### Benchmark Comparison
Calculate the same composite momentum for the benchmark (^DJI). Then compare each stock's composite to the benchmark:
- If stock_composite - benchmark_composite > 2: **Overweight**
- If stock_composite - benchmark_composite < -2: **Underweight**
- Otherwise: **Neutral**

The +/- 2% threshold creates a dead zone to avoid false rotation signals.

## Relative Strength
Relative strength measures excess return over the benchmark for each period:
- RS_1M = Stock_1M_Return - Benchmark_1M_Return
- RS_3M = Stock_3M_Return - Benchmark_3M_Return
- RS_6M = Stock_6M_Return - Benchmark_6M_Return
- Avg_RS = (RS_1M + RS_3M + RS_6M) / 3

Higher Avg_RS indicates stronger relative momentum. Stocks are ranked 1 (strongest) to 5 (weakest).

## Portfolio Signal
Based on the aggregate signal distribution:
- **Bullish**: More than 50% of stocks are Overweight
- **Bearish**: More than 50% of stocks are Underweight
- **Mixed**: Otherwise
