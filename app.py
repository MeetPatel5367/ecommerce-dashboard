import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="E-commerce Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
:root {
    --bg: #0f172a;
    --card: #111827;
    --soft: #1f2937;
    --line: #334155;
    --text: #e5e7eb;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --accent2: #22c55e;
    --accent3: #f59e0b;
}
.stApp {
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
    color: var(--text);
}
section[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}
h1, h2, h3 {
    color: #f8fafc !important;
}
.dashboard-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 0.2rem;
}
.dashboard-subtitle {
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 1.2rem;
}
.kpi-card {
    background: rgba(17, 24, 39, 0.9);
    border: 1px solid #263244;
    border-radius: 18px;
    padding: 18px 18px 14px 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}
.kpi-label {
    color: #94a3b8;
    font-size: 0.92rem;
    margin-bottom: 6px;
}
.kpi-value {
    color: #f8fafc;
    font-size: 1.9rem;
    font-weight: 800;
}
.section-card {
    background: rgba(17, 24, 39, 0.88);
    border: 1px solid #263244;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.16);
    margin-bottom: 16px;
}
.insight-card {
    background: rgba(14, 165, 233, 0.10);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-left: 4px solid #38bdf8;
    border-radius: 14px;
    padding: 12px 14px;
    margin-top: 10px;
    color: #dbeafe;
}
div[data-testid="stMetric"] {
    background: rgba(17, 24, 39, 0.88);
    border: 1px solid #263244;
    padding: 10px;
    border-radius: 16px;
}
[data-baseweb="tab-list"] {
    gap: 8px;
}
[data-baseweb="tab"] {
    background: #0f172a !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 16px !important;
}
hr {
    border-color: #223046;
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
# PREP
# -----------------------------
products["product_category_name"] = products["product_category_name"].fillna("unknown")
customers["customer_city"] = customers["customer_city"].fillna("unknown")
customers["customer_state"] = customers["customer_state"].fillna("unknown")

if {"order_year", "order_month", "monthly_revenue"}.issubset(monthly.columns):
    monthly["year_month"] = (
        monthly["order_year"].astype(str) + "-" +
        monthly["order_month"].astype(str).str.zfill(2)
    )
    monthly = monthly.sort_values(["order_year", "order_month"])

if "avg_review_score" in reviews.columns:
    reviews["review_score_group"] = reviews["avg_review_score"].round().clip(lower=1, upper=5)

category_revenue = (
    products.groupby("product_category_name", as_index=False)["total_revenue"]
    .sum()
    .sort_values("total_revenue", ascending=False)
)

low_category_revenue = (
    products.groupby("product_category_name", as_index=False)["total_revenue"]
    .sum()
    .sort_values("total_revenue", ascending=True)
    .head(10)
)

top_customers = customers.sort_values("total_spent", ascending=False).head(10)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("## ⚙ Dashboard Controls")

years = ["All"] + sorted(monthly["order_year"].dropna().astype(int).unique().tolist()) if "order_year" in monthly.columns else ["All"]
selected_year = st.sidebar.selectbox("Select year", years)

categories = ["All"] + sorted(products["product_category_name"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select category", categories)

show_tables = st.sidebar.toggle("Show detailed tables", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### Downloads")
st.sidebar.download_button(
    "Download products data",
    products.to_csv(index=False),
    file_name="products.csv",
    mime="text/csv"
)
st.sidebar.download_button(
    "Download customers data",
    customers.to_csv(index=False),
    file_name="customers.csv",
    mime="text/csv"
)
st.sidebar.download_button(
    "Download monthly revenue data",
    monthly.to_csv(index=False),
    file_name="monthly.csv",
    mime="text/csv"
)
st.sidebar.download_button(
    "Download reviews data",
    reviews.to_csv(index=False),
    file_name="reviews.csv",
    mime="text/csv"
)

# -----------------------------
# FILTERS
# -----------------------------
filtered_monthly = monthly.copy()
if selected_year != "All" and "order_year" in filtered_monthly.columns:
    filtered_monthly = filtered_monthly[filtered_monthly["order_year"] == int(selected_year)]

filtered_products = products.copy()
if selected_category != "All":
    filtered_products = filtered_products[filtered_products["product_category_name"] == selected_category]

filtered_category_revenue = (
    filtered_products.groupby("product_category_name", as_index=False)["total_revenue"]
    .sum()
    .sort_values("total_revenue", ascending=False)
)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="dashboard-title">E-commerce Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">A professional decision-support dashboard built from the Gold layer of the Lakehouse pipeline. It presents revenue, customer, product, and review insights in a clean executive format.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# KPIs
# -----------------------------
total_revenue = products["total_revenue"].sum() if "total_revenue" in products.columns else 0
total_orders = int(products["total_orders"].sum()) if "total_orders" in products.columns else 0
total_customers = int(customers["customer_unique_id"].nunique()) if "customer_unique_id" in customers.columns else len(customers)
avg_review = reviews["avg_review_score"].mean() if "avg_review_score" in reviews.columns else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Revenue</div><div class="kpi-value">{total_revenue:,.2f}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Orders</div><div class="kpi-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Customers</div><div class="kpi-value">{total_customers:,}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Average Review Score</div><div class="kpi-value">{avg_review:.2f}</div></div>', unsafe_allow_html=True)

st.markdown("")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Products", "Customers", "Reviews"])

# -----------------------------
# OVERVIEW
# -----------------------------
with tab1:
    left, right = st.columns((1.25, 1))

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Monthly Revenue Trend")
        if not filtered_monthly.empty and {"year_month", "monthly_revenue"}.issubset(filtered_monthly.columns):
            fig_line = px.line(
                filtered_monthly,
                x="year_month",
                y="monthly_revenue",
                markers=True,
                template="plotly_dark"
            )
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Month",
                yaxis_title="Revenue",
                height=360
            )
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown(
                '<div class="insight-card"><b>Insight:</b> The monthly revenue pattern shows how sales evolve over time and helps identify growth periods, seasonal shifts, and anomalies.</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top Product Categories")
        top10 = filtered_category_revenue.head(10)
        if not top10.empty:
            fig_bar = px.bar(
                top10,
                x="total_revenue",
                y="product_category_name",
                orientation="h",
                template="plotly_dark",
                text_auto=".2s"
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Revenue",
                yaxis_title="Category",
                height=360,
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            top_cat = top10.iloc[0]["product_category_name"]
            st.markdown(
                f'<div class="insight-card"><b>Insight:</b> The strongest category is <b>{top_cat}</b>, indicating demand concentration in a limited number of product areas.</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns((1, 1))
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Low Performing Categories")
        fig_donut = px.pie(
            low_category_revenue,
            names="product_category_name",
            values="total_revenue",
            hole=0.58,
            template="plotly_dark"
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent")
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=360,
            showlegend=True,
            legend=dict(orientation="v")
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown(
            '<div class="insight-card"><b>Insight:</b> These categories contribute the least revenue and may require review, repositioning, or removal to improve portfolio efficiency.</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Revenue Share Snapshot")
        if not category_revenue.empty:
            share_top5 = category_revenue.head(5).copy()
            fig_share = px.treemap(
                share_top5,
                path=["product_category_name"],
                values="total_revenue",
                template="plotly_dark"
            )
            fig_share.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=360
            )
            st.plotly_chart(fig_share, use_container_width=True)
            st.markdown(
                '<div class="insight-card"><b>Insight:</b> The leading categories account for a disproportionately large share of total revenue, reinforcing the need for focused category management.</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# PRODUCTS
# -----------------------------
with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Product Performance Explorer")

    product_view = filtered_products.sort_values("total_revenue", ascending=False).head(20)

    if not product_view.empty:
        fig_prod = px.bar(
            product_view.head(10),
            x="total_revenue",
            y="product_category_name",
            orientation="h",
            color="total_orders" if "total_orders" in product_view.columns else None,
            template="plotly_dark",
            text_auto=".2s"
        )
        fig_prod.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Revenue",
            yaxis_title="Category",
            height=420,
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_prod, use_container_width=True)

        st.markdown(
            '<div class="insight-card"><b>Insight:</b> Product analysis reveals where revenue is strongest and helps identify categories with the highest strategic value.</div>',
            unsafe_allow_html=True
        )

        if show_tables:
            st.dataframe(product_view, use_container_width=True, height=320)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CUSTOMERS
# -----------------------------
with tab3:
    left, right = st.columns((1, 1))

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top Customers by Spending")
        customer_col = "customer_city" if "customer_city" in top_customers.columns else top_customers.columns[0]

        fig_customers = px.bar(
            top_customers,
            x="total_spent",
            y=customer_col,
            orientation="h",
            template="plotly_dark",
            text_auto=".2s"
        )
        fig_customers.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Total Spent",
            yaxis_title="Customer Segment",
            height=420,
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_customers, use_container_width=True)
        st.markdown(
            '<div class="insight-card"><b>Insight:</b> A relatively small customer segment contributes a large share of spending, supporting targeted retention and loyalty strategies.</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Customer Distribution by State")
        if "customer_state" in customers.columns and "total_spent" in customers.columns:
            state_spend = customers.groupby("customer_state", as_index=False)["total_spent"].sum().sort_values("total_spent", ascending=False).head(10)
            fig_state = px.bar(
                state_spend,
                x="customer_state",
                y="total_spent",
                template="plotly_dark",
                text_auto=".2s"
            )
            fig_state.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="State",
                yaxis_title="Total Spent",
                height=420
            )
            st.plotly_chart(fig_state, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if show_tables:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Customer Table")
        st.dataframe(top_customers, use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# REVIEWS
# -----------------------------
with tab4:
    left, right = st.columns((1, 1))

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Review Score Distribution")
        grouped_reviews = reviews.groupby("review_score_group", as_index=False).size()
        grouped_reviews.columns = ["review_score_group", "count"]

        fig_reviews = px.pie(
            grouped_reviews,
            names="review_score_group",
            values="count",
            hole=0.58,
            template="plotly_dark"
        )
        fig_reviews.update_traces(textposition="inside", textinfo="percent+label")
        fig_reviews.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=400
        )
        st.plotly_chart(fig_reviews, use_container_width=True)
        st.markdown(
            '<div class="insight-card"><b>Insight:</b> Review scores cluster mainly around 4 and 5, indicating generally positive customer satisfaction.</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Average Review by Category")
        if {"product_category_name", "avg_review_score"}.issubset(reviews.columns):
            review_cat = (
                reviews.groupby("product_category_name", as_index=False)["avg_review_score"]
                .mean()
                .sort_values("avg_review_score", ascending=False)
                .head(10)
            )
            fig_review_cat = px.bar(
                review_cat,
                x="avg_review_score",
                y="product_category_name",
                orientation="h",
                template="plotly_dark",
                text_auto=".2f"
            )
            fig_review_cat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Average Review Score",
                yaxis_title="Category",
                height=400,
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig_review_cat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if show_tables:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Review Table")
        st.dataframe(reviews.head(20), use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
