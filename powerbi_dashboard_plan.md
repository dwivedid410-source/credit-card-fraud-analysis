# Power BI Dashboard Design Plan
# Financial Transaction Risk & Fraud Pattern Analysis
# ============================================================

## Overview
Dashboard Name : Financial Fraud Intelligence Hub
Target Users   : Risk Analysts, Operations Managers, Senior Leadership
Refresh Cadence: Daily (batch) or Real-Time (streaming connector)
Pages          : 3 tabs — Executive Summary | Transaction Deep Dive | Risk Heatmap


# ============================================================
# PAGE 1: EXECUTIVE SUMMARY (High-Level KPIs)
# ============================================================

## KPI Cards (Top Row — 5 cards)

Card 1: Total Transactions
  Value  : COUNT of all rows
  Format : #,##0
  Color  : Blue

Card 2: Total Fraud Cases
  Value  : SUM of [is_fraud] = 1
  Format : #,##0
  Color  : Red

Card 3: Fraud Rate (%)
  Value  : [Fraud Rate %] DAX measure
  Format : 0.00%
  Color  : Orange — conditional (red if > 0.5%)

Card 4: Total Financial Exposure (Fraud)
  Value  : [Total Fraud Amount] DAX measure
  Format : $#,##0.00
  Color  : Dark Red

Card 5: Avg Fraud Transaction Amount
  Value  : [Avg Fraud Amount] DAX measure
  Format : $#,##0.00
  Color  : Amber


## Charts — Page 1

Chart A: Clustered Bar Chart
  Title  : Transaction Volume by Class (Legitimate vs. Fraudulent)
  X-Axis : Transaction Type
  Y-Axis : Count
  Colors : Blue (Legit), Red (Fraud)

Chart B: Donut Chart
  Title  : Fraud vs. Legitimate Split (%)
  Values : COUNT(transactions) grouped by is_fraud
  Colors : #2196F3 (Legit), #F44336 (Fraud)

Chart C: Line Chart
  Title  : Hourly Transaction Volume & Fraud Trend
  X-Axis : Hour of Day (0–23)
  Y-Axis : Count (primary), Fraud Rate % (secondary axis)
  Series : Total Transactions (line), Fraud Count (line, red)

Chart D: Stacked Bar Chart
  Title  : Fraud Count by Amount Band
  X-Axis : Amount Segment
  Y-Axis : Fraud Count
  Tooltip: Fraud Rate %, Total Exposure


## Slicers — Page 1
  - Transaction Type     (Legitimate / Fraudulent / All)
  - Amount Band          (Micro / Low / Medium / High / Premium / Very High)
  - Hour of Day          (slider 0–23)
  - Day Number           (1 or 2)
  - Risk Tier            (CRITICAL / HIGH / MEDIUM / LOW / MINIMAL)


# ============================================================
# PAGE 2: TRANSACTION DEEP DIVE
# ============================================================

## Charts

Chart E: Histogram
  Title  : Transaction Amount Distribution by Class
  Bins   : $0–50, $50–100, $100–500, $500–1000, $1000+
  Filter : is_fraud slicer

Chart F: Scatter Plot
  Title  : Amount vs. Time — Fraud Flagged
  X-Axis : Time (seconds)
  Y-Axis : Amount
  Color  : is_fraud (Red = Fraud, Blue = Legit)
  Size   : Amount

Chart G: Table Visual
  Title  : Top 20 High-Risk Fraudulent Transactions
  Fields : Transaction ID, Amount, Hour, Risk Tier, Amount Band
  Sort   : Amount DESC
  Conditional Formatting: Amount (red gradient)

Chart H: Gauge Chart
  Title  : Fraud Exposure as % of Total Volume
  Value  : [Fraud Exposure %] measure
  Target : 0.5% (industry benchmark)


# ============================================================
# PAGE 3: RISK HEATMAP & SEGMENTATION
# ============================================================

Chart I: Matrix / Heatmap
  Title  : Fraud Rate Heatmap — Hour of Day × Amount Band
  Rows   : Hour of Day
  Columns: Amount Band
  Values : Fraud Rate %
  Coloring: Conditional formatting (white → dark red)

