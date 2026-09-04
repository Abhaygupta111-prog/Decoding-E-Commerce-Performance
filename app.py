"""
Cart2Insights Streamlit Dashboard
Run with: streamlit run streamlit/app.py

Works against SQLite (default, zero setup) or MySQL — set DB_ENGINE in .env.
Date truncation/diffing is done in pandas rather than SQL so the same
queries work on both backends without dialect-specific functions.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_engine
import queries as q

st.set_page_config(page_title="Cart2Insights", layout="wide", page_icon="🛒")

st.title("🛒 Cart2Insights: E-Commerce Performance Dashboard")


# --- Data loading (cached) -------------------------------------------------
@st.cache_resource
def get_db_engine():
    return get_engine()


@st.cache_data(ttl=3600)
def run_query(query: str) -> pd.DataFrame:
    engine = get_db_engine()
    return pd.read_sql(query, engine)


# --- Sidebar navigation -----------------------------------------------------
section = st.sidebar.radio(
    "Select Section",
    [
        "Business Overview",
        "Sales Analysis",
        "Customer Analysis",
        "Seller & Product Analysis",
        "Delivery Analysis",
        "Customer Experience",
    ],
)

# --- 1. Business Overview ----------------------------------------------------
if section == "Business Overview":
    st.header("Business Overview")
    df = run_query(q.BUSINESS_OVERVIEW)
    row = df.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${row['total_revenue']:,.0f}")
    c2.metric("Total Orders", f"{row['total_orders']:,}")
    c3.metric("Total Customers", f"{row['total_customers']:,}")
    c4, c5, c6 = st.columns(3)
    c4.metric("Total Sellers", f"{row['total_sellers']:,}")
    c5.metric("Avg Order Value", f"${row['avg_order_value']:,.2f}")
    c6.metric("Avg Review Score", f"{row['avg_review_score']:.2f} / 5")

    status_df = run_query(q.ORDERS_BY_STATUS)
    st.plotly_chart(px.pie(status_df, names="order_status", values="n", title="Orders by Status"),
                     use_container_width=True)

# --- 2. Sales Analysis ---------------------------------------------------
elif section == "Sales Analysis":
    st.header("Sales Analysis")

    raw = run_query(q.SALES_RAW_FOR_TREND)
    raw["order_purchase_timestamp"] = pd.to_datetime(raw["order_purchase_timestamp"])
    raw["month"] = raw["order_purchase_timestamp"].dt.to_period("M").astype(str)
    trend = raw.groupby("month").apply(lambda x: (x["price"] + x["freight_value"]).sum()).reset_index(name="revenue")
    st.plotly_chart(px.line(trend, x="month", y="revenue", title="Monthly Revenue Trend"),
                     use_container_width=True)

    category_rev = run_query(q.REVENUE_BY_CATEGORY)
    st.plotly_chart(px.bar(category_rev, x="category", y="revenue", title="Top 15 Categories by Revenue"),
                     use_container_width=True)

    state_rev = run_query(q.REVENUE_BY_STATE)
    st.plotly_chart(px.bar(state_rev, x="customer_state", y="revenue", title="Revenue by Customer State"),
                     use_container_width=True)

# --- 3. Customer Analysis -------------------------------------------------
elif section == "Customer Analysis":
    st.header("Customer Analysis")

    repeat_vs_new = run_query(q.REPEAT_VS_NEW_CUSTOMERS)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.pie(repeat_vs_new, names="customer_type", values="num_customers",
                                title="Repeat vs New Customers"), use_container_width=True)

    top_customers = run_query(q.TOP_CUSTOMERS_BY_SPEND)
    with col2:
        st.plotly_chart(px.bar(top_customers, x="customer_unique_id", y="total_spent",
                                title="Top 10 Customers by Spend"), use_container_width=True)

    dist_state = run_query(q.CUSTOMERS_BY_STATE)
    st.plotly_chart(px.bar(dist_state, x="customer_state", y="n", title="Customer Distribution by State"),
                     use_container_width=True)

# --- 4. Seller & Product Analysis -----------------------------------------
elif section == "Seller & Product Analysis":
    st.header("Seller & Product Analysis")

    top_sellers = run_query(q.TOP_SELLERS)
    st.plotly_chart(px.bar(top_sellers, x="seller_id", y="revenue", title="Top 10 Sellers by Revenue"),
                     use_container_width=True)

    seller_ratings = run_query(q.TOP_RATED_SELLERS)
    st.plotly_chart(px.bar(seller_ratings, x="seller_id", y="avg_review_score",
                            title="Top 10 Rated Sellers (min. 10 orders)"), use_container_width=True)

    category_perf = run_query(q.TOP_CATEGORIES_BY_UNITS)
    st.plotly_chart(px.bar(category_perf, x="category", y="units_sold", title="Top 15 Categories by Units Sold"),
                     use_container_width=True)

# --- 5. Delivery Analysis -------------------------------------------------
elif section == "Delivery Analysis":
    st.header("Delivery Analysis")

    raw = run_query(q.DELIVERY_RAW)
    for c in raw.columns:
        raw[c] = pd.to_datetime(raw[c])
    raw["delivery_days"] = (raw["order_delivered_customer_date"] - raw["order_purchase_timestamp"]).dt.days
    raw["is_delayed"] = raw["order_delivered_customer_date"] > raw["order_estimated_delivery_date"]

    c1, c2 = st.columns(2)
    c1.metric("Avg Delivery Time", f"{raw['delivery_days'].mean():.1f} days")
    c2.metric("On-Time Delivery Rate", f"{(~raw['is_delayed']).mean()*100:.1f}%")

    status_split = raw["is_delayed"].map({True: "Delayed", False: "On-Time"}).value_counts().reset_index()
    status_split.columns = ["status", "count"]
    st.plotly_chart(px.pie(status_split, names="status", values="count", title="On-Time vs Delayed Orders"),
                     use_container_width=True)

    delay_review = run_query(q.DELAY_VS_REVIEW_RAW)
    delay_review["order_delivered_customer_date"] = pd.to_datetime(delay_review["order_delivered_customer_date"])
    delay_review["order_estimated_delivery_date"] = pd.to_datetime(delay_review["order_estimated_delivery_date"])
    delay_review["delivery_status"] = (delay_review["order_delivered_customer_date"] >
                                        delay_review["order_estimated_delivery_date"]).map({True: "Delayed", False: "On-Time"})
    summary = delay_review.groupby("delivery_status")["review_score"].mean().reset_index()
    st.plotly_chart(px.bar(summary, x="delivery_status", y="review_score",
                            title="Delivery Delay vs Avg Review Score"), use_container_width=True)

# --- 6. Customer Experience ------------------------------------------------
elif section == "Customer Experience":
    st.header("Customer Experience")

    dist = run_query(q.REVIEW_SCORE_DISTRIBUTION)
    st.plotly_chart(px.bar(dist, x="review_score", y="num_reviews", title="Review Score Distribution"),
                     use_container_width=True)

    category_reviews = run_query(q.REVIEW_SCORE_BY_CATEGORY)
    st.plotly_chart(px.bar(category_reviews, x="category", y="avg_score",
                            title="Top 15 Categories by Avg Review Score (min. 20 reviews)"), use_container_width=True)
