import pandas as pd

from .ingestion import load_data


ORDER_DATETIME_COLUMNS = [
	"order_purchase_timestamp",
	"order_approved_at",
	"order_delivered_carrier_date",
	"order_delivered_customer_date",
	"order_estimated_delivery_date",
]


def clean_data(raw_data_dir: str = "data/raw") -> dict[str, pd.DataFrame]:
	dataframes = load_data(raw_data_dir)
	cleaned_dataframes = {
		name: df.copy() for name, df in dataframes.items()
	}

	orders_df = cleaned_dataframes["orders"]
	for column in ORDER_DATETIME_COLUMNS:
		orders_df[column] = pd.to_datetime(orders_df[column], errors="coerce")

	order_items_df = cleaned_dataframes["order_items"]
	order_items_df["shipping_limit_date"] = pd.to_datetime(
		order_items_df["shipping_limit_date"],
		errors="coerce",
	)

	products_df = cleaned_dataframes["products"]
	products_df["product_category_name"] = products_df[
		"product_category_name"
	].fillna("unknown")

	return cleaned_dataframes
