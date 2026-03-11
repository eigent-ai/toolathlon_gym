Hey, the finance team needs a comprehensive tax compliance audit for our online store. We have a Tax_Regulations.pdf in your workspace along with a guide.md that explains the methodology, so please review those first.

Pull all order data from the store, including each order's total, tax collected, and billing state. Also pull the configured tax rates. Using the methodology in the PDF and guide, compute the expected tax for every order by matching the billing state to the applicable rate. Remember that if no state-specific rate exists, the default rate with an empty state field should be used as a fallback. If a state has multiple rates configured, sum them together.

Create an Excel file called Tax_Compliance_Report.xlsx in your workspace with three sheets.

The first sheet should be called "Order Tax Audit" with columns Order_ID, Order_Total, Billing_State, Applicable_Rate, Expected_Tax, Actual_Tax, Discrepancy, and Status. Discrepancy is Actual minus Expected. Status should be Compliant if the absolute discrepancy is at most $0.50, Over-Collection if actual exceeds expected by more than $1.00, and Under-Collection if actual falls below expected by more than $1.00. For discrepancies between $0.50 and $1.00 in either direction, classify based on the sign. Include all orders sorted by Order_ID. Round monetary values to 2 decimals, rates to 4 decimals.

The second sheet should be called "State Summary" with columns State, Order_Count, Total_Revenue, Total_Expected_Tax, Total_Actual_Tax, Net_Discrepancy, Compliance_Rate_Pct, and Requires_Filing. Sort by state alphabetically. Compliance_Rate_Pct is the percentage of orders within tolerance rounded to 1 decimal. Requires_Filing is Yes if total actual tax exceeds $100, otherwise No.

The third sheet should be called "Compliance Overview" with two columns Label and Value containing summary metrics: Total_Orders_Audited, Compliant_Orders, Over_Collection_Orders, Under_Collection_Orders, Total_Over_Collected, Total_Under_Collected, Net_Tax_Discrepancy, States_Requiring_Filing, and Overall_Compliance_Rate.

Schedule four quarterly tax filing deadline reminders on the calendar as all-day events. Use the dates from the regulations PDF for the year 2026: April 15 titled "Tax Filing Deadline - Q1", July 15 titled "Tax Filing Deadline - Q2", October 15 titled "Tax Filing Deadline - Q3", and January 15 titled "Tax Filing Deadline - Q4".

Create a Google Form titled "Vendor Tax Information" to collect tax details from our vendors. It should have five questions: vendor name as a short text field, tax ID number as a short text field, state of registration as a short text field, tax-exempt status as a radio button choice with options Yes and No, and a text field for uploading or describing their tax certificate.

When everything is done, call claim_done.
