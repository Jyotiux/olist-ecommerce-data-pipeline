from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


DATA_FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "products": "olist_products_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

ORDER_DATETIME_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def spark_transform_data(raw_data_dir: str = "data/raw") -> dict[str, DataFrame]:
    spark = (
        SparkSession.builder
        .appName("OlistSparkTransformation")
        .master("local[*]")
        .getOrCreate()
    )

    dataframes = {
        name: spark.read.option("header", True).option("inferSchema", True).csv(
            f"{raw_data_dir}/{filename}"
        )
        for name, filename in DATA_FILES.items()
    }

    customers_df = dataframes["customers"]
    orders_df = dataframes["orders"]
    order_items_df = dataframes["order_items"]
    payments_df = dataframes["payments"]
    products_df = dataframes["products"]
    category_translation_df = dataframes["category_translation"]

    dim_customers = customers_df.groupBy("customer_unique_id").agg(
        F.first("customer_city", ignorenulls=True).alias("customer_city"),
        F.first("customer_state", ignorenulls=True).alias("customer_state"),
    ).select(
        "customer_unique_id",
        "customer_city",
        "customer_state",
    )

    dim_products = products_df.select(
        "product_id",
        F.coalesce(F.col("product_category_name"), F.lit("unknown")).alias(
            "product_category_name"
        ),
    ).join(
        category_translation_df,
        on="product_category_name",
        how="left",
    ).groupBy("product_id").agg(
        F.first("product_category_name_english", ignorenulls=True).alias(
            "product_category_name_english"
        ),
    ).select(
        "product_id",
        "product_category_name_english",
    )

    order_items_agg = order_items_df.groupBy("order_id").agg(
        F.count("order_id").alias("item_count"),
        F.sum("price").alias("product_value"),
        F.sum("freight_value").alias("freight_value"),
    )

    payments_agg = payments_df.groupBy("order_id").agg(
        F.sum("payment_value").alias("payment_value"),
    )

    fact_orders = orders_df.select(
        "order_id",
        "customer_id",
        *[
            F.to_timestamp(column).alias(column)
            if column in ORDER_DATETIME_COLUMNS
            else F.col(column)
            for column in ["order_purchase_timestamp", "order_status"]
        ],
    ).join(
        customers_df.select("customer_id", "customer_unique_id"),
        on="customer_id",
        how="left",
    ).join(
        order_items_agg,
        on="order_id",
        how="left",
    ).join(
        payments_agg,
        on="order_id",
        how="left",
    ).select(
        "order_id",
        "customer_unique_id",
        "order_purchase_timestamp",
        "order_status",
        F.coalesce(F.col("item_count"), F.lit(0)).cast("int").alias("item_count"),
        F.coalesce(F.col("product_value"), F.lit(0.0)).alias("product_value"),
        F.coalesce(F.col("freight_value"), F.lit(0.0)).alias("freight_value"),
        F.coalesce(F.col("payment_value"), F.lit(0.0)).alias("payment_value"),
    )

    monthly_sales = fact_orders.withColumn(
        "month",
        F.date_format("order_purchase_timestamp", "yyyy-MM"),
    ).groupBy("month").agg(
        F.count("order_id").alias("order_count"),
        F.sum("product_value").alias("product_revenue"),
        F.sum("freight_value").alias("freight_revenue"),
        F.sum("payment_value").alias("total_revenue"),
    ).withColumn(
        "average_order_value",
        F.col("total_revenue") / F.col("order_count"),
    ).select(
        "month",
        "order_count",
        "product_revenue",
        "freight_revenue",
        "total_revenue",
        "average_order_value",
    )

    customer_metrics = fact_orders.groupBy("customer_unique_id").agg(
        F.count("order_id").alias("total_orders"),
        F.sum("payment_value").alias("total_spend"),
        F.min("order_purchase_timestamp").alias("first_purchase_date"),
        F.max("order_purchase_timestamp").alias("last_purchase_date"),
    ).select(
        "customer_unique_id",
        "total_orders",
        "total_spend",
        "first_purchase_date",
        "last_purchase_date",
    )

    return {
        "dim_customers": dim_customers,
        "dim_products": dim_products,
        "fact_orders": fact_orders,
        "monthly_sales": monthly_sales,
        "customer_metrics": customer_metrics,
    }
