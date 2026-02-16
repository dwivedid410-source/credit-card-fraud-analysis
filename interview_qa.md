# Interview Q&A — Financial Transaction Risk & Fraud Pattern Analysis
# Deepak Dwivedi | Data Analyst Portfolio Project
# ============================================================
# Covers: SQL | Python | Power BI | Business Logic | Statistics
# ============================================================


## ─────────────────────────────────────────────────────────
## SECTION A: SQL TECHNICAL QUESTIONS
## ─────────────────────────────────────────────────────────

**Q1. What SQL concepts did you use in this project and why?**

A: I used several advanced SQL concepts to build a production-quality analytical pipeline:

- **CTEs (Common Table Expressions):** Used to stage intermediate results before final aggregation. For example, I first created a `transaction_metrics` CTE that assigned a risk tier to every transaction, then joined it in a `risk_summary` CTE for clean, readable aggregated output. CTEs improve code readability, enable step-by-step logic decomposition, and are reusable within the same query.

- **Window Functions (NTILE, ROW_NUMBER, OVER):** Used `NTILE(10)` to split fraud transactions into deciles for concentration analysis — revealing what percentage of fraud exposure comes from the top 10% of high-value transactions. `ROW_NUMBER()` ranked fraudulent transactions by amount for top-N reporting.

- **Aggregations with CASE:** Used conditional `SUM(CASE WHEN is_fraud=1 THEN amount END)` inside GROUP BY queries to calculate fraud exposure per segment without requiring a subquery or join.

- **FLOOR and MOD for time decomposition:** Since the dataset stores time in seconds elapsed, I decomposed it using `FLOOR(time_seconds / 3600) % 24` to derive hour of day — enabling hourly fraud pattern analysis without a date dimension table.

- **UNION ALL:** Used to combine multiple percentile statistics into a single summary output for the executive scorecard.


**Q2. How did you handle the class imbalance in SQL analysis?**

A: SQL doesn't perform machine learning, so I focused on making the imbalance visible and quantifiable rather than correcting it. Every aggregation query included a `fraud_rate_pct` column calculated as `SUM(is_fraud) * 100.0 / COUNT(*)`, which contextualizes fraud count relative to total volume. This prevents misleading interpretations where absolute fraud counts look small. In the amount segmentation analysis, I showed both absolute counts and fraud rates side by side so that analysts can identify high-risk bands even when they contain few records.

For downstream ML work, I would recommend SMOTE (Synthetic Minority Oversampling Technique) or adjusting class weights in the model to correct the imbalance.


**Q3. Explain the risk segmentation CTE logic in your SQL script.**

A: I used a two-level CTE architecture:

```sql
WITH transaction_metrics AS (
    SELECT id, amount, is_fraud,
        CASE
            WHEN amount >= 5000                         THEN 'CRITICAL'
            WHEN amount >= 1000 AND is_fraud = 1        THEN 'HIGH'
            WHEN amount >= 500  AND is_fraud = 1        THEN 'MEDIUM'
            WHEN is_fraud = 1                           THEN 'LOW'
            ELSE 'MINIMAL'
        END AS risk_tier
    FROM transactions
),
risk_summary AS (
    SELECT risk_tier, COUNT(*), SUM(is_fraud),
           ROUND(SUM(is_fraud)*100.0/COUNT(*), 2) AS fraud_rate_pct,
           ROUND(AVG(amount), 2) AS avg_amount
    FROM transaction_metrics
    GROUP BY risk_tier
)
SELECT * FROM risk_summary;
```

The first CTE tags each individual transaction with a risk tier based on both amount and fraud flag. The second CTE aggregates those tags into a summary. This two-level approach keeps each logical step separate, which is easier to debug, extend, and explain to stakeholders.


**Q4. Why did you use DECIMAL(10,2) for the amount column instead of FLOAT?**

A: Financial data requires exact decimal precision. `FLOAT` and `DOUBLE` are binary floating-point types that introduce rounding errors — for example, $122.50 might be stored as $122.4999999. In financial reporting, even sub-cent discrepancies can compound into significant errors at scale, fail reconciliation checks, or trigger audit flags.

`DECIMAL(10,2)` stores values as exact base-10 numbers, guaranteeing that $122.50 is always stored and retrieved as exactly $122.50. For a fraud analysis system where transaction amounts drive risk tier assignments and financial exposure calculations, this precision is non-negotiable.


---

## ─────────────────────────────────────────────────────────
## SECTION B: PYTHON / EDA TECHNICAL QUESTIONS
## ─────────────────────────────────────────────────────────

