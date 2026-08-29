import os

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from .transformation import transform_data
from dotenv import load_dotenv

load_dotenv()

TABLES_TO_LOAD = [
	"dim_customers",
	"dim_products",
	"fact_orders",
	"monthly_sales",
	"customer_metrics",
]


def load_to_postgres(raw_data_dir: str = "data/raw") -> dict[str, int]:
	transformed_data = transform_data(raw_data_dir)

	connection_url = URL.create(
		drivername="postgresql+psycopg2",
		host=os.environ["DB_HOST"],
		port=os.environ["DB_PORT"],
		database=os.environ["DB_NAME"],
		username=os.environ["DB_USER"],
		password=os.environ["DB_PASSWORD"],
	)
	engine = create_engine(connection_url)

	with engine.begin() as connection:
		connection.execute(
			text(
				"TRUNCATE TABLE fact_orders, customer_metrics, monthly_sales, "
				"dim_products, dim_customers"
			)
		)

		for table_name in TABLES_TO_LOAD:
			transformed_data[table_name].to_sql(
				table_name,
				con=connection,
				if_exists="append",
				index=False,
			)

	row_counts = {
		table_name: len(transformed_data[table_name])
		for table_name in TABLES_TO_LOAD
	}
	for table_name, row_count in row_counts.items():
		print(f"{table_name}: {row_count} rows loaded")

	engine.dispose()
	return row_counts


if __name__ == "__main__":
	load_to_postgres()
