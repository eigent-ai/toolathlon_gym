# Stress Testing Methodology Guide

## Monthly Return Calculation
- Group daily closing prices by calendar month
- Use the last available closing price for each month
- Monthly return = (Close_month_N - Close_month_N-1) / Close_month_N-1

## Portfolio VaR (Value at Risk) at 95% Confidence
1. Compute weighted monthly portfolio returns: sum of (weight_i * return_i) for each month
2. VaR_95 = 5th percentile of monthly portfolio returns * total portfolio value
3. This represents the maximum expected monthly loss at 95% confidence

## Maximum Drawdown
1. Compute cumulative portfolio returns: product of (1 + monthly_return) over time
2. Track running maximum of cumulative returns
3. Drawdown at each point = (cumulative - running_max) / running_max
4. Max drawdown = minimum of all drawdown values

## Sharpe Ratio (per stock)
- Annualized return = mean(monthly returns) * 12
- Annualized volatility = std(monthly returns) * sqrt(12)
- Sharpe = (annualized_return - 0.05) / annualized_volatility
- Use 5% as the annual risk-free rate

## Stress Test Application
- For each scenario, apply the scenario return to each stock's current allocated value
- Scenario_Value = Current_Value * (1 + Scenario_Return)
- Scenario_PnL = Scenario_Value - Current_Value
- Portfolio total = sum of all individual stock scenario values
