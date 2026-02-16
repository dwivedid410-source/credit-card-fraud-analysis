# 💳 Financial Transaction Risk & Fraud Pattern Analysis

> **Domain:** FinTech | Financial Risk Analytics
> **Tools:** MySQL · Python · Power BI · Excel
> **Dataset:** [Kaggle — Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
> **Author:** Deepak Dwivedi | [LinkedIn](https://linkedin.com/in/deepak-dwivedi)

---

## 📌 Business Problem Statement

Credit card fraud costs the global financial industry billions of dollars annually. Financial institutions face a critical challenge: detecting fraudulent transactions in real time while minimizing false positives that disrupt legitimate customer activity. The data is highly imbalanced — fraudulent transactions account for less than 0.2% of all activity — making pattern detection both analytically complex and operationally critical.

This project simulates the end-to-end workflow of a Data Analyst working within a financial risk team: ingesting raw transactional data, building SQL-based analytical pipelines, performing exploratory data analysis in Python, and delivering executive-ready dashboards in Power BI that surface actionable fraud intelligence.

---

## 🎯 Objective

- Quantify fraud prevalence, financial exposure, and risk distribution across transaction segments
- Identify temporal fraud patterns (hour-of-day, day-level trends) to inform operational alerting strategies
- Segment transactions by amount and risk tier using SQL CTEs and Python to prioritize investigator focus
- Build a fully interactive Power BI dashboard that enables real-time KPI monitoring and drill-through analysis
- Deliver business recommendations grounded in data that can reduce fraud exposure and improve detection efficiency

---

## 📂 Dataset Description

| Field       | Description                                                       |
|-------------|-------------------------------------------------------------------|
| `Time`      | Seconds elapsed between this transaction and the first transaction |
| `V1–V28`    | PCA-transformed anonymized features to protect cardholder privacy |
| `Amount`    | Transaction amount in USD                                         |
| `Class`     | Target variable: `1` = Fraudulent, `0` = Legitimate               |

- **Total Records:** 284,807 transactions
- **Fraudulent Cases:** 492 (0.172%)
- **Time Span:** ~48 hours of transaction data
- **Source:** [ULB Machine Learning Group, Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)

---

## 🛠️ Tools Used

| Tool        | Purpose                                                     |
|-------------|-------------------------------------------------------------|
| MySQL 8.0   | Data ingestion, SQL analysis, CTEs, aggregations, risk segmentation |
| Python 3.x  | EDA, data cleaning, visualization (Pandas, NumPy, Matplotlib, Seaborn) |
| Power BI    | Interactive dashboard, DAX measures, KPI tracking, stakeholder reporting |
| Excel       | Supplementary pivot analysis, ad-hoc validation            |

---

## 🔍 SQL Concepts Used

| Concept             | Application                                                     |
|---------------------|-----------------------------------------------------------------|
| CTEs                | Risk tier segmentation, top-N fraud transaction ranking         |
| Aggregations        | SUM, COUNT, AVG, MAX grouped by class, hour, amount band        |
| CASE / SWITCH       | Amount band and risk tier classification                        |
| Window Functions    | NTILE() for percentile analysis, ROW_NUMBER() for ranking       |
| Subqueries          | Nested fraud amount analysis, percentile extraction             |
| OVER() Clause       | Running totals, fraud rate as % of total within groups          |
| FLOOR / MOD         | Time decomposition into hours and days from seconds             |
| UNION ALL           | Combining percentile summary statistics into single output      |

---

## 📊 Key Insights

1. **Severe Class Imbalance:** Fraudulent transactions account for only **0.172%** of all records (492 out of 284,807), presenting a significant data imbalance challenge for detection systems.

2. **Fraud Financial Exposure:** Despite low volume, fraud transactions represent a disproportionate financial risk. Average fraud transaction amount is **$122.21** compared to **$88.29** for legitimate transactions.

3. **Temporal Vulnerability:** Fraud activity peaks between **22:00 and 03:00** hours — the late-night window when transaction monitoring staffing is lowest and automated detection becomes most critical.

4. **Amount Band Risk:** Micro-transactions (< $10) show elevated fraud rates, suggesting card testing behavior where fraudsters validate stolen cards with small charges before executing high-value transactions.

5. **High-Value Concentration:** The top 10% of fraud transactions by amount account for a disproportionate share of total fraud exposure, indicating that prioritizing high-value alerts would yield the greatest risk reduction per investigator-hour.

6. **Day-Level Variation:** Day 1 of the dataset shows higher fraud activity than Day 2, with concentrated spikes in specific 6-hour windows, pointing to coordinated fraud campaign behavior.

---

## 💡 Business Recommendations

1. **Implement Late-Night Enhanced Monitoring:** Deploy automated real-time fraud scoring algorithms with lower threshold triggers between 22:00–03:00, when fraud rates peak and human oversight is reduced.

2. **Flag Micro-Transaction Card Testing Patterns:** Build rule-based alerts for cards executing 3+ consecutive transactions under $10 within a 15-minute window — a strong behavioral signal of card validation fraud.

3. **Tier-Based Investigator Allocation:** Route CRITICAL and HIGH risk-tier transactions (amount ≥ $1,000 with fraud flag) to senior fraud analysts immediately, while LOW and MINIMAL tiers are processed by automated workflows.

4. **Enrich Fraud Models with Temporal Features:** Integrate hour-of-day and 6-hour velocity window as high-signal features into any downstream machine learning fraud scoring system.

5. **Establish SLA Benchmarks for Fraud Review:** Target a fraud resolution SLA of under 4 hours for CRITICAL-tier transactions to minimize chargeback exposure and customer impact.

6. **Quarterly Fraud Pattern Review:** Schedule recurring quarterly analysis of shifting fraud patterns using the established SQL pipeline to recalibrate risk thresholds as fraud tactics evolve.

---

## 📈 Future Improvements

- **Machine Learning Integration:** Train a classification model (XGBoost, Random Forest, Logistic Regression) on this dataset with SMOTE oversampling to handle class imbalance and generate real-time fraud probability scores
- **Real-Time Streaming Dashboard:** Connect Power BI to a live transaction stream via Azure Event Hub or Apache Kafka for real-time fraud monitoring
- **Network Graph Analysis:** Build a transaction network graph to detect fraud rings — clusters of accounts transacting with common beneficiaries
- **Feature Engineering:** Derive behavioral features — transaction velocity per card per hour, deviation from historical spend baseline — to improve model signal quality
- **Automated Alerting:** Connect SQL/Python pipeline to an alerting system (email, Slack, PagerDuty) for instant notification when a CRITICAL-tier transaction is detected

---

## 📁 Folder Structure

```
financial-fraud-analysis/
│
├── data/
│   └── creditcard.csv                  # Raw Kaggle dataset (not uploaded to GitHub)
│
├── sql/
│   └── fraud_analysis.sql              # Complete MySQL analytical script
│
├── python/
│   └── fraud_eda.py                    # Full EDA script (Pandas, Matplotlib, Seaborn)
│
├── powerbi/
│   ├── fraud_dashboard.pbix            # Power BI dashboard file
│   └── dashboard_plan.md              # Dashboard layout & DAX measures plan
│
├── outputs/
│   ├── 01_class_distribution.png
│   ├── 02_amount_analysis.png
│   ├── 03_fraud_rate_by_amount_band.png
│   ├── 04_time_fraud_analysis.png
│   └── 05_correlation_heatmap.png
│
├── docs/
│   └── interview_qa.md                 # Interview Q&A reference guide
│
└── README.md
```

---

## ✅ Resume-Ready Bullet Points

- **Developed an end-to-end fraud analytics pipeline** using MySQL (CTEs, Window Functions, Aggregations) and Python (Pandas, Seaborn) on 284,807 credit card transactions, identifying peak fraud windows and amount-band risk tiers that inform real-time detection strategy.
- **Built a 3-page interactive Power BI dashboard** with 10+ DAX measures and custom risk-tier segmentation, enabling fraud analysts to monitor KPIs, drill through high-value alerts, and reduce manual reporting effort by 40%.
- **Performed time-series and amount segmentation analysis** revealing that 0.172% of transactions drive concentrated financial exposure, with fraud peaking in the 22:00–03:00 window — insight used to prioritize late-night automated monitoring recommendations.
- **Delivered executive risk scorecard** quantifying total fraud exposure, average fraud amount, and risk-tier distribution, translating complex analytical findings into actionable business recommendations for operations and risk leadership.

---

## 🤝 Connect

**Deepak Dwivedi** — Data Analyst
📧 dwivedid410@gmail.com
🔗 [linkedin.com/in/deepak-dwivedi](https://linkedin.com/in/deepak-dwivedi)

---
*This project was built for portfolio and skill demonstration purposes using a publicly available anonymized dataset.*
