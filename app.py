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
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
:root {
    --bg-dark: #081120;
    --bg-mid: #0f172a;
    --card: rgba(15, 23, 42, 0.88);
    --card-border: #22304a;
    --text-main: #f8fafc;
    --text-soft: #cbd5e1;
    --text-muted: #94a3b8;
    --accent: #38bdf8;
    --accent-2: #6366f1;
    --accent-3: #22c55e;
    --warning: #f59e0b;
}

.stApp {
    background: radial-gradient(circle at top left, #0b1d3a 0%, #081120 45%, #050b16 100%);
    color: var(--text-main);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07101e 0%, #0b1628 100%);
    border-right: 1px solid #1f2b40;
}

section[data-testid="stSidebar"] * {
    /*color: #f8fafc !important;*/
}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] div {
    /*color: #f8fafc !important;*/
}

section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background: #f8fafc !important;
    /*color: #0f172a !important;*/
    border-radius: 10px !important;
    border: 1px solid #cbd5e1 !important;
}

section[data-testid="stSidebar"] .stSelectbox svg {
    fill: #0f172a !important;
}

section[data-testid="stSidebar"] .stDownloadButton button {
    background: #f8fafc !important;
    color: #0f172a !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] .stCheckbox label {
   /* color: #f8fafc !important;*/
    font-weight: 500 !important;
}

h1, h2, h3 {
    color: #f8fafc !important;
}

.dashboard-title {
    font-size: 2.35rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.2rem;
    letter-spacing: 0.2px;
}

.dashboard-subtitle {
    color: #cbd5e1;
    font-size: 1rem;
    margin-bottom: 1rem;
    max-width: 1100px;
}

.kpi-card {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid #22304a;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    min-height: 120px;
}

.kpi-label {
    color: #94a3b8;
    font-size: 0.92rem;
    margin-bottom: 10px;
}

.kpi-value {
    color: #ffffff;
    font-size: 1.95rem;
    font-weight: 800;
    line-height: 1.1;
}

.section-card {
    background: rgba(15, 23, 42, 0.90);
    border: 1px solid #22304a;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    margin-bottom: 16px;
}

.insight-card {
    background: rgba(56, 189, 248, 0.10);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-left: 4px solid #38bdf8;
    border-radius: 14px;
    padding: 12px 14px;
    margin-top: 10px;
    color: #dbeafe;
    font-size: 0.96rem;
}

.summary-card {
    background: rgba(99, 102, 241, 0.10);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-left: 4px solid #6366f1;
    border-radius: 14px;
    padding: 14px 16px;
    color: #e0e7ff;
    margin-bottom: 18px;
}

.small-note {
    color: #94a3b8;
    font-size: 0.92rem;
}

[data-baseweb="tab-list"] {
    gap: 10px;
}

[data-baseweb="tab"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 1px solid #22304a !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 10px 16px !important;
}

[data-baseweb="tab"][aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}

hr {
    border-color: #24334b;
}
/* HIDE STREAMLIT HEADER */
header[data-testid="stHeader"] {
    display: none;
}

div[data-testid="stToolbar"] {
    display: none;
}

