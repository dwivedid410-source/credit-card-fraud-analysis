-- ============================================================
-- Project  : Financial Transaction Risk & Fraud Pattern Analysis
-- Dataset  : Kaggle Credit Card Fraud Detection (creditcard.csv)
-- Author   : Deepak Dwivedi
-- Tool     : MySQL 8.0+
-- ============================================================

-- ─────────────────────────────────────────
-- SECTION 1: DATABASE & TABLE SETUP
-- ─────────────────────────────────────────

CREATE DATABASE IF NOT EXISTS fraud_detection;
USE fraud_detection;

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    time_seconds  FLOAT          NOT NULL COMMENT 'Seconds elapsed since first transaction',
    v1  FLOAT, v2  FLOAT, v3  FLOAT, v4  FLOAT, v5  FLOAT,
    v6  FLOAT, v7  FLOAT, v8  FLOAT, v9  FLOAT, v10 FLOAT,
    v11 FLOAT, v12 FLOAT, v13 FLOAT, v14 FLOAT, v15 FLOAT,
    v16 FLOAT, v17 FLOAT, v18 FLOAT, v19 FLOAT, v20 FLOAT,
    v21 FLOAT, v22 FLOAT, v23 FLOAT, v24 FLOAT, v25 FLOAT,
    v26 FLOAT, v27 FLOAT, v28 FLOAT,
    amount        DECIMAL(10,2)  NOT NULL COMMENT 'Transaction amount in USD',
    is_fraud      TINYINT(1)     NOT NULL COMMENT '1 = Fraudulent, 0 = Legitimate'
);

-- Load data from CSV (update path to match your environment)
-- LOAD DATA INFILE '/path/to/creditcard.csv'
-- INTO TABLE transactions
-- FIELDS TERMINATED BY ','
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (time_seconds, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
--  v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
--  v21, v22, v23, v24, v25, v26, v27, v28, amount, is_fraud);


-- ─────────────────────────────────────────
-- SECTION 2: BASIC VALIDATION & OVERVIEW
-- ─────────────────────────────────────────

-- 2.1 Total transaction count by class
SELECT
    is_fraud,
    CASE WHEN is_fraud = 1 THEN 'Fraudulent' ELSE 'Legitimate' END AS transaction_type,
    COUNT(*)                                                        AS total_transactions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 4)             AS percentage
FROM transactions
GROUP BY is_fraud;

-- 2.2 Key financial summary
SELECT
    MIN(amount)    AS min_amount,
    MAX(amount)    AS max_amount,
    ROUND(AVG(amount), 2)  AS avg_amount,
    ROUND(SUM(amount), 2)  AS total_volume_usd,
    COUNT(*)               AS total_transactions
FROM transactions;


-- ─────────────────────────────────────────
-- SECTION 3: FRAUD RATE ANALYSIS
-- ─────────────────────────────────────────

-- 3.1 Overall fraud rate
SELECT
    COUNT(*)                                                 AS total_transactions,
    SUM(is_fraud)                                            AS total_fraudulent,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 4)              AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) AS total_fraud_amount_usd,
    ROUND(SUM(CASE WHEN is_fraud = 0 THEN amount ELSE 0 END), 2) AS total_legit_amount_usd
FROM transactions;

-- 3.2 Fraud vs. Legitimate average transaction amount
SELECT
    CASE WHEN is_fraud = 1 THEN 'Fraudulent' ELSE 'Legitimate' END AS transaction_type,
    COUNT(*)                   AS transaction_count,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(MIN(amount), 2)      AS min_amount,
    ROUND(MAX(amount), 2)      AS max_amount,
    ROUND(SUM(amount), 2)      AS total_amount
FROM transactions
GROUP BY is_fraud
ORDER BY is_fraud DESC;


-- ─────────────────────────────────────────
-- SECTION 4: AMOUNT SEGMENTATION
-- ─────────────────────────────────────────

