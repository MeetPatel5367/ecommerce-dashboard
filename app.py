import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Enterprise E-commerce Research Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# PAGE STYLE
# -------------------------------------------------
st.markdown("""
<style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1450px;
    }

    .stApp {
        background: linear-gradient(135deg, #020617 0%, #081225 45%, #0f172a 100%);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #06101f 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    .hero-box {
        background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.92));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 28px;
        padding: 38px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.30);
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.15;
        margin-bottom: 14px;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        line-height: 1.9;
        margin-bottom: 16px;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 14px;
    }

    .hero-badge {
        background: rgba(59,130,246,0.15);
        border: 1px solid rgba(96,165,250,0.25);
        color: #dbeafe;
        padding: 8px 16px;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(17,24,39,0.95));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 14px 28px rgba(0,0,0,0.22);
        margin-bottom: 12px;
        min-height: 145px;
    }

    .metric-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #93c5fd;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.25;
        word-break: break-word;
    }

    .clean-text-box {
        background: linear-gradient(135deg, rgba(15,23,42,0.92), rgba(30,41,59,0.88));
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 22px;
        padding: 28px;
        margin-top: 18px;
        margin-bottom: 18px;
        box-shadow: 0 12px 24px rgba(0,0,0,0.20);
    }

    .clean-text-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 20px;
    }

    .clean-paragraph {
        font-size: 1.08rem;
        line-height: 2;
        color: #e2e8f0;
        margin-bottom: 18px;
    }

    .highlight-number {
        color: #7dd3fc;
        font-weight: 700;
    }

    .highlight-word {
        color: #ffffff;
        font-weight: 700;
    }

    .insight-box {
        background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(15,23,42,0.35));
        border-left: 4px solid #3b82f6;
        border-radius: 16px;
        padding: 16px 18px;
        margin-top: 16px;
        color: #dbeafe;
        font-size: 1rem;
        line-height: 1.8;
    }

    .research-box {
        background: linear-gradient(135deg, rgba(22,163,74,0.16), rgba(15,23,42,0.35));
        border-left: 4px solid #22c55e;
        border-radius: 16px;
        padding: 16px 18px;
        margin-top: 14px;
        color: #dcfce7;
        font-size: 1rem;
        line-height: 1.8;
    }

    div[data-testid="stTabs"] button {
        background: rgba(15,23,42,0.75) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        padding: 10px 16px !important;
        margin-right: 6px !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    monthly_sales = pd.read_csv("data/gold_monthly_sales.csv")
    customer_summary = pd.read_csv("data/gold_customer_summary.csv")

    monthly_sales.columns = monthly_sales.columns.str.strip().str.lower()
    customer_summary.columns = customer_summary.columns.str.strip().str.lower()

    monthly_sales["year"] = pd.to_numeric(monthly_sales["year"], errors="coerce")
    monthly_sales["month"] = pd.to_numeric(monthly_sales["month"], errors="coerce")
    monthly_sales["monthly_revenue"] = pd.to_numeric(monthly_sales["monthly_revenue"], errors="coerce")

    customer_summary["total_orders"] = pd.to_numeric(customer_summary["total_orders"], errors="coerce")
    customer_summary["total_spent"] = pd.to_numeric(customer_summary["total_spent"], errors="coerce")

    monthly_sales = monthly_sales.dropna(subset=["year", "month", "monthly_revenue"]).copy()
    customer_summary = customer_summary.dropna(subset=["total_orders", "total_spent"]).copy()

    monthly_sales["year"] = monthly_sales["year"].astype(int)
    monthly_sales["month"] = monthly_sales["month"].astype(int)

    return monthly_sales, customer_summary

monthly_sales, customer_summary = load_data()

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def get_quarter(month):
    if month in [1, 2, 3]:
        return "Q1"
    elif month in [4, 5, 6]:
        return "Q2"
    elif month in [7, 8, 9]:
        return "Q3"
    return "Q4"

def money(x):
    return f"${x:,.2f}"

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.markdown("## Control Center")

available_years = sorted(monthly_sales["year"].unique())
selected_year = st.sidebar.selectbox("Select Analysis Year", available_years)

top_n = st.sidebar.slider("Top Customers", 5, 25, 10)

min_spending = float(customer_summary["total_spent"].min())
max_spending = float(customer_summary["total_spent"].max())

min_customer_spending = st.sidebar.slider(
    "Minimum Customer Spending",
    min_value=min_spending,
    max_value=max_spending,
    value=min_spending
)

analysis_focus = st.sidebar.radio(
    "Analysis Focus",
    ["Balanced View", "Revenue Focus", "Customer Focus"]
)

show_raw_data = st.sidebar.checkbox("Show Raw Data", value=False)
show_methodology = st.sidebar.checkbox("Show Methodology", value=True)
show_future_scope = st.sidebar.checkbox("Show Future Scope", value=True)

# -------------------------------------------------
# FILTER DATA
# -------------------------------------------------
filtered_sales = monthly_sales[monthly_sales["year"] == selected_year].sort_values("month").copy()
filtered_sales["quarter"] = filtered_sales["month"].apply(get_quarter)

filtered_customers = customer_summary[customer_summary["total_spent"] >= min_customer_spending].copy()
top_customers = filtered_customers.sort_values("total_spent", ascending=False).head(top_n)

quarterly_summary = filtered_sales.groupby("quarter", as_index=False)["monthly_revenue"].sum()

filtered_sales["previous_month_revenue"] = filtered_sales["monthly_revenue"].shift(1)
filtered_sales["mom_growth_percent"] = (
    (filtered_sales["monthly_revenue"] - filtered_sales["previous_month_revenue"])
    / filtered_sales["previous_month_revenue"]
) * 100
filtered_sales["mom_growth_percent"] = filtered_sales["mom_growth_percent"].round(2)

customer_summary["customer_segment"] = pd.cut(
    customer_summary["total_spent"],
    bins=[-np.inf, 100, 500, np.inf],
    labels=["Low Value", "Medium Value", "High Value"]
)
segment_counts = customer_summary["customer_segment"].value_counts().sort_index()

# -------------------------------------------------
# METRICS
# -------------------------------------------------
total_revenue = filtered_sales["monthly_revenue"].sum()
avg_revenue = filtered_sales["monthly_revenue"].mean()
median_revenue = filtered_sales["monthly_revenue"].median()
total_customers = customer_summary["customer_id"].nunique() if "customer_id" in customer_summary.columns else len(customer_summary)

best_month = filtered_sales.loc[filtered_sales["monthly_revenue"].idxmax()]
worst_month = filtered_sales.loc[filtered_sales["monthly_revenue"].idxmin()]

positive_growth = filtered_sales["mom_growth_percent"].dropna().gt(0).sum()
negative_growth = filtered_sales["mom_growth_percent"].dropna().lt(0).sum()

avg_customer_spent = customer_summary["total_spent"].mean()
median_customer_spent = customer_summary["total_spent"].median()
top_customer_spent = customer_summary["total_spent"].max()

# -------------------------------------------------
# HERO SECTION
# -------------------------------------------------
st.markdown(f"""
<div class="hero-box">
    <div class="hero-title">Enterprise E-commerce Research Analytics Platform</div>
    <div class="hero-subtitle">
        A professional digital analytics system for processed gold-layer e-commerce data.
        This platform supports revenue monitoring, customer intelligence, segmentation analysis,
        business reporting, technical explanation, and future-ready expansion for the selected year <b>{selected_year}</b>.
    </div>
    <div class="hero-badges">
        <div class="hero-badge">Research Dashboard</div>
        <div class="hero-badge">Executive Reporting</div>
        <div class="hero-badge">Customer Intelligence</div>
        <div class="hero-badge">Future Ready</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# METRIC CARDS
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value">{money(total_revenue)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg Monthly Revenue</div>
        <div class="metric-value">{money(avg_revenue)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Best Month</div>
        <div class="metric-value">Month {int(best_month['month'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Customers</div>
        <div class="metric-value">{total_customers:,}</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview", "Revenue", "Customers", "Segments",
    "Quality & Export", "Methodology", "Future Scope"
])

# -------------------------------------------------
# OVERVIEW TAB WITH NEW WRITING DESIGN
# -------------------------------------------------
with tab1:
    st.markdown(f"""
    <div class="clean-text-box">
        <div class="clean-text-title">Executive Overview</div>

        <div class="clean-paragraph">
            For <span class="highlight-word">{selected_year}</span>, the total revenue is
            <span class="highlight-number">{money(total_revenue)}</span>,
            with an average monthly revenue of
            <span class="highlight-number">{money(avg_revenue)}</span>
            and a median revenue of
            <span class="highlight-number">{money(median_revenue)}</span>.
        </div>

        <div class="clean-paragraph">
            The highest revenue month is
            <span class="highlight-word">Month {int(best_month['month'])}</span>
            with revenue of
            <span class="highlight-number">{money(best_month['monthly_revenue'])}</span>,
            while the lowest revenue month is
            <span class="highlight-word">Month {int(worst_month['month'])}</span>
            with revenue of
            <span class="highlight-number">{money(worst_month['monthly_revenue'])}</span>.
        </div>

        <div class="clean-paragraph">
            The annual trend shows
            <span class="highlight-number">{positive_growth}</span> positive-growth months and
            <span class="highlight-number">{negative_growth}</span> negative-growth months,
            giving a clear picture of yearly business movement.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if analysis_focus == "Balanced View":
        st.markdown("""
        <div class="insight-box">
            <b>Balanced View:</b> This dashboard combines financial analytics and customer intelligence in one integrated interface.
        </div>
        """, unsafe_allow_html=True)
    elif analysis_focus == "Revenue Focus":
        st.markdown("""
        <div class="insight-box">
            <b>Revenue Focus:</b> This view places stronger attention on monthly income patterns, quarterly performance, and growth behaviour.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="insight-box">
            <b>Customer Focus:</b> Customer analysis shows strong value concentration, with the highest customer spending reaching {money(top_customer_spent)}.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="research-box">
        <b>Research Value:</b> The dashboard transforms processed data into readable, interactive, and decision-oriented business insight.
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# REVENUE TAB
# -------------------------------------------------
with tab2:
    st.subheader("Revenue Analytics")
    st.line_chart(filtered_sales.set_index("month")["monthly_revenue"])
    st.bar_chart(quarterly_summary.set_index("quarter")["monthly_revenue"])
    st.dataframe(filtered_sales[["month", "monthly_revenue", "mom_growth_percent"]], use_container_width=True)

# -------------------------------------------------
# CUSTOMERS TAB
# -------------------------------------------------
with tab3:
    st.subheader("Customer Analysis")
    if "customer_id" in top_customers.columns:
        customer_chart = top_customers.copy()
        customer_chart["label"] = customer_chart["customer_id"].astype(str).str[:12]
        st.bar_chart(customer_chart.set_index("label")["total_spent"])
        st.dataframe(top_customers[["customer_id", "total_orders", "total_spent"]], use_container_width=True)
    else:
        st.dataframe(top_customers, use_container_width=True)

    st.write(f"Average customer spending: {money(avg_customer_spent)}")
    st.write(f"Median customer spending: {money(median_customer_spent)}")
    st.write(f"Highest customer spending: {money(top_customer_spent)}")

# -------------------------------------------------
# SEGMENTS TAB
# -------------------------------------------------
with tab4:
    st.subheader("Customer Segmentation")
    st.bar_chart(segment_counts)
    st.write("Low Value: below 100")
    st.write("Medium Value: 100 to 500")
    st.write("High Value: above 500")

# -------------------------------------------------
# QUALITY TAB
# -------------------------------------------------
with tab5:
    st.subheader("Quality and Export")

    quality_df = pd.DataFrame({
        "Dataset": ["Monthly Sales", "Customer Summary"],
        "Rows": [len(monthly_sales), len(customer_summary)],
        "Columns": [len(monthly_sales.columns), len(customer_summary.columns)],
        "Missing Values": [monthly_sales.isna().sum().sum(), customer_summary.isna().sum().sum()],
        "Duplicate Rows": [monthly_sales.duplicated().sum(), customer_summary.duplicated().sum()]
    })

    st.dataframe(quality_df, use_container_width=True)

    st.download_button(
        "Download Revenue CSV",
        filtered_sales.to_csv(index=False).encode("utf-8"),
        file_name=f"revenue_analysis_{selected_year}.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download Customer CSV",
        top_customers.to_csv(index=False).encode("utf-8"),
        file_name="customer_analysis.csv",
        mime="text/csv"
    )

    if show_raw_data:
        st.subheader("Raw Data")
        st.dataframe(monthly_sales, use_container_width=True)
        st.dataframe(customer_summary, use_container_width=True)

# -------------------------------------------------
# METHODOLOGY TAB
# -------------------------------------------------
with tab6:
    if show_methodology:
        st.subheader("Technical Methodology")
        st.write(
            "This project uses processed gold-layer e-commerce data generated from cleaned and transformed source records."
        )
        st.write(
            "The dashboard reads monthly sales and customer summary outputs, then converts them into business-focused visual analytics."
        )
        st.write(
            "This reflects a clear pipeline approach: raw data, transformation, summary generation, and interactive presentation."
        )

# -------------------------------------------------
# FUTURE SCOPE TAB
# -------------------------------------------------
with tab7:
    if show_future_scope:
        st.subheader("Future Scope")
        st.write("1. Predictive revenue forecasting")
        st.write("2. Real-time cloud integration")
        st.write("3. Product-level analytics")
        st.write("4. Role-based dashboard access")
        st.write("5. Machine learning for churn prediction and recommendations")
