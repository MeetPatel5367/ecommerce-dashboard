import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="E-commerce Analytics Dashboard", layout="wide")

@st.cache_data
def load_data():
    products = pd.read_csv("data/products.csv")
    customers = pd.read_csv("data/customers.csv")
    monthly = pd.read_csv("data/monthly.csv")
    reviews = pd.read_csv("data/reviews.csv")
    return products, customers, monthly, reviews

products, customers, monthly, reviews = load_data()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Products", "Customers", "Reviews"]
)

st.sidebar.markdown("---")
st.sidebar.download_button(
    "Download products data",
    data=products.to_csv(index=False),
    file_name="products.csv",
    mime="text/csv"
)

if page == "Dashboard":
    st.title("E-commerce Analytics Dashboard")
    st.markdown("Interactive dashboard for analysing revenue, customers, product performance, and reviews.")

    total_revenue = products["total_revenue"].sum() if "total_revenue" in products.columns else 0
    total_orders = products["total_orders"].sum() if "total_orders" in products.columns else 0
    total_customers = customers["customer_unique_id"].nunique() if "customer_unique_id" in customers.columns else len(customers)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"{total_revenue:,.2f}")
    c2.metric("Total Orders", f"{int(total_orders):,}")
    c3.metric("Total Customers", f"{int(total_customers):,}")

    st.markdown("---")

    if "order_year" in monthly.columns:
        years = sorted(monthly["order_year"].dropna().unique())
        selected_year = st.selectbox("Select year", years)
        filtered_monthly = monthly[monthly["order_year"] == selected_year].copy()
    else:
        filtered_monthly = monthly.copy()

    if {"order_year", "order_month", "monthly_revenue"}.issubset(filtered_monthly.columns):
        filtered_monthly["year_month"] = (
            filtered_monthly["order_year"].astype(str)
            + "-"
            + filtered_monthly["order_month"].astype(str).str.zfill(2)
        )
        filtered_monthly = filtered_monthly.sort_values(["order_year", "order_month"])

    st.subheader("Monthly Revenue Trend")
    if {"year_month", "monthly_revenue"}.issubset(filtered_monthly.columns):
        st.line_chart(filtered_monthly.set_index("year_month")["monthly_revenue"])

    st.subheader("Top Product Categories")
    if {"product_category_name", "total_revenue"}.issubset(products.columns):
        top_products = (
            products.groupby("product_category_name", as_index=False)["total_revenue"]
            .sum()
            .sort_values("total_revenue", ascending=False)
            .head(10)
        )
        st.bar_chart(top_products.set_index("product_category_name")["total_revenue"])

        top_category = top_products.iloc[0]["product_category_name"]
        st.success(f"Top performing category: {top_category}")

    st.subheader("Low Performing Categories")
    if {"product_category_name", "total_revenue"}.issubset(products.columns):
        low_products = (
            products.groupby("product_category_name", as_index=False)["total_revenue"]
            .sum()
            .sort_values("total_revenue", ascending=True)
            .head(10)
        )

        fig1, ax1 = plt.subplots()
        ax1.pie(
            low_products["total_revenue"],
            labels=low_products["product_category_name"],
            autopct="%1.1f%%"
        )
        ax1.set_title("Low Performing Product Categories")
        st.pyplot(fig1)

elif page == "Products":
    st.title("Product Analysis")

    if "product_category_name" in products.columns:
        categories = sorted(products["product_category_name"].dropna().unique())
        selected_category = st.selectbox("Select category", categories)
        filtered_products = products[products["product_category_name"] == selected_category].copy()
    else:
        filtered_products = products.copy()

    st.subheader("Filtered Product Data")
    st.dataframe(filtered_products, use_container_width=True)

    if {"product_category_name", "total_revenue"}.issubset(filtered_products.columns):
        st.subheader("Revenue View")
        category_revenue = filtered_products.groupby("product_category_name")["total_revenue"].sum()
        st.bar_chart(category_revenue)

elif page == "Customers":
    st.title("Customer Analysis")

    if "total_spent" in customers.columns:
        top_customers = customers.sort_values("total_spent", ascending=False).head(10)
        display_col = "customer_city" if "customer_city" in top_customers.columns else top_customers.columns[0]

        st.subheader("Top Customers by Total Spending")
        st.bar_chart(top_customers.set_index(display_col)["total_spent"])

    st.subheader("Customer Data")
    st.dataframe(customers, use_container_width=True)

elif page == "Reviews":
    st.title("Review Analysis")

    if "avg_review_score" in reviews.columns:
        review_dist = reviews.copy()
        review_dist["review_score_group"] = review_dist["avg_review_score"].round()
        grouped_reviews = review_dist.groupby("review_score_group").size().sort_index()

        fig2, ax2 = plt.subplots()
        ax2.pie(grouped_reviews.values, labels=grouped_reviews.index, autopct="%1.1f%%")
        ax2.set_title("Distribution of Customer Review Scores")
        st.pyplot(fig2)

    st.subheader("Review Data")
    st.dataframe(reviews, use_container_width=True)