-- 4.1 Transaction amount buckets — volume and fraud rate per bracket
SELECT
    amount_band,
    COUNT(*)                                            AS total_transactions,
    SUM(is_fraud)                                       AS fraud_count,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 2)         AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount END), 2) AS fraud_exposure_usd
FROM (
    SELECT
        amount,
        is_fraud,
        CASE
            WHEN amount < 10        THEN '1. Micro        (< $10)'
            WHEN amount < 100       THEN '2. Low     ($10 - $99)'
            WHEN amount < 500       THEN '3. Medium ($100 - $499)'
            WHEN amount < 1000      THEN '4. High   ($500 - $999)'
            WHEN amount < 5000      THEN '5. Premium ($1K - $4,999)'
            ELSE                         '6. Very High   (>= $5K)'
        END AS amount_band
    FROM transactions
) AS segmented
GROUP BY amount_band
ORDER BY amount_band;


-- ─────────────────────────────────────────
-- SECTION 5: RISK SEGMENTATION USING CTE
-- ─────────────────────────────────────────

-- 5.1 CTE-based risk tier assignment with full metrics
WITH transaction_metrics AS (
    SELECT
        id,
        amount,
        is_fraud,
        CASE
            WHEN amount >= 5000                          THEN 'CRITICAL'
            WHEN amount >= 1000 AND is_fraud = 1         THEN 'HIGH'
            WHEN amount >= 500  AND is_fraud = 1         THEN 'MEDIUM'
            WHEN is_fraud = 1                            THEN 'LOW'
            ELSE                                              'MINIMAL'
        END AS risk_tier
    FROM transactions
),
risk_summary AS (
    SELECT
        risk_tier,
        COUNT(*)                                        AS transaction_count,
        SUM(is_fraud)                                   AS confirmed_fraud,
        ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 2)     AS fraud_rate_pct,
        ROUND(AVG(amount), 2)                           AS avg_transaction_amt,
        ROUND(SUM(CASE WHEN is_fraud=1 THEN amount END), 2) AS fraud_exposure_usd
    FROM transaction_metrics
    GROUP BY risk_tier
)
SELECT *
FROM risk_summary
ORDER BY
    FIELD(risk_tier, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL');

-- 5.2 CTE: Top 20 highest-risk individual transactions
WITH flagged_transactions AS (
    SELECT
        id,
        amount,
        is_fraud,
        time_seconds,
        ROUND(time_seconds / 3600, 2) AS hours_elapsed,
        CASE
            WHEN amount >= 5000 THEN 'CRITICAL'
            WHEN amount >= 1000 THEN 'HIGH'
            WHEN amount >= 500  THEN 'MEDIUM'
            ELSE 'LOW'
        END AS risk_tier,
        ROW_NUMBER() OVER (ORDER BY amount DESC) AS amount_rank
    FROM transactions
    WHERE is_fraud = 1
)
SELECT *
FROM flagged_transactions
WHERE amount_rank <= 20
ORDER BY amount DESC;


-- ─────────────────────────────────────────
-- SECTION 6: TIME-BASED FRAUD ANALYSIS
-- ─────────────────────────────────────────

-- 6.1 Hourly fraud pattern (fraud peaks by hour of day)
SELECT
    FLOOR(time_seconds / 3600) % 24          AS hour_of_day,
    COUNT(*)                                  AS total_transactions,
    SUM(is_fraud)                             AS fraud_count,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(AVG(CASE WHEN is_fraud=1 THEN amount END), 2) AS avg_fraud_amount
FROM transactions
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- 6.2 Day-level fraud trend (Days 1–2 in dataset = Day index)
SELECT
    FLOOR(time_seconds / 86400) + 1          AS day_number,
    COUNT(*)                                  AS total_transactions,
    SUM(is_fraud)                             AS fraud_count,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud=1 THEN amount ELSE 0 END), 2) AS fraud_exposure_usd
FROM transactions
GROUP BY day_number
ORDER BY day_number;

