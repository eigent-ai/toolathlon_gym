# Sales Forecast Methodology

## Approach

The regional sales forecast uses a trailing average methodology adjusted by economic indicators.

## Formula

Monthly Forecast = 3-Month Trailing Average x (1 + GDP Growth Rate / 100)

Where:
- 3-Month Trailing Average = average of the last three months of revenue (October, November, December 2025)
- GDP Growth Rate = annual GDP growth percentage for the region

## Quarterly Forecast

Quarterly Forecast = Monthly Forecast x 3

This assumes consistent monthly performance within the quarter.

## Data Sources

- Historical sales data: company data warehouse
- Economic indicators: external economic data API (GDP growth, consumer confidence, inflation)

## Regions

Forecasts are produced for all five sales regions:
- North America
- Europe
- Asia Pacific
- Latin America
- Middle East

## Limitations

- Does not account for seasonal patterns beyond what the trailing average captures
- Assumes economic conditions remain stable
- Does not incorporate planned product launches or promotions
- Simple linear adjustment may not capture complex economic effects