Chart J: Treemap
  Title  : Fraud Financial Exposure by Risk Tier
  Group  : Risk Tier
  Size   : Total Fraud Amount
  Color  : Risk Tier

Chart K: Waterfall Chart
  Title  : Fraud Exposure Breakdown by Amount Segment
  Category: Amount Band
  Values : Fraud Exposure USD


# ============================================================
# DAX MEASURES — COMPLETE
# ============================================================

## Core Measures

Total Transactions =
    COUNTROWS(transactions)

Total Fraud Cases =
    CALCULATE(COUNTROWS(transactions), transactions[is_fraud] = 1)

Total Legitimate =
    CALCULATE(COUNTROWS(transactions), transactions[is_fraud] = 0)

Fraud Rate % =
    DIVIDE(
        CALCULATE(COUNTROWS(transactions), transactions[is_fraud] = 1),
        COUNTROWS(transactions),
        0
    )

Total Transaction Volume =
    SUM(transactions[amount])

Total Fraud Amount =
    CALCULATE(SUM(transactions[amount]), transactions[is_fraud] = 1)

Total Legit Amount =
    CALCULATE(SUM(transactions[amount]), transactions[is_fraud] = 0)

Avg Fraud Amount =
    CALCULATE(AVERAGE(transactions[amount]), transactions[is_fraud] = 1)

Avg Legit Amount =
    CALCULATE(AVERAGE(transactions[amount]), transactions[is_fraud] = 0)

Fraud Exposure % =
    DIVIDE([Total Fraud Amount], [Total Transaction Volume], 0)

Max Fraud Amount =
    CALCULATE(MAX(transactions[amount]), transactions[is_fraud] = 1)


## Calculated Columns (Power Query / DAX)

Amount Band =
    SWITCH(
        TRUE(),
        transactions[amount] < 10,   "1. Micro (< $10)",
        transactions[amount] < 100,  "2. Low ($10-$99)",
        transactions[amount] < 500,  "3. Medium ($100-$499)",
        transactions[amount] < 1000, "4. High ($500-$999)",
        transactions[amount] < 5000, "5. Premium ($1K-$4,999)",
        "6. Very High (>= $5K)"
    )

Hour of Day =
    MOD(INT(transactions[time_seconds] / 3600), 24)

Risk Tier =
    SWITCH(
        TRUE(),
        transactions[amount] >= 5000,                           "CRITICAL",
        transactions[amount] >= 1000 && transactions[is_fraud] = 1, "HIGH",
        transactions[amount] >= 500  && transactions[is_fraud] = 1, "MEDIUM",
        transactions[is_fraud] = 1,                             "LOW",
        "MINIMAL"
    )

Day Number =
    INT(transactions[time_seconds] / 86400) + 1


## Time Intelligence Measures (if connected to date table)

Fraud Rate Previous Period =
    CALCULATE(
        [Fraud Rate %],
        PREVIOUSDAY('DateTable'[Date])
    )

Fraud Rate Change % =
    DIVIDE(
        [Fraud Rate %] - [Fraud Rate Previous Period],
        [Fraud Rate Previous Period],
        0
    )


# ============================================================
# DASHBOARD LAYOUT SPECIFICATIONS
# ============================================================

Canvas Size    : 1280 × 720 px (16:9 widescreen)
Theme          : Custom — Dark header (#1A237E), white canvas, red accents
Font           : Segoe UI throughout
KPI Cards      : Top strip (full width, 5 equal columns)
Charts Row 1   : 60% width (bar chart) | 40% width (donut)
Charts Row 2   : 50% width (line chart) | 50% width (stacked bar)
Slicers        : Left panel (vertical, 15% canvas width)
Page Navigator : Top right corner (3 page buttons)


# ============================================================
# RECOMMENDED SLICERS
# ============================================================

1. Transaction Type       (Dropdown)
2. Amount Band            (Checkbox list)
3. Risk Tier              (Dropdown)
4. Hour of Day            (Between slider)
5. Day Number             (Toggle 1 / 2)
6. Amount Range           (Numeric range filter: $0 – $25,691)