**Q5. Walk me through your EDA approach for this dataset.**

A: I followed a structured EDA methodology with five phases:

1. **Data Loading & Structural Validation:** Loaded the CSV, confirmed shape (284,807 rows × 31 columns), inspected dtypes, and verified that V1–V28 are floats (PCA-transformed) while `Amount` and `Class` are the primary business columns.

2. **Data Quality Audit:** Checked for missing values (none found), duplicate rows (1 duplicate present), and confirmed that `Class` contains only binary values (0/1) with no corruption.

3. **Target Variable Distribution:** Quantified the class imbalance — 99.828% legitimate vs. 0.172% fraudulent — visualized through both a bar chart and donut chart to make the imbalance immediately visible to stakeholders.

4. **Feature-Level Analysis:** Compared `Amount` distributions between classes using histograms and box plots. Fraud transactions showed a different spread — higher maximum values but lower median, suggesting fraud is not exclusively a high-value phenomenon.

5. **Temporal and Segmentation Analysis:** Decomposed `Time` (seconds) into `hour_of_day` and `day_number`, then plotted fraud rate and volume by hour to identify peak fraud windows. Applied amount band segmentation to calculate fraud rate per bracket.

6. **Correlation Analysis:** Generated a heatmap of V1–V10 against `Class` to identify which PCA components have the strongest linear relationship with fraud — useful for informing feature selection in downstream ML work.


**Q6. How did you handle the PCA-transformed features (V1–V28) in your EDA?**

A: Because V1–V28 are PCA-transformed principal components from an anonymized feature set, their original meaning is inaccessible. I treated them as numeric signals rather than business-interpretable fields. In the EDA, I:

1. Used a correlation heatmap to identify which components correlate most strongly with `Class` — V4, V11, V12, V14, and V17 showed notable correlations and would be high-priority features for a classification model.
2. Avoided distributional analysis on individual V-features since they lack business context — instead, I focused analysis on `Amount` and `Time`, which are the only interpretable business variables.
3. Noted that correlation does not imply causation, and any V-feature importance would need to be validated through model SHAP values for proper interpretability.


**Q7. The dataset has severe class imbalance. How does this affect your EDA and what would you do next?**

A: The imbalance (0.172% fraud) creates several analytical risks:

- **Misleading accuracy:** A model that predicts "Legitimate" for every transaction achieves 99.83% accuracy — a meaningless metric here. Precision, Recall, F1, and AUC-ROC are the appropriate evaluation metrics.
- **Visual distortion:** Standard histograms are dominated by the majority class. I addressed this by plotting fraud and legitimate distributions separately and using percentage-based fraud rates rather than raw counts.
- **Model training risk:** Training without addressing imbalance results in models biased toward the majority class, failing to detect the rare fraud events that matter most.

For next steps, I would apply:
1. **SMOTE (Synthetic Minority Oversampling):** Generate synthetic fraud samples in the training set to balance class distribution
2. **Class weight adjustment:** Set `class_weight='balanced'` in scikit-learn classifiers to penalize misclassification of the minority class more heavily
3. **Threshold tuning:** Instead of default 0.5 probability threshold, tune the decision threshold using Precision-Recall curves to optimize for high recall (catching more fraud) at acceptable precision


---

## ─────────────────────────────────────────────────────────
## SECTION C: POWER BI / DAX QUESTIONS
## ─────────────────────────────────────────────────────────

**Q8. Explain the key DAX measures you built for this dashboard.**

A: The three most important DAX measures in this project are:

**Fraud Rate %:**
```dax
Fraud Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(transactions), transactions[is_fraud] = 1),
    COUNTROWS(transactions),
    0
)
```
This calculates the percentage of fraudulent transactions dynamically — it respects all active slicers, so when a user filters by hour or amount band, it recalculates within that filtered context. `DIVIDE` is used instead of `/` to handle division-by-zero gracefully, returning 0 when no transactions exist.

**Total Fraud Amount:**
```dax
Total Fraud Amount =
CALCULATE(SUM(transactions[amount]), transactions[is_fraud] = 1)
```
`CALCULATE` modifies the filter context — it adds an explicit filter for fraud-only transactions on top of any existing slicer filters. This gives the exact financial exposure from fraudulent transactions.

**Risk Tier Calculated Column:**
```dax
Risk Tier =
SWITCH(TRUE(),
    transactions[amount] >= 5000, "CRITICAL",
    transactions[amount] >= 1000 && transactions[is_fraud] = 1, "HIGH",
    transactions[amount] >= 500  && transactions[is_fraud] = 1, "MEDIUM",
    transactions[is_fraud] = 1, "LOW",
    "MINIMAL"
)
```
This column-level calculation enables the risk tier slicer and treemap visualization, grouping every transaction into a business-meaningful risk category that analysts can immediately act on.


