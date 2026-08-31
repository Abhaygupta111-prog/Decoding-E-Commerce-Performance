# Cart2Insights: Decoding E-Commerce Performance

## Project Objective
Analyze e-commerce data spanning orders, customers, products, sellers, payments,
deliveries, and reviews to uncover business insights on sales, customer behavior,
seller/product performance, delivery operations, and customer satisfaction.

Built on the Olist Brazilian E-Commerce public dataset (9 tables).

## Tech Stack
Python, Pandas, SQL (SQLite by default / MySQL supported), SQLAlchemy, Streamlit,
Matplotlib/Seaborn/Plotly, SciPy/Statsmodels

## Project Structure
```
cart2insights/
├── data/
│   ├── raw/                          # original CSVs (gitignored)
│   ├── cleaned/                      # cleaned CSVs (gitignored)
│   └── cart2insights.db              # SQLite database (gitignored)
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_quality_analysis.ipynb
│   ├── 03_data_cleaning.ipynb
│   ├── 04_sql_analysis.ipynb
│   ├── 05_feature_engineering.ipynb
│   ├── 06_eda.ipynb
│   └── 07_statistical_analysis.ipynb
├── sql/
│   ├── create_tables.sql
│   └── analysis_queries.sql
├── streamlit/
│   ├── app.py                        # dashboard entry point
│   ├── database.py                   # SQLAlchemy engine (SQLite/MySQL)
│   ├── queries.py                    # centralized SQL query strings
│   └── utils.py                      # data-loading/inspection helpers
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
   - Default (`DB_ENGINE=sqlite`) needs no further setup
   - For MySQL, set `DB_ENGINE=mysql` and fill in `DB_USER`/`DB_PASSWORD`/`DB_NAME`
4. Place raw CSVs in `data/raw/`
5. Run notebooks in order: `01` → `02` → `03` → `04` → `05` → `06` → `07`
6. Launch dashboard: `streamlit run streamlit/app.py`

## Workflow
- **01 Data Understanding** — load and inspect the 9 raw tables
- **02 Data Quality Analysis** — missing values, duplicates, invalid values, PK checks
- **03 Data Cleaning** — resolve each issue found in 02 (dedup, fill, standardize)
- **04 SQL Analysis** — load cleaned data into SQL and run business queries
  (joins, subqueries, CTEs, window functions, aggregations)
- **05 Feature Engineering** — order value, delivery delay, customer spend, seller metrics
- **06 EDA** — univariate/bivariate/multivariate, trend, correlation, distribution
- **07 Statistical Analysis**
  - T-Test: delivery delay vs. review score
  - ANOVA: order value across product categories
  - Chi-Square: payment method vs. order status
- **Streamlit Dashboard** (`streamlit/app.py`) — business overview, sales, customers,
  sellers/products, delivery, customer experience
- **Business Insights** — Observation → Interpretation → Business Impact for each key finding

## Key Findings
- Delayed orders average a **2.27** review score vs. **4.21** for on-time orders
  (t-test, p ≈ 0) — delivery delay is strongly associated with dissatisfaction
- Order value differs significantly across product categories (ANOVA, p ≈ 0)
- Payment method is significantly associated with order status
  (chi-square, χ²=677, p ≈ 1.2×10⁻¹²⁴)
- ~3.1% of customers are repeat buyers (2,997 of 96,096 unique customers)
- Average delivery time is 12.1 days; 6.8% of orders are delivered late

## Business Recommendations
_(fill in as analysis progresses)_
