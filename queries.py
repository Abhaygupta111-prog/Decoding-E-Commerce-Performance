"""
Centralized SQL business queries for Cart2Insights.
Used by streamlit/app.py and notebooks/04_sql_analysis.ipynb so the same
queries back both the dashboard and the analysis notebook.

Kept portable across SQLite and MySQL: no dialect-specific date functions
(DATE_FORMAT, DATEDIFF) — date math is done in pandas after fetching.
"""

# --- 1. Business Overview ---------------------------------------------------

BUSINESS_OVERVIEW = """
SELECT
    (SELECT SUM(payment_value) FROM order_payments) AS total_revenue,
    (SELECT COUNT(DISTINCT order_id) FROM orders) AS total_orders,
    (SELECT COUNT(DISTINCT customer_id) FROM customers) AS total_customers,
    (SELECT COUNT(DISTINCT seller_id) FROM sellers) AS total_sellers,
    (SELECT AVG(payment_value) FROM order_payments) AS avg_order_value,
    (SELECT AVG(review_score) FROM order_reviews) AS avg_review_score
"""

ORDERS_BY_STATUS = """
SELECT order_status, COUNT(*) AS n
FROM orders
GROUP BY order_status
ORDER BY n DESC
"""

# --- 2. Sales Analysis -------------------------------------------------------

SALES_RAW_FOR_TREND = """
SELECT o.order_purchase_timestamp, oi.price, oi.freight_value
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
"""

REVENUE_BY_CATEGORY = """
SELECT ct.product_category_name_english AS category, SUM(oi.price) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY revenue DESC
LIMIT 15
"""

REVENUE_BY_STATE = """
SELECT c.customer_state, SUM(oi.price) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY revenue DESC
"""

TOP_SELLING_PRODUCTS = """
SELECT oi.product_id, ct.product_category_name_english AS category,
       COUNT(*) AS units_sold, SUM(oi.price) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY oi.product_id, category
ORDER BY units_sold DESC
LIMIT 10
"""

# --- 3. Customer Analysis ----------------------------------------------------

REPEAT_VS_NEW_CUSTOMERS = """
SELECT CASE WHEN order_count > 1 THEN 'Repeat' ELSE 'New' END AS customer_type,
       COUNT(*) AS num_customers
FROM (
    SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
) sub
GROUP BY customer_type
"""

TOP_CUSTOMERS_BY_SPEND = """
SELECT c.customer_unique_id, SUM(oi.price + oi.freight_value) AS total_spent,
       COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_unique_id
ORDER BY total_spent DESC
LIMIT 10
"""

CUSTOMERS_BY_STATE = """
SELECT customer_state, COUNT(*) AS n
FROM customers
GROUP BY customer_state
ORDER BY n DESC
"""

# --- 4. Seller & Product Analysis --------------------------------------------

TOP_SELLERS = """
SELECT seller_id, SUM(price) AS revenue, COUNT(DISTINCT order_id) AS orders
FROM order_items
GROUP BY seller_id
ORDER BY revenue DESC
LIMIT 10
"""

TOP_RATED_SELLERS = """
SELECT oi.seller_id, COUNT(DISTINCT oi.order_id) AS order_count,
       AVG(r.review_score) AS avg_review_score
FROM order_items oi
JOIN order_reviews r ON oi.order_id = r.order_id
GROUP BY oi.seller_id
HAVING order_count >= 10
ORDER BY avg_review_score DESC
LIMIT 10
"""

TOP_CATEGORIES_BY_UNITS = """
SELECT ct.product_category_name_english AS category, COUNT(*) AS units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY units_sold DESC
LIMIT 15
"""

# --- 5. Delivery Analysis -----------------------------------------------------

DELIVERY_RAW = """
SELECT order_purchase_timestamp, order_delivered_customer_date, order_estimated_delivery_date
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
"""

DELIVERY_BY_STATE_RAW = """
SELECT c.customer_state, o.order_purchase_timestamp,
       o.order_delivered_customer_date, o.order_estimated_delivery_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
"""

DELAY_VS_REVIEW_RAW = """
SELECT o.order_id, o.order_delivered_customer_date, o.order_estimated_delivery_date, r.review_score
FROM orders o
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_delivered_customer_date IS NOT NULL
"""

# Alias used by notebooks/04_sql_analysis.ipynb
DELAY_VS_REVIEW = DELAY_VS_REVIEW_RAW

# --- 6. Customer Experience ---------------------------------------------------

REVIEW_SCORE_DISTRIBUTION = """
SELECT review_score, COUNT(*) AS num_reviews
FROM order_reviews
GROUP BY review_score
ORDER BY review_score
"""

REVIEW_SCORE_BY_CATEGORY = """
SELECT ct.product_category_name_english AS category,
       AVG(r.review_score) AS avg_score, COUNT(*) AS n
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
HAVING n >= 20
ORDER BY avg_score DESC
LIMIT 15
"""