---

## ─────────────────────────────────────────────────────────
## SECTION D: BUSINESS & ANALYTICAL QUESTIONS
## ─────────────────────────────────────────────────────────

**Q9. What were the three most important business insights from this project?**

A:

1. **Late-Night Fraud Concentration:** Fraud rates spike significantly between 22:00 and 03:00 — hours where transaction volume is lower but fraud concentration is highest. This directly suggests that banks should either increase automated monitoring sensitivity during these hours or adjust real-time scoring thresholds based on time-of-day context. A static, time-agnostic fraud model misses this signal entirely.

2. **Micro-Transaction Card Testing Behavior:** The amount band analysis revealed that transactions under $10 have a disproportionately high fraud rate relative to their value. This is consistent with known card testing fraud — where criminals validate stolen card credentials with small charges before executing larger fraudulent transactions. An operational recommendation is to flag cards with 3+ consecutive micro-transactions within a short time window as a high-priority review trigger.

3. **Top-Decile Exposure Concentration:** Using SQL NTILE analysis, I found that the top 10% of fraudulent transactions by amount account for the majority of total fraud financial exposure. This means investigator resources should be disproportionately concentrated on high-value fraud alerts — a triage approach that maximizes risk reduction per analyst-hour rather than treating all fraud cases equally.


**Q10. How would you present these findings to a non-technical business stakeholder?**

A: I would structure the presentation in three layers:

**Layer 1 — The Problem (1 slide):**
"We processed 284,807 transactions. 492 were fraudulent — less than 0.2% of volume. But those 492 transactions represent [total fraud exposure] in financial risk. The challenge is catching them without blocking legitimate customers."

**Layer 2 — What the Data Shows (3 slides):**
Use the Power BI dashboard with KPI cards first — Total Fraud Cases, Fraud Rate %, Financial Exposure. These numbers anchor the conversation in business terms before showing any charts. Then show the hourly fraud chart and the amount band bar chart with a single-sentence insight annotation on each: "Fraud peaks at night" and "Small transactions are being used to test stolen cards."

**Layer 3 — What We Should Do (1 slide):**
Convert each insight into a specific, actionable recommendation with an estimated impact. For example: "Increasing automated alert sensitivity between 22:00–03:00 could intercept [X%] of fraud cases based on current patterns." Always tie analytics back to a decision that a business leader can authorize.

I would avoid showing raw SQL output, correlation matrices, or Python code to non-technical stakeholders — those belong in the technical appendix if requested.


**Q11. How does this project demonstrate skills relevant to a mid-level Data Analyst role?**

A: This project covers the complete analytical workflow that mid-level Data Analyst roles require:

- **SQL proficiency at depth:** Not just SELECT queries but CTEs, window functions, time decomposition, and multi-table logic that reflects real analytical workloads
- **Python for EDA:** Structured, documented EDA with business-relevant visualizations — not just matplotlib plots, but insights tied to specific business questions
- **BI tool expertise:** Power BI dashboard with calculated columns, DAX measures, conditional formatting, and multi-page navigation — the kind of dashboard a stakeholder actually uses daily
- **Business communication:** README and insights are written in business language, not technical jargon — demonstrating the ability to translate data findings into decisions
- **End-to-end thinking:** The project connects data ingestion → SQL analysis → Python EDA → dashboard → business recommendations in a coherent pipeline rather than treating each skill as an isolated exercise

This mirrors what a Data Analyst does in a FinTech, banking, or operations team: own the data pipeline, surface insights, and make recommendations — not just run reports.


---

## QUICK-REFERENCE FACT SHEET

| Metric                     | Value                     |
|----------------------------|---------------------------|
| Total Transactions         | 284,807                   |
| Fraudulent Transactions    | 492                       |
| Fraud Rate                 | 0.172%                    |
| Avg Fraud Amount           | ~$122.21                  |
| Avg Legitimate Amount      | ~$88.29                   |
| Max Transaction Amount     | $25,691.16                |
| Peak Fraud Window          | 22:00 – 03:00 hours       |
| Dataset Time Span          | ~48 hours                 |
| SQL Concepts Used          | 8 (CTE, Window Fn, CASE…) |
| Power BI DAX Measures      | 11+                       |
| Python Visualizations      | 5 charts                  |
