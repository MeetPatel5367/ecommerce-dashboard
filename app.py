import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="E-commerce Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# CUSTOM STYLING
# -----------------------------
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #1f2937;
}
.kpi-card {
    background-color: #f8fafc;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.insight-box {
    background-color: #f0f9ff;
    border-left: 5px solid #0ea5e9;
    padding: 14px 16px;
    border-radius: 10px;
    color: #0f172a;
    margin-top: 8px;
    margin-bottom: 16px;
}
.section-box {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 18px;
}
.small-text {
    color: #6b7280;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    products = pd.read_csv("data/products.csv")
    customers = pd.read_csv("data/customers.csv")
    monthly = pd.read_csv("data/monthly.csv")
    reviews = pd.read_csv("data/reviews.csv")
    return products, customers, monthly, reviews

products, customers, monthly, reviews = load_data()

# -----------------------------
# DATA PREP
# -----------------------------
if {"product_category_name", "total_revenue"}.issubset(products.columns):
    category_revenue = (
        products.groupby("product_category_name", as_index=False)["total_revenue"]
        .sum()
        .sort_values("total_revenue", ascending=False)
    )
else:
    category_revenue = pd.DataFrame()

if {"order_year", "order_month", "monthly_revenue"}.issubset(monthly.columns):
    monthly = monthly.copy()
    monthly["year_month"] = (
        monthly["order_year"].astype(str)
        + "-"
        + monthly["order_month"].astype(str).str.zfill(2)
    )
    monthly = monthly.sort_values(["order_year", "order_month"])

if "avg_review_score" in reviews.columns:
    reviews = reviews.copy()
    reviews["review_score_group"] = reviews["avg_review_score"].round()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("📌 Dashboard Controls")
st.sidebar.markdown("Use the filters below to explore the dashboard.")

available_years = sorted(monthly["order_year"].dropna().unique()) if "order_year" in monthly.columns else []
selected_year = st.sidebar.selectbox(
    "Select Year",
    available_years if available_years else ["All"]
)

available_categories = sorted(products["product_category_name"].dropna().unique()) if "product_category_name" in products.columns else []
selected_category = st.sidebar.selectbox(
    "Select Product Category",
    ["All"] + available_categories if available_categories else ["All"]
)

show_raw_tables = st.sidebar.checkbox("Show detailed tables", value=True)

st.sidebar.markdown("---")
st.sidebar.download_button(
    "⬇ Download Products CSV",
    data=products.to_csv(index=False),
    file_name="products.csv",
    mime="text/csv"
)

st.sidebar.download_button(
    "⬇ Download Customers CSV",
    data=customers.to_csv(index=False),
    file_name="customers.csv",
    mime="text/csv"
)

# -----------------------------
# FILTERED DATA
# -----------------------------
filtered_monthly = monthly.copy()
if selected_year != "All" and "order_year" in filtered_monthly.columns:
    filtered_monthly = filtered_monthly[filtered_monthly["order_year"] == selected_year]

filtered_products = products.copy()
if selected_category != "All" and "product_category_name" in filtered_products.columns:
    filtered_products = filtered_products[filtered_products["product_category_name"] == selected_category]

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 E-commerce Intelligence Dashboard")
st.markdown(
    "<div class='small-text'>Professional analytics dashboard built from the Gold layer of the Lakehouse pipeline. "
    "It presents business-ready insights on revenue, product performance, customers, and review behaviour.</div>",
    unsafe_allow_html=True
)

st.markdown("")

# -----------------------------
# KPI SECTION
# -----------------------------
total_revenue = float(products["total_revenue"].sum()) if "total_revenue" in products.columns else 0
total_orders = int(products["total_orders"].sum()) if "total_orders" in products.columns else 0
total_customers = int(customers["customer_unique_id"].nunique()) if "customer_unique_id" in customers.columns else len(customers)
avg_review = float(reviews["avg_review_score"].mean()) if "avg_review_score" in reviews.columns else 0

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>Total Revenue</h3>
        <h2>{total_revenue:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>Total Orders</h3>
        <h2>{total_orders:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>Total Customers</h3>
        <h2>{total_customers:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>Average Review Score</h3>
        <h2>{avg_review:.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview", "Products", "Customers", "Reviews"
])

# -----------------------------
# OVERVIEW TAB
# -----------------------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Monthly Revenue Trend")
        if not filtered_monthly.empty and {"year_month", "monthly_revenue"}.issubset(filtered_monthly.columns):
            st.line_chart(filtered_monthly.set_index("year_month")["monthly_revenue"])
            st.markdown("""
            <div class='insight-box'>
            <b>Insight:</b> The monthly revenue trend highlights how sales change over time and helps identify seasonal patterns, growth periods, and possible anomalies in business performance.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Monthly revenue data is not available.")

    with c2:
        st.subheader("Top Product Categories")
        if not category_revenue.empty:
            top_categories = category_revenue.head(10).set_index("product_category_name")
            st.bar_chart(top_categories["total_revenue"])
            top_cat = category_revenue.iloc[0]["product_category_name"]
            st.markdown(f"""
            <div class='insight-box'>
            <b>Insight:</b> The highest revenue-generating category is <b>{top_cat}</b>. This suggests demand is concentrated in a small number of strong-performing categories.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Product category revenue data is not available.")

    st.subheader("Low Performing Categories")
    if not category_revenue.empty:
        low_categories = category_revenue.sort_values("total_revenue", ascending=True).head(10)

        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(
            low_categories["total_revenue"],
            labels=low_categories["product_category_name"],
            autopct="%1.1f%%",
            startangle=90
        )
        ax1.set_title("Low Performing Product Categories")
        st.pyplot(fig1)

        st.markdown("""
        <div class='insight-box'>
        <b>Insight:</b> Low-performing categories contribute only a small share of total revenue. These may require strategic review, repositioning, or removal to improve overall profitability.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# PRODUCTS TAB
# -----------------------------
with tab2:
    st.subheader("Product Revenue Analysis")

    if not filtered_products.empty:
        display_products = filtered_products.sort_values("total_revenue", ascending=False).head(20)
        if {"product_category_name", "total_revenue"}.issubset(display_products.columns):
            product_chart = (
                display_products.groupby("product_category_name", as_index=False)["total_revenue"]
                .sum()
                .sort_values("total_revenue", ascending=False)
                .head(10)
                .set_index("product_category_name")
            )
            st.bar_chart(product_chart["total_revenue"])

        st.markdown("""
        <div class='insight-box'>
        <b>Insight:</b> Product-level analysis helps identify which categories are driving business value and which areas may need optimisation.
        </div>
        """, unsafe_allow_html=True)

        if show_raw_tables:
            st.subheader("Product Table")
            st.dataframe(display_products, use_container_width=True)
    else:
        st.info("No product data available for the selected filter.")

# -----------------------------
# CUSTOMERS TAB
# -----------------------------
with tab3:
    st.subheader("Top Customers by Total Spending")

    if not customers.empty and "total_spent" in customers.columns:
        top_customers = customers.sort_values("total_spent", ascending=False).head(10)

        if "customer_city" in top_customers.columns:
            customer_chart = top_customers.groupby("customer_city")["total_spent"].sum().sort_values(ascending=False)
            st.bar_chart(customer_chart)
        else:
            st.bar_chart(top_customers.set_index(top_customers.columns[0])["total_spent"])

        st.markdown("""
        <div class='insight-box'>
        <b>Insight:</b> A small segment of customers contributes disproportionately to revenue. This supports the case for loyalty programmes and targeted retention strategies.
        </div>
        """, unsafe_allow_html=True)

        if show_raw_tables:
            st.subheader("Customer Table")
            st.dataframe(top_customers, use_container_width=True)
    else:
        st.info("Customer spending data is not available.")

# -----------------------------
# REVIEWS TAB
# -----------------------------
with tab4:
    st.subheader("Review Score Distribution")

    if not reviews.empty and "review_score_group" in reviews.columns:
        grouped_reviews = reviews.groupby("review_score_group").size().sort_index()

        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.pie(
            grouped_reviews.values,
            labels=grouped_reviews.index,
            autopct="%1.1f%%",
            startangle=90
        )
        ax2.set_title("Distribution of Customer Review Scores")
        st.pyplot(fig2)

        st.markdown("""
        <div class='insight-box'>
        <b>Insight:</b> Review score distribution indicates overall customer satisfaction. A concentration of scores around 4 and 5 suggests generally positive customer experience.
        </div>
        """, unsafe_allow_html=True)

        if show_raw_tables:
            st.subheader("Review Table")
            st.dataframe(reviews.head(20), use_container_width=True)
    else:
        st.info("Review data is not available.")
