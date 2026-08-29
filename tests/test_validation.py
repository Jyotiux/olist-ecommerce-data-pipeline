import pandas as pd
import pytest

from src import validation


def get_valid_data():
    return {
        "customers": pd.DataFrame({
            "customer_id": ["customer_1"],
        }),
        "orders": pd.DataFrame({
            "order_id": ["order_1"],
            "customer_id": ["customer_1"],
        }),
        "order_items": pd.DataFrame({
            "order_id": ["order_1"],
            "product_id": ["product_1"],
            "price": [100.0],
            "freight_value": [10.0],
        }),
        "payments": pd.DataFrame({
            "order_id": ["order_1"],
            "payment_value": [110.0],
            "payment_installments": [1],
        }),
        "products": pd.DataFrame({
            "product_id": ["product_1"],
        }),
    }


def test_validate_data_passes_for_valid_data(monkeypatch):
    data = get_valid_data()

    monkeypatch.setattr(validation, "clean_data", lambda _: data)

    result = validation.validate_data()

    assert result is data


def test_validate_data_rejects_null_customer_id(monkeypatch):
    data = get_valid_data()
    data["customers"].loc[0, "customer_id"] = None

    monkeypatch.setattr(validation, "clean_data", lambda _: data)

    with pytest.raises(
        ValueError,
        match="customers.customer_id must not be null",
    ):
        validation.validate_data()


def test_validate_data_rejects_duplicate_customer_id(monkeypatch):
    data = get_valid_data()

    data["customers"] = pd.DataFrame({
        "customer_id": ["customer_1", "customer_1"],
    })

    monkeypatch.setattr(validation, "clean_data", lambda _: data)

    with pytest.raises(
        ValueError,
        match="customers.customer_id must be unique",
    ):
        validation.validate_data()


def test_validate_data_rejects_missing_customer_reference(monkeypatch):
    data = get_valid_data()
    data["orders"].loc[0, "customer_id"] = "missing_customer"

    monkeypatch.setattr(validation, "clean_data", lambda _: data)

    with pytest.raises(
        ValueError,
        match="orders.customer_id must exist in customers.customer_id",
    ):
        validation.validate_data()


def test_validate_data_rejects_negative_price(monkeypatch):
    data = get_valid_data()
    data["order_items"].loc[0, "price"] = -100.0

    monkeypatch.setattr(validation, "clean_data", lambda _: data)

    with pytest.raises(
        ValueError,
        match="order_items.price must not be negative",
    ):
        validation.validate_data()


def test_validate_data_rejects_negative_payment_installments(monkeypatch):
    data = get_valid_data()
    data["payments"].loc[0, "payment_installments"] = -1

    monkeypatch.setattr(validation, "clean_data", lambda _: data)

    with pytest.raises(
        ValueError,
        match="payments.payment_installments must not be negative",
    ):
        validation.validate_data()