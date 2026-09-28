USE sales_db;

-- 1. Monthly total sales
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    COUNT(DISTINCT order_id)        AS total_orders,
    SUM(quantity)                   AS units_sold,
    ROUND(SUM(revenue), 2)          AS total_revenue
FROM sales
GROUP BY month
ORDER BY month;

-- 2. Top 5 best-selling products (revenue ke hisaab se)
SELECT
    p.product_name,
    SUM(s.quantity)          AS units_sold,
    ROUND(SUM(s.revenue), 2) AS total_revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC
LIMIT 5;

-- 3. Region-wise revenue
SELECT
    region,
    ROUND(SUM(revenue), 2)                                         AS total_revenue,
    ROUND(100 * SUM(revenue) / (SELECT SUM(revenue) FROM sales), 2) AS revenue_share_pct
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- 4. Category-wise sales (JOIN products + sales)
SELECT
    p.category,
    SUM(s.quantity)          AS units_sold,
    ROUND(SUM(s.revenue), 2) AS total_revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;
