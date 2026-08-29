import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


load_dotenv()

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource
def get_engine():
    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        database=os.environ["DB_NAME"],
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
    return create_engine(connection_url)


@st.cache_data
def load_dashboard_data():
    engine = get_engine()

    queries = {
        "monthly_sales": """
            SELECT
                month,
                order_count,
                product_revenue,
                freight_revenue,
                total_revenue,
                average_order_value
            FROM monthly_sales
            ORDER BY month
        """,

        "top_customers": """
            SELECT
                customer_unique_id,
                total_orders,
                total_spend
            FROM customer_metrics
            ORDER BY total_spend DESC
            LIMIT 10
        """,

        "state_revenue": """
            SELECT
                dc.customer_state,
                SUM(fo.payment_value) AS total_revenue
            FROM fact_orders AS fo
            JOIN dim_customers AS dc
                ON fo.customer_unique_id = dc.customer_unique_id
            GROUP BY dc.customer_state
            ORDER BY total_revenue DESC
            LIMIT 10
        """,

        "order_status": """
            SELECT
                order_status,
                COUNT(*) AS order_count
            FROM fact_orders
            GROUP BY order_status
            ORDER BY order_count DESC
        """,

        "kpis": """
            SELECT
                COUNT(*) AS total_orders,
                SUM(payment_value) AS total_revenue,
                AVG(payment_value) AS average_order_value
            FROM fact_orders
        """,

        "customers": """
            SELECT COUNT(*) AS total_customers
            FROM dim_customers
        """,
    }

    return {
        name: pd.read_sql(text(query), engine)
        for name, query in queries.items()
    }


def main():
    st.title("E-Commerce Analytics")
    st.caption(
        "Olist marketplace performance overview | "
        "PostgreSQL · Pandas · PySpark"
    )

    data = load_dashboard_data()

    kpis = data["kpis"].iloc[0]
    total_customers = data["customers"].iloc[0]["total_customers"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        f"R$ {kpis['total_revenue']:,.2f}",
    )

    col2.metric(
        "Total Orders",
        f"{int(kpis['total_orders']):,}",
    )

    col3.metric(
        "Total Customers",
        f"{int(total_customers):,}",
    )

    col4.metric(
        "Average Order Value",
        f"R$ {kpis['average_order_value']:,.2f}",
    )

    st.divider()

    st.subheader("Revenue Trend")

    monthly_sales = data["monthly_sales"].copy()
    monthly_sales["month"] = pd.to_datetime(monthly_sales["month"])
    monthly_sales = monthly_sales.sort_values("month")

    st.line_chart(
        monthly_sales,
        x="month",
        y="total_revenue",
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Top States by Revenue")

        state_revenue = data["state_revenue"].copy()

        st.bar_chart(
            state_revenue,
            x="customer_state",
            y="total_revenue",
            use_container_width=True,
        )

    with right:
        st.subheader("Order Status")

        order_status = data["order_status"].copy()

        st.bar_chart(
            order_status,
            x="order_status",
            y="order_count",
            use_container_width=True,
        )

    st.divider()

    st.subheader("Top Customers")

    top_customers = data["top_customers"].copy()

    top_customers = top_customers.rename(
        columns={
            "customer_unique_id": "Customer ID",
            "total_orders": "Orders",
            "total_spend": "Total Spend (R$)",
        }
    )

    top_customers["Total Spend (R$)"] = top_customers[
        "Total Spend (R$)"
    ].map(lambda value: f"R$ {value:,.2f}")

    st.dataframe(
        top_customers,
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()