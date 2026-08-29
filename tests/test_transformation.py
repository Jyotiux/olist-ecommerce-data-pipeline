from src.transformation import transform_data


def test_transform_returns_expected_tables():
    data = transform_data()

    expected_tables = {
        "dim_customers",
        "dim_products",
        "fact_orders",
        "monthly_sales",
        "customer_metrics",
    }

    assert set(data.keys()) == expected_tables


def test_fact_orders_has_unique_order_ids():
    data = transform_data()

    fact_orders = data["fact_orders"]

    assert fact_orders["order_id"].is_unique


def test_transformed_data_has_expected_columns():
    data = transform_data()

    assert list(data["dim_customers"].columns) == [
        "customer_unique_id",
        "customer_city",
        "customer_state",
    ]

    assert list(data["dim_products"].columns) == [
        "product_id",
        "product_category_name_english",
    ]

    assert list(data["fact_orders"].columns) == [
        "order_id",
        "customer_unique_id",
        "order_purchase_timestamp",
        "order_status",
        "item_count",
        "product_value",
        "freight_value",
        "payment_value",
    ]


def test_customer_metrics_has_unique_customers():
    data = transform_data()

    customer_metrics = data["customer_metrics"]

    assert customer_metrics["customer_unique_id"].is_unique