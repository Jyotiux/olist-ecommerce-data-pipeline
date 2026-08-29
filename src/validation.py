import pandas as pd

from .cleaning import clean_data


def validate_data(raw_data_dir: str = "data/raw") -> dict[str, pd.DataFrame]:
	dataframes = clean_data(raw_data_dir)

	customers_df = dataframes["customers"]
	orders_df = dataframes["orders"]
	order_items_df = dataframes["order_items"]
	payments_df = dataframes["payments"]
	products_df = dataframes["products"]

	if customers_df["customer_id"].isna().any():
		raise ValueError("Check failed: customers.customer_id must not be null.")

	if orders_df["customer_id"].isna().any():
		raise ValueError("Check failed: orders.customer_id must not be null.")

	if orders_df["order_id"].isna().any():
		raise ValueError("Check failed: orders.order_id must not be null.")

	if order_items_df["order_id"].isna().any():
		raise ValueError("Check failed: order_items.order_id must not be null.")

	if payments_df["order_id"].isna().any():
		raise ValueError("Check failed: payments.order_id must not be null.")

	if products_df["product_id"].isna().any():
		raise ValueError("Check failed: products.product_id must not be null.")

	if order_items_df["product_id"].isna().any():
		raise ValueError("Check failed: order_items.product_id must not be null.")

	if customers_df["customer_id"].duplicated().any():
		raise ValueError("Check failed: customers.customer_id must be unique.")

	if orders_df["order_id"].duplicated().any():
		raise ValueError("Check failed: orders.order_id must be unique.")

	valid_customer_ids = set(customers_df["customer_id"])
	missing_customer_ids = ~orders_df["customer_id"].isin(valid_customer_ids)
	if missing_customer_ids.any():
		raise ValueError(
			"Check failed: every orders.customer_id must exist in customers.customer_id."
		)

	valid_order_ids = set(orders_df["order_id"])
	missing_order_ids = ~order_items_df["order_id"].isin(valid_order_ids)
	if missing_order_ids.any():
		raise ValueError(
			"Check failed: every order_items.order_id must exist in orders.order_id."
		)

	valid_product_ids = set(products_df["product_id"])
	missing_product_ids = ~order_items_df["product_id"].isin(valid_product_ids)
	if missing_product_ids.any():
		raise ValueError(
			"Check failed: every order_items.product_id must exist in products.product_id."
		)

	if (order_items_df["price"] < 0).any():
		raise ValueError("Check failed: order_items.price must not be negative.")

	if (order_items_df["freight_value"] < 0).any():
		raise ValueError(
			"Check failed: order_items.freight_value must not be negative."
		)

	if (payments_df["payment_value"] < 0).any():
		raise ValueError("Check failed: payments.payment_value must not be negative.")

	if (payments_df["payment_installments"] < 0).any():
		raise ValueError(
			"Check failed: payments.payment_installments must not be negative."
		)

	return dataframes
