# ============================================================
# Project  : Financial Transaction Risk & Fraud Pattern Analysis
# Dataset  : Kaggle Credit Card Fraud Detection (creditcard.csv)
# Author   : Deepak Dwivedi
# Tool     : Python 3.x | Pandas | Matplotlib | Seaborn
# ============================================================

# ── CELL 1: Import Libraries ────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['font.size'] = 12
print("✅ Libraries loaded successfully.")


# ── CELL 2: Load Dataset ────────────────────────────────────
df = pd.read_csv("creditcard.csv")

print(f"📦 Dataset Shape : {df.shape}")
print(f"📋 Columns       : {list(df.columns)}")
print(f"\n🔍 First 5 rows:")
df.head()


# ── CELL 3: Data Summary & Structure ───────────────────────
print("=" * 55)
print("  DATA STRUCTURE & TYPE OVERVIEW")
print("=" * 55)
print(df.dtypes)
print("\n")
print("=" * 55)
print("  DESCRIPTIVE STATISTICS — AMOUNT & TIME")
print("=" * 55)
print(df[['Time', 'Amount', 'Class']].describe().round(4))


# ── CELL 4: Missing Value & Duplicate Check ─────────────────
print("=" * 55)
print("  MISSING VALUE AUDIT")
print("=" * 55)
missing = df.isnull().sum()
print(missing[missing > 0] if missing.sum() > 0 else "✅ No missing values found.")

print("\n" + "=" * 55)
print("  DUPLICATE ROW CHECK")
print("=" * 55)
dupes = df.duplicated().sum()
print(f"{'⚠️  Duplicates found: ' + str(dupes) if dupes > 0 else '✅ No duplicate rows found.'}")


# ── CELL 5: Class Distribution — Fraud vs. Legitimate ───────
fraud_counts   = df['Class'].value_counts()
fraud_pct      = df['Class'].value_counts(normalize=True) * 100
fraud_summary  = pd.DataFrame({
    'Transaction Type' : ['Legitimate', 'Fraudulent'],
    'Count'            : [fraud_counts[0], fraud_counts[1]],
    'Percentage (%)'   : [round(fraud_pct[0], 4), round(fraud_pct[1], 4)]
})
print("=" * 55)
print("  FRAUD vs. LEGITIMATE DISTRIBUTION")
print("=" * 55)
print(fraud_summary.to_string(index=False))

# Visualization — class imbalance
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
colors = ['#2196F3', '#F44336']

axes[0].bar(['Legitimate', 'Fraudulent'], fraud_counts.values, color=colors, edgecolor='black', width=0.5)
axes[0].set_title('Transaction Count: Legitimate vs. Fraudulent', fontweight='bold')
axes[0].set_ylabel('Number of Transactions')
for bar, val in zip(axes[0].patches, fraud_counts.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                 f'{val:,}', ha='center', fontweight='bold')

