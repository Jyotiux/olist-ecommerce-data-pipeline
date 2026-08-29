import pandas as pd

from .validation import validate_data


def transform_data(raw_data_dir: str = "data/raw") -> dict[str, pd.DataFrame]:
	dataframes = validate_data(raw_data_dir)

	customers_df = dataframes["customers"]
	orders_df = dataframes["orders"]
	order_items_df = dataframes["order_items"]
	payments_df = dataframes["payments"]
	products_df = dataframes["products"]
	category_translation_df = dataframes["category_translation"]

	dim_customers = (
		customers_df[["customer_unique_id", "customer_city", "customer_state"]]
		.groupby("customer_unique_id", as_index=False)
		.agg(
			{
				"customer_city": "first",
				"customer_state": "first",
			}
		)
	)

	dim_products = products_df[["product_id", "product_category_name"]].merge(
		category_translation_df,
		on="product_category_name",
		how="left",
	)[["product_id", "product_category_name_english"]]
	dim_products = dim_products.drop_duplicates(subset=["product_id"])

	order_items_agg = order_items_df.groupby("order_id", as_index=False).agg(
		item_count=("order_id", "size"),
		product_value=("price", "sum"),
		freight_value=("freight_value", "sum"),
	)

	payments_agg = payments_df.groupby("order_id", as_index=False).agg(
		payment_value=("payment_value", "sum"),
	)

	fact_orders = orders_df[[
		"order_id",
		"customer_id",
		"order_purchase_timestamp",
		"order_status",
	]].merge(
		customers_df[["customer_id", "customer_unique_id"]],
		on="customer_id",
		how="left",
	)
	fact_orders = fact_orders.merge(order_items_agg, on="order_id", how="left")
	fact_orders = fact_orders.merge(payments_agg, on="order_id", how="left")

	fact_orders["item_count"] = fact_orders["item_count"].fillna(0).astype(int)
	fact_orders["product_value"] = fact_orders["product_value"].fillna(0.0)
	fact_orders["freight_value"] = fact_orders["freight_value"].fillna(0.0)
	fact_orders["payment_value"] = fact_orders["payment_value"].fillna(0.0)

	fact_orders = fact_orders[[
		"order_id",
		"customer_unique_id",
		"order_purchase_timestamp",
		"order_status",
		"item_count",
		"product_value",
		"freight_value",
		"payment_value",
	]]

	fact_orders_for_monthly = fact_orders.copy()
	fact_orders_for_monthly["month"] = fact_orders_for_monthly[
		"order_purchase_timestamp"
	].dt.to_period("M")

	monthly_sales = fact_orders_for_monthly.groupby("month", as_index=False).agg(
		order_count=("order_id", "count"),
		product_revenue=("product_value", "sum"),
		freight_revenue=("freight_value", "sum"),
		total_revenue=("payment_value", "sum"),
	)
	monthly_sales["average_order_value"] = (
		monthly_sales["total_revenue"] / monthly_sales["order_count"]
	)
	monthly_sales["month"] = monthly_sales["month"].astype(str)

	customer_metrics = fact_orders.groupby(
		"customer_unique_id", as_index=False
	).agg(
		total_orders=("order_id", "count"),
		total_spend=("payment_value", "sum"),
		first_purchase_date=("order_purchase_timestamp", "min"),
		last_purchase_date=("order_purchase_timestamp", "max"),
	)

	return {
		"dim_customers": dim_customers,
		"dim_products": dim_products,
		"fact_orders": fact_orders,
		"monthly_sales": monthly_sales,
		"customer_metrics": customer_metrics,
	}