-- 6.3 Fraud velocity: rolling fraud count per 6-hour window
SELECT
    FLOOR(time_seconds / 21600) AS six_hour_window,
    FLOOR(time_seconds / 21600) * 6 AS window_start_hour,
    COUNT(*)               AS total_txns,
    SUM(is_fraud)          AS fraud_count,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY six_hour_window
ORDER BY six_hour_window;


-- ─────────────────────────────────────────
-- SECTION 7: HIGH-VALUE TRANSACTION ANALYSIS
-- ─────────────────────────────────────────

-- 7.1 All fraudulent high-value transactions (amount > $1,000)
SELECT
    id,
    ROUND(amount, 2)                        AS amount_usd,
    ROUND(time_seconds / 3600, 1)           AS hours_elapsed,
    CASE
        WHEN amount >= 5000 THEN 'CRITICAL'
        WHEN amount >= 2000 THEN 'HIGH'
        ELSE 'ELEVATED'
    END AS risk_label
FROM transactions
WHERE is_fraud = 1
  AND amount > 1000
ORDER BY amount DESC;

-- 7.2 Top 10 highest fraud-exposure amount bands
SELECT
    CASE
        WHEN amount < 10   THEN 'Micro (< $10)'
        WHEN amount < 100  THEN 'Low ($10-$99)'
        WHEN amount < 500  THEN 'Medium ($100-$499)'
        WHEN amount < 1000 THEN 'High ($500-$999)'
        ELSE 'Premium ($1000+)'
    END AS amount_band,
    COUNT(*)                                              AS fraud_transactions,
    ROUND(SUM(amount), 2)                                 AS total_fraud_exposure,
    ROUND(AVG(amount), 2)                                 AS avg_fraud_amount
FROM transactions
WHERE is_fraud = 1
GROUP BY amount_band
ORDER BY total_fraud_exposure DESC;


-- ─────────────────────────────────────────
-- SECTION 8: ADVANCED AGGREGATIONS
-- ─────────────────────────────────────────

-- 8.1 Percentile distribution of fraud amounts
SELECT
    '25th Percentile' AS metric,
    MAX(amount) AS value
FROM (
    SELECT amount FROM transactions WHERE is_fraud = 1
    ORDER BY amount LIMIT 25 -- adjust to dataset size
) AS p25
UNION ALL
SELECT '50th Percentile', ROUND(AVG(amount), 2)
FROM (SELECT amount FROM transactions WHERE is_fraud = 1) AS med
UNION ALL
SELECT '75th Percentile', MAX(amount)
FROM (
    SELECT amount FROM transactions WHERE is_fraud = 1
    ORDER BY amount LIMIT 75
) AS p75
UNION ALL
SELECT 'Max', MAX(amount)
FROM transactions WHERE is_fraud = 1;

-- 8.2 Fraud concentration: what % of fraud comes from top 10% of amounts?
WITH ranked_fraud AS (
    SELECT
        amount,
        NTILE(10) OVER (ORDER BY amount DESC) AS decile
    FROM transactions
    WHERE is_fraud = 1
)
SELECT
    CASE WHEN decile = 1 THEN 'Top 10%' ELSE 'Bottom 90%' END AS segment,
    COUNT(*)               AS fraud_count,
    ROUND(SUM(amount), 2)  AS total_fraud_amount,
    ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 2) AS pct_of_total_fraud
FROM ranked_fraud
GROUP BY CASE WHEN decile = 1 THEN 'Top 10%' ELSE 'Bottom 90%' END;

-- 8.3 Summary scorecard — executive view
SELECT
    COUNT(*)                                                    AS total_transactions,
    SUM(is_fraud)                                               AS total_fraud_cases,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 4)                 AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud=1 THEN amount ELSE 0 END), 2) AS total_fraud_value_usd,
    ROUND(AVG(CASE WHEN is_fraud=1 THEN amount END), 2)         AS avg_fraud_amount,
    ROUND(MAX(CASE WHEN is_fraud=1 THEN amount END), 2)         AS max_fraud_amount,
    ROUND(SUM(amount), 2)                                       AS total_txn_volume_usd
FROM transactions;
