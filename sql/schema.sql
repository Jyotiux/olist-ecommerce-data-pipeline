CREATE TABLE dim_customers (
	customer_unique_id TEXT PRIMARY KEY,
	customer_city TEXT,
	customer_state TEXT
);

CREATE TABLE dim_products (
	product_id TEXT PRIMARY KEY,
	product_category_name_english TEXT
);

CREATE TABLE fact_orders (
	order_id TEXT PRIMARY KEY,
	customer_unique_id TEXT REFERENCES dim_customers(customer_unique_id),
	order_purchase_timestamp TIMESTAMP,
	order_status TEXT,
	item_count INTEGER,
	product_value NUMERIC(12, 2),
	freight_value NUMERIC(12, 2),
	payment_value NUMERIC(12, 2)
);

CREATE TABLE monthly_sales (
	month TEXT PRIMARY KEY,
	order_count INTEGER,
	product_revenue NUMERIC(14, 2),
	freight_revenue NUMERIC(14, 2),
	total_revenue NUMERIC(14, 2),
	average_order_value NUMERIC(14, 2)
);

CREATE TABLE customer_metrics (
	customer_unique_id TEXT PRIMARY KEY REFERENCES dim_customers(customer_unique_id),
	total_orders INTEGER,
	total_spend NUMERIC(14, 2),
	first_purchase_date TIMESTAMP,
	last_purchase_date TIMESTAMP
);