axes[1].pie(fraud_counts.values, labels=['Legitimate', 'Fraudulent'],
            autopct='%1.3f%%', colors=colors, startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
axes[1].set_title('Class Distribution (Proportion)', fontweight='bold')

plt.suptitle('Class Imbalance: Credit Card Fraud Dataset', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/01_class_distribution.png', dpi=150, bbox_inches='tight')
plt.show()


# ── CELL 6: Transaction Amount Analysis ─────────────────────
legit_amt = df[df['Class'] == 0]['Amount']
fraud_amt = df[df['Class'] == 1]['Amount']

print("=" * 55)
print("  AMOUNT STATISTICS: LEGITIMATE vs. FRAUDULENT")
print("=" * 55)
amount_stats = pd.DataFrame({
    'Metric'      : ['Count', 'Mean ($)', 'Median ($)', 'Std Dev', 'Min ($)', 'Max ($)'],
    'Legitimate'  : [len(legit_amt), round(legit_amt.mean(),2), round(legit_amt.median(),2),
                     round(legit_amt.std(),2), round(legit_amt.min(),2), round(legit_amt.max(),2)],
    'Fraudulent'  : [len(fraud_amt), round(fraud_amt.mean(),2), round(fraud_amt.median(),2),
                     round(fraud_amt.std(),2), round(fraud_amt.min(),2), round(fraud_amt.max(),2)]
})
print(amount_stats.to_string(index=False))

# Visualization — amount distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(legit_amt, bins=60, color='#2196F3', alpha=0.75, edgecolor='black', label='Legitimate')
axes[0].hist(fraud_amt, bins=60, color='#F44336', alpha=0.75, edgecolor='black', label='Fraudulent')
axes[0].set_title('Transaction Amount Distribution', fontweight='bold')
axes[0].set_xlabel('Amount (USD)')
axes[0].set_ylabel('Frequency')
axes[0].legend()
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

# Box plot comparison
axes[1].boxplot([legit_amt, fraud_amt], labels=['Legitimate', 'Fraudulent'],
                patch_artist=True,
                boxprops=dict(facecolor='#E3F2FD'),
                medianprops=dict(color='#F44336', linewidth=2))
axes[1].set_title('Amount Spread: Boxplot Comparison', fontweight='bold')
axes[1].set_ylabel('Transaction Amount (USD)')
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

plt.suptitle('Transaction Amount Analysis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/02_amount_analysis.png', dpi=150, bbox_inches='tight')
plt.show()


# ── CELL 7: Amount Segmentation (Risk Buckets) ──────────────
def assign_risk_band(amount):
    if amount < 10:
        return '1. Micro (< $10)'
    elif amount < 100:
        return '2. Low ($10-$99)'
    elif amount < 500:
        return '3. Medium ($100-$499)'
    elif amount < 1000:
        return '4. High ($500-$999)'
    elif amount < 5000:
        return '5. Premium ($1K-$4,999)'
    else:
        return '6. Very High (>= $5K)'

df['amount_band'] = df['Amount'].apply(assign_risk_band)

band_summary = df.groupby('amount_band').agg(
    total_transactions=('Class', 'count'),
    fraud_count=('Class', 'sum'),
    total_amount=('Amount', 'sum')
).reset_index()
band_summary['fraud_rate_pct'] = (band_summary['fraud_count'] / band_summary['total_transactions'] * 100).round(2)
band_summary['fraud_exposure'] = df[df['Class']==1].groupby('amount_band')['Amount'].sum().values

print("=" * 65)
print("  FRAUD RATE BY TRANSACTION AMOUNT BAND")
print("=" * 65)
print(band_summary[['amount_band','total_transactions','fraud_count','fraud_rate_pct']].to_string(index=False))

# Visualization
fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(band_summary['amount_band'], band_summary['fraud_rate_pct'],
              color='#EF5350', edgecolor='black', alpha=0.85)
ax.set_title('Fraud Rate (%) by Transaction Amount Band', fontweight='bold', fontsize=13)
ax.set_xlabel('Amount Segment')
ax.set_ylabel('Fraud Rate (%)')
ax.tick_params(axis='x', rotation=20)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{bar.get_height():.2f}%', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/03_fraud_rate_by_amount_band.png', dpi=150, bbox_inches='tight')
plt.show()


# ── CELL 8: Time-Based Fraud Analysis ───────────────────────
df['hour_of_day'] = (df['Time'] / 3600).astype(int) % 24

hourly = df.groupby(['hour_of_day', 'Class']).size().unstack(fill_value=0).reset_index()
hourly.columns = ['hour', 'legitimate', 'fraudulent']
hourly['fraud_rate'] = (hourly['fraudulent'] / (hourly['legitimate'] + hourly['fraudulent']) * 100).round(4)

fig, axes = plt.subplots(2, 1, figsize=(14, 9))

# Transaction volume by hour
axes[0].bar(hourly['hour'], hourly['legitimate'], label='Legitimate',
            color='#42A5F5', alpha=0.8, edgecolor='white')
axes[0].bar(hourly['hour'], hourly['fraudulent'], bottom=hourly['legitimate'],
            label='Fraudulent', color='#EF5350', alpha=0.85, edgecolor='white')
axes[0].set_title('Hourly Transaction Volume: Legitimate vs. Fraudulent', fontweight='bold')
axes[0].set_xlabel('Hour of Day')
axes[0].set_ylabel('Number of Transactions')
axes[0].set_xticks(range(0, 24))
axes[0].legend()

# Fraud rate by hour
axes[1].plot(hourly['hour'], hourly['fraud_rate'], color='#D32F2F',
             marker='o', linewidth=2, markersize=6, markerfacecolor='white', markeredgewidth=2)
axes[1].fill_between(hourly['hour'], hourly['fraud_rate'], alpha=0.15, color='#EF5350')
axes[1].set_title('Fraud Rate (%) by Hour of Day', fontweight='bold')
axes[1].set_xlabel('Hour of Day')
axes[1].set_ylabel('Fraud Rate (%)')
axes[1].set_xticks(range(0, 24))

plt.suptitle('Time-Based Fraud Pattern Analysis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/04_time_fraud_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

print("📊 Peak fraud hours:")
print(hourly.nlargest(5, 'fraud_rate')[['hour', 'fraudulent', 'fraud_rate']].to_string(index=False))


# ── CELL 9: Correlation Heatmap (PCA Features) ──────────────
# Only V1–V10 shown for readability; extend to V28 as needed
feature_cols = [f'V{i}' for i in range(1, 11)] + ['Amount', 'Class']
corr_matrix  = df[feature_cols].corr()

plt.figure(figsize=(12, 8))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, linewidths=0.5,
            cbar_kws={'shrink': 0.8})
plt.title('Correlation Heatmap: Key Features vs. Fraud Class', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig('outputs/05_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()


# ── CELL 10: Key Business Insights Summary ──────────────────
total_txns        = len(df)
total_fraud       = df['Class'].sum()
fraud_rate        = round(total_fraud / total_txns * 100, 4)
total_volume      = round(df['Amount'].sum(), 2)
fraud_exposure    = round(df[df['Class']==1]['Amount'].sum(), 2)
avg_fraud_amt     = round(df[df['Class']==1]['Amount'].mean(), 2)
avg_legit_amt     = round(df[df['Class']==0]['Amount'].mean(), 2)
peak_hour         = hourly.loc[hourly['fraud_rate'].idxmax(), 'hour']
highest_band      = band_summary.loc[band_summary['fraud_rate_pct'].idxmax(), 'amount_band']

print("=" * 60)
print("  📊  EXECUTIVE RISK SUMMARY — FRAUD ANALYSIS")
print("=" * 60)
print(f"  Total Transactions     : {total_txns:,}")
print(f"  Total Fraudulent Cases : {total_fraud:,}")
print(f"  Overall Fraud Rate     : {fraud_rate}%")
print(f"  Total Transaction Vol  : ${total_volume:,.2f}")
print(f"  Total Fraud Exposure   : ${fraud_exposure:,.2f}")
print(f"  Avg Fraud Amount       : ${avg_fraud_amt:,.2f}")
print(f"  Avg Legitimate Amount  : ${avg_legit_amt:,.2f}")
print(f"  Peak Fraud Hour        : {peak_hour}:00")
print(f"  Highest Risk Band      : {highest_band}")
print("=" * 60)
print("\n📌 KEY BUSINESS INSIGHTS:")
print(f"  1. Only {fraud_rate}% of transactions are fraudulent — severe class imbalance.")
print(f"  2. Fraudulent transactions average ${avg_fraud_amt} vs. ${avg_legit_amt} for legitimate ones.")
print(f"  3. Total financial exposure from fraud: ${fraud_exposure:,.2f}.")
print(f"  4. Peak fraud activity occurs around hour {peak_hour}:00 (late-night/early-morning window).")
print(f"  5. Amount band '{highest_band}' shows the highest fraud concentration.")
print("\n✅ EDA Complete. Proceed to Power BI Dashboard or ML Modelling.")
