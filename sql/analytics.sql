-- 1. Monthly revenue trend
SELECT
	month,
	product_revenue,
	freight_revenue,
	total_revenue
FROM monthly_sales
ORDER BY month;

-- 2. Top 10 customers by total spend
SELECT
	customer_unique_id,
	total_orders,
	total_spend
FROM customer_metrics
ORDER BY total_spend DESC
LIMIT 10;

-- 3. Top customer states by total revenue
SELECT
	dc.customer_state,
	SUM(fo.payment_value) AS total_revenue
FROM fact_orders AS fo
JOIN dim_customers AS dc
	ON fo.customer_unique_id = dc.customer_unique_id
GROUP BY dc.customer_state
ORDER BY total_revenue DESC;

-- 4. Order status distribution
SELECT
	order_status,
	COUNT(*) AS order_count
FROM fact_orders
GROUP BY order_status
ORDER BY order_count DESC;

-- 5. Average order value by month
SELECT
	month,
	average_order_value
FROM monthly_sales
ORDER BY month;
