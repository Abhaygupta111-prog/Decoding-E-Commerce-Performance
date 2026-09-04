-- ============================================================
-- Cart2Insights: Business Analysis Queries
-- Covers: SELECT/WHERE/ORDER BY, GROUP BY/HAVING, Joins,
-- Subqueries, CTEs, Window functions, Aggregations
-- ============================================================

-- 1. BUSINESS OVERVIEW -----------------------------------------

-- Total revenue, orders, customers, sellers, avg order value, avg review score
SELECT
    (SELECT SUM(payment_value) FROM order_payments) AS total_revenue,
    (SELECT COUNT(DISTINCT order_id) FROM orders) AS total_orders,
    (SELECT COUNT(DISTINCT customer_id) FROM customers) AS total_customers,
    (SELECT COUNT(DISTINCT seller_id) FROM sellers) AS total_sellers,
    (SELECT AVG(payment_value) FROM order_payments) AS avg_order_value,
    (SELECT AVG(review_score) FROM order_reviews) AS avg_review_score;


-- 2. SALES ANALYSIS ---------------------------------------------

-- Monthly revenue trend
SELECT
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS order_month,
    SUM(oi.price + oi.freight_value) AS monthly_revenue,
    COUNT(DISTINCT o.order_id) AS order_count
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY order_month
ORDER BY order_month;

-- Revenue by product category
SELECT
    ct.product_category_name_english AS category,
    SUM(oi.price) AS category_revenue,
    COUNT(oi.order_id) AS items_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY category_revenue DESC;

-- Top 10 selling products
SELECT
    oi.product_id,
    ct.product_category_name_english AS category,
    COUNT(*) AS units_sold,
    SUM(oi.price) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY oi.product_id, category
ORDER BY units_sold DESC
LIMIT 10;

-- Sales by customer state
SELECT
    c.customer_state,
    SUM(oi.price) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY revenue DESC;


-- 3. CUSTOMER ANALYSIS --------------------------------------------

-- Customer spending + order count (CTE)
WITH customer_orders AS (
    SELECT
        o.customer_id,
        o.order_id,
        SUM(oi.price + oi.freight_value) AS order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id, o.order_id
)
SELECT
    customer_id,
    COUNT(order_id) AS total_orders,
    SUM(order_total) AS total_spending,
    AVG(order_total) AS avg_order_value
FROM customer_orders
GROUP BY customer_id
ORDER BY total_spending DESC;

-- Repeat vs new customers (using customer_unique_id)
SELECT
    CASE WHEN order_count > 1 THEN 'Repeat' ELSE 'New' END AS customer_type,
    COUNT(*) AS num_customers
FROM (
    SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
) sub
GROUP BY customer_type;

-- Top 10 customers by spend
SELECT
    c.customer_unique_id,
    SUM(oi.price + oi.freight_value) AS total_spent,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_unique_id
ORDER BY total_spent DESC
LIMIT 10;


-- 4. SELLER & PRODUCT ANALYSIS -------------------------------------

-- Top sellers by revenue, with running rank (window function)
SELECT
    seller_id,
    seller_revenue,
    RANK() OVER (ORDER BY seller_revenue DESC) AS revenue_rank
FROM (
    SELECT seller_id, SUM(price) AS seller_revenue
    FROM order_items
    GROUP BY seller_id
) s
ORDER BY revenue_rank
LIMIT 10;

-- Seller average review score (HAVING to filter low-volume sellers)
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS order_count,
    AVG(r.review_score) AS avg_review_score
FROM order_items oi
JOIN order_reviews r ON oi.order_id = r.order_id
GROUP BY oi.seller_id
HAVING order_count >= 10
ORDER BY avg_review_score DESC;


-- 5. DELIVERY ANALYSIS ----------------------------------------------

-- Average delivery time (days) and on-time vs delayed split
SELECT
    AVG(DATEDIFF(order_delivered_customer_date, order_purchase_timestamp)) AS avg_delivery_days,
    SUM(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date
             THEN 1 ELSE 0 END) AS on_time_orders,
    SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date
             THEN 1 ELSE 0 END) AS delayed_orders
FROM orders
WHERE order_delivered_customer_date IS NOT NULL;

-- Delivery performance by customer state
SELECT
    c.customer_state,
    AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)) AS avg_delivery_days,
    AVG(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
             THEN 1 ELSE 0 END) AS delay_rate
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY delay_rate DESC;

-- Delivery delay vs review score
SELECT
    CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
         THEN 'Delayed' ELSE 'On-Time' END AS delivery_status,
    AVG(r.review_score) AS avg_review_score,
    COUNT(*) AS num_orders
FROM orders o
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY delivery_status;


-- 6. CUSTOMER EXPERIENCE ----------------------------------------------

-- Review score distribution
SELECT review_score, COUNT(*) AS num_reviews
FROM order_reviews
GROUP BY review_score
ORDER BY review_score;

-- Average review score by product category
SELECT
    ct.product_category_name_english AS category,
    AVG(r.review_score) AS avg_review_score,
    COUNT(*) AS num_reviews
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
HAVING num_reviews >= 20
ORDER BY avg_review_score DESC;