div[data-testid="stDecoration"] {
    display: none;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
.block-container {
    padding-top: 0.5rem !important;
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
# PREP DATA
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

top_customers_all = customers.sort_values("total_spent", ascending=False)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("## ⚙ Dashboard Controls")
st.sidebar.markdown("Use these filters to explore the analytical results.")

year_options = ["All"] + sorted(monthly["order_year"].dropna().astype(int).unique().tolist()) if "order_year" in monthly.columns else ["All"]
selected_year = st.sidebar.selectbox("Select year", year_options)

category_options = ["All"] + sorted(products["product_category_name"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select product category", category_options)

state_options = ["All"] + sorted(customers["customer_state"].dropna().unique().tolist()) if "customer_state" in customers.columns else ["All"]
selected_state = st.sidebar.selectbox("Select customer state", state_options)

top_n = st.sidebar.slider("Select number of categories/customers", 5, 20, 10)

show_tables = st.sidebar.checkbox("Show detailed tables", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⬇ Downloads")
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
# FILTER DATA
# -----------------------------
filtered_monthly = monthly.copy()
if selected_year != "All" and "order_year" in filtered_monthly.columns:
    filtered_monthly = filtered_monthly[filtered_monthly["order_year"] == int(selected_year)]

filtered_products = products.copy()
if selected_category != "All":
    filtered_products = filtered_products[filtered_products["product_category_name"] == selected_category]

filtered_customers = customers.copy()
if selected_state != "All" and "customer_state" in filtered_customers.columns:
    filtered_customers = filtered_customers[filtered_customers["customer_state"] == selected_state]

filtered_category_revenue = (
    filtered_products.groupby("product_category_name", as_index=False)["total_revenue"]
    .sum()
    .sort_values("total_revenue", ascending=False)
)

low_category_revenue = (
    filtered_products.groupby("product_category_name", as_index=False)["total_revenue"]
    .sum()
    .sort_values("total_revenue", ascending=True)
    .head(top_n)
)

top_products = filtered_category_revenue.head(top_n)
top_customers = filtered_customers.sort_values("total_spent", ascending=False).head(top_n)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="dashboard-title">E-commerce Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">An advanced executive dashboard developed from the Gold layer of the Lakehouse pipeline. It supports professional analysis of revenue trends, customer behaviour, product performance, and review outcomes through interactive filters and modern visual design.</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="summary-card">
<b>Executive Summary:</b> This dashboard translates the final Gold-layer outputs into a professional business intelligence interface. It allows stakeholders to explore which categories generate the most revenue, which customer segments spend the most, how revenue changes over time, and how customer satisfaction varies across product groups.
</div>
""", unsafe_allow_html=True)

# -----------------------------
# KPI CARDS
# -----------------------------
total_revenue = filtered_products["total_revenue"].sum() if "total_revenue" in filtered_products.columns else 0
total_orders = int(filtered_products["total_orders"].sum()) if "total_orders" in filtered_products.columns else 0
total_customers = int(filtered_customers["customer_unique_id"].nunique()) if "customer_unique_id" in filtered_customers.columns else len(filtered_customers)
avg_review = reviews["avg_review_score"].mean() if "avg_review_score" in reviews.columns else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Filtered Revenue</div><div class="kpi-value">{total_revenue:,.2f}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Filtered Orders</div><div class="kpi-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Filtered Customers</div><div class="kpi-value">{total_customers:,}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Average Review Score</div><div class="kpi-value">{avg_review:.2f}</div></div>', unsafe_allow_html=True)

st.markdown("")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Products", "Customers", "Reviews", "Research Notes"]
)

# -----------------------------
# OVERVIEW TAB
# -----------------------------
with tab1:
    left, right = st.columns((1.25, 1))

    with left:
        with placeholder.container():

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
                    yaxis_title="Monthly Revenue",
                    height=360
                )
                st.plotly_chart(fig_line, use_container_width=True)
                st.markdown(
                    '<div class="insight-card"><b>Insight:</b> The revenue trend helps identify seasonal demand patterns and periods of strong or weak commercial performance.</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top Categories by Revenue")
        if not top_products.empty:
            fig_bar = px.bar(
                top_products,
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
            top_cat = top_products.iloc[0]["product_category_name"]
            st.markdown(
                f'<div class="insight-card"><b>Insight:</b> The strongest category in the current filtered view is <b>{top_cat}</b>, indicating concentration of demand in a limited set of product areas.</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Low Performing Categories")
        if not low_category_revenue.empty:
            fig_donut = px.pie(
                low_category_revenue,
                names="product_category_name",
                values="total_revenue",
                hole=0.62,
                template="plotly_dark"
            )
            fig_donut.update_traces(textposition="inside", textinfo="percent")
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=360,
                legend=dict(orientation="v")
            )
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown(
                '<div class="insight-card"><b>Insight:</b> Low-performing categories contribute little to revenue and may be candidates for repositioning, targeted promotion, or discontinuation.</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top Customer Spending")
        if not top_customers.empty and "total_spent" in top_customers.columns:
            customer_label = "customer_city" if "customer_city" in top_customers.columns else top_customers.columns[0]
            fig_cust = px.bar(
                top_customers,
                x="total_spent",
                y=customer_label,
                orientation="h",
                template="plotly_dark",
                text_auto=".2s"
            )
            fig_cust.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Total Spent",
                yaxis_title="Customer Segment",
                height=360,
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig_cust, use_container_width=True)
            st.markdown(
                '<div class="insight-card"><b>Insight:</b> High-value customer groups account for a disproportionate share of spending, supporting focused retention strategies.</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# PRODUCTS TAB
# -----------------------------
with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Product Category Explorer")

    if not filtered_products.empty:
        prod_view = (
            filtered_products.groupby("product_category_name", as_index=False)[["total_revenue", "total_orders"]]
            .sum()
            .sort_values("total_revenue", ascending=False)
            .head(top_n)
        )

        fig_prod = px.scatter(
            prod_view,
            x="total_orders",
            y="total_revenue",
            size="total_revenue",
            color="product_category_name",
            template="plotly_dark",
            hover_name="product_category_name"
        )
        fig_prod.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Total Orders",
            yaxis_title="Total Revenue",
            height=450,
            showlegend=False
        )
        st.plotly_chart(fig_prod, use_container_width=True)

        st.markdown(
            '<div class="insight-card"><b>Insight:</b> This view shows how order volume and revenue interact across categories. Categories in the upper-right region are the most strategically valuable.</div>',
            unsafe_allow_html=True
        )

        if show_tables:
            st.dataframe(prod_view, use_container_width=True, height=320)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CUSTOMERS TAB
# -----------------------------
with tab3:
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top Spending Customers")
        if not top_customers.empty:
            fig_top_cust = px.bar(
                top_customers,
                x="total_spent",
                y="customer_city" if "customer_city" in top_customers.columns else top_customers.columns[0],
                orientation="h",
                template="plotly_dark",
                text_auto=".2s"
            )
            fig_top_cust.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Total Spending",
                yaxis_title="Customer Group",
                height=420,
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig_top_cust, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Customer Spending by State")
        if {"customer_state", "total_spent"}.issubset(filtered_customers.columns):
            state_spend = (
                filtered_customers.groupby("customer_state", as_index=False)["total_spent"]
                .sum()
                .sort_values("total_spent", ascending=False)
                .head(top_n)
            )
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
                yaxis_title="Total Spending",
                height=420
            )
            st.plotly_chart(fig_state, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# REVIEWS TAB
# -----------------------------
with tab4:
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Review Score Distribution")
        if "review_score_group" in reviews.columns:
            grouped_reviews = reviews.groupby("review_score_group", as_index=False).size()
            grouped_reviews.columns = ["review_score_group", "count"]

            fig_reviews = px.pie(
                grouped_reviews,
                names="review_score_group",
                values="count",
                hole=0.62,
                template="plotly_dark"
            )
            fig_reviews.update_traces(textposition="inside", textinfo="percent+label")
            fig_reviews.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=380
            )
            st.plotly_chart(fig_reviews, use_container_width=True)

            st.markdown(
                '<div class="insight-card"><b>Insight:</b> Review behaviour is concentrated around positive scores, indicating a generally satisfactory customer experience.</div>',
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
                .head(top_n)
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
                height=380,
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig_review_cat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# RESEARCH NOTES TAB
# -----------------------------
with tab5:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Research Interpretation Notes")
    st.markdown("""
- The dashboard is built directly from the **Gold layer** of the Medallion architecture.
- Revenue analysis reveals concentration in a small number of high-performing categories.
- Customer analysis supports the importance of **high-value customer retention**.
- Review analysis indicates generally positive satisfaction, with variation across categories.
- The dashboard demonstrates how a Lakehouse-based pipeline can support business-ready analytics and executive decision-making.
    """)
    st.markdown(
        '<div class="insight-card"><b>Dissertation value:</b> This dashboard acts as the presentation layer of the project and demonstrates how cleaned and aggregated data can be transformed into decision-support tools for stakeholders.</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
