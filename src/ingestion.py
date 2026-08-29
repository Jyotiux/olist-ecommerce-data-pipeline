from pathlib import Path

import pandas as pd


DATA_FILES = {
	"customers": "olist_customers_dataset.csv",
	"orders": "olist_orders_dataset.csv",
	"order_items": "olist_order_items_dataset.csv",
	"payments": "olist_order_payments_dataset.csv",
	"products": "olist_products_dataset.csv",
	"category_translation": "product_category_name_translation.csv",
}


def load_data(raw_data_dir: str | Path = "data/raw") -> dict[str, pd.DataFrame]:
	raw_data_path = Path(raw_data_dir)
	file_paths = {
		name: raw_data_path / filename for name, filename in DATA_FILES.items()
	}
	missing_files = [
		str(path) for path in file_paths.values() if not path.is_file()
	]

	if missing_files:
		raise FileNotFoundError(
			"Missing required dataset files: " + ", ".join(missing_files)
		)

	return {
		name: pd.read_csv(path) for name, path in file_paths.items()
	}


def inspect_data(raw_data_dir: str | Path = "data/raw") -> None:
	dataframes = load_data(raw_data_dir)

	for dataset_name, df in dataframes.items():
		print(f"dataset name: {dataset_name}")
		print(f"row count: {df.shape[0]}")
		print(f"column count: {df.shape[1]}")
		print(f"column names: {list(df.columns)}")
		print("data types:")
		for column, dtype in df.dtypes.items():
			print(f"  {column}: {dtype}")
		print("null count by column:")
		for column, null_count in df.isna().sum().items():
			print(f"  {column}: {null_count}")
		print(f"duplicate row count: {int(df.duplicated().sum())}")
		print("-" * 80)


if __name__ == "__main__":
	inspect_data()
