import pytest

from src.transformation import transform_data
from src.spark_transform import spark_transform_data


@pytest.fixture(scope="module")
def pandas_data():
    return transform_data()


@pytest.fixture(scope="module")
def spark_data():
    data = spark_transform_data()
    yield data

    spark = next(iter(data.values())).sparkSession
    spark.stop()


def test_spark_and_pandas_row_counts_match(pandas_data, spark_data):
    for name, pandas_df in pandas_data.items():
        assert len(pandas_df) == spark_data[name].count()


def test_spark_fact_orders_has_unique_order_ids(spark_data):
    fact_orders = spark_data["fact_orders"]

    total_orders = fact_orders.count()
    unique_orders = fact_orders.select("order_id").distinct().count()

    assert total_orders == unique_orders


def test_spark_and_pandas_fact_order_totals_match(
    pandas_data,
    spark_data,
):
    pandas_totals = pandas_data["fact_orders"][
        ["product_value", "freight_value", "payment_value"]
    ].sum()

    spark_totals_row = spark_data["fact_orders"].selectExpr(
        "sum(product_value) AS product_value",
        "sum(freight_value) AS freight_value",
        "sum(payment_value) AS payment_value",
    ).first()

    for column in pandas_totals.index:
        assert float(spark_totals_row[column]) == pytest.approx(
            float(pandas_totals[column]),
            abs=0.01,
        )