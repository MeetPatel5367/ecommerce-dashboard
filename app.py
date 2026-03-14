import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Enterprise E-commerce Research Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# HIDE STREAMLIT DEFAULT HEADER / WHITE SPACE
# ---------------------------------------------------------
st.markdown("""
<style>
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1500px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def get_quarter(month):
    if month in [1, 2, 3]:
        return "Q1"
    elif month in [4, 5, 6]:
        return "Q2"
    elif month in [7, 8, 9]:
        return "Q3"
    return "Q4"


def format_currency(value):
    return f"${value:,.2f}"


def safe_metric(series, func="sum"):
    if series.empty:
        return 0
    if func == "sum":
        return series.sum()
    if func == "mean":
        return series.mean()
    if func == "max":
        return series.max()
    if func == "min":
        return series.min()
    if func == "median":
        return series.median()
    if func == "std":
        return series.std()
    return 0


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.markdown("## Control Center")

available_years = sorted(monthly_sales["year"].unique())
selected_year = st.sidebar.selectbox("Select Analysis Year", available_years)

top_n = st.sidebar.slider("Top Customers", 5, 25, 10)

min_spent = float(customer_summary["total_spent"].min())
max_spent = float(customer_summary["total_spent"].max())

spending_threshold = st.sidebar.slider(
    "Minimum Customer Spending",
    min_value=min_spent,
    max_value=max_spent,
    value=min_spent
)

analysis_mode = st.sidebar.radio(
    "Analysis Focus",
    ["Balanced View", "Revenue Focus", "Customer Focus"]
)

show_raw_data = st.sidebar.checkbox("Show Raw Data", value=False)
show_methodology = st.sidebar.checkbox("Show Methodology", value=True)
show_future_scope = st.sidebar.checkbox("Show Future Scope", value=True)

# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------
filtered_sales = monthly_sales[monthly_sales["year"] == selected_year].sort_values("month").copy()
filtered_customers = customer_summary[customer_summary["total_spent"] >= spending_threshold].copy()
top_customers = filtered_customers.sort_values("total_spent", ascending=False).head(top_n).copy()

if "customer_id" in top_customers.columns:
    top_customers["short_customer_id"] = top_customers["customer_id"].astype(str).str[:10]
else:
    top_customers["short_customer_id"] = [f"C{i+1}" for i in range(len(top_customers))]

filtered_sales["quarter"] = filtered_sales["month"].apply(get_quarter)
quarterly_summary = (
    filtered_sales.groupby("quarter", as_index=False)["monthly_revenue"]
    .sum()
    .sort_values("quarter")
)

filtered_sales["previous_month_revenue"] = filtered_sales["monthly_revenue"].shift(1)
filtered_sales["mom_growth_percent"] = (
    (filtered_sales["monthly_revenue"] - filtered_sales["previous_month_revenue"])
    / filtered_sales["previous_month_revenue"]
) * 100
filtered_sales["mom_growth_percent"] = filtered_sales["mom_growth_percent"].round(2)

customer_summary = customer_summary.copy()
customer_summary["customer_segment"] = pd.cut(
    customer_summary["total_spent"],
    bins=[-np.inf, 100, 500, np.inf],
    labels=["Low Value", "Medium Value", "High Value"]
)
segment_counts = customer_summary["customer_segment"].value_counts().sort_index()

# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------
total_revenue = safe_metric(filtered_sales["monthly_revenue"], "sum")
avg_revenue = safe_metric(filtered_sales["monthly_revenue"], "mean")
max_revenue = safe_metric(filtered_sales["monthly_revenue"], "max")
min_revenue = safe_metric(filtered_sales["monthly_revenue"], "min")
median_revenue = safe_metric(filtered_sales["monthly_revenue"], "median")
revenue_std = safe_metric(filtered_sales["monthly_revenue"], "std")

avg_customer_spent = safe_metric(customer_summary["total_spent"], "mean")
median_customer_spent = safe_metric(customer_summary["total_spent"], "median")
top_customer_spent = safe_metric(customer_summary["total_spent"], "max")
total_customers = customer_summary["customer_id"].nunique() if "customer_id" in customer_summary.columns else len(customer_summary)

positive_growth = filtered_sales["mom_growth_percent"].dropna().gt(0).sum()
negative_growth = filtered_sales["mom_growth_percent"].dropna().lt(0).sum()

best_month_row = filtered_sales.loc[filtered_sales["monthly_revenue"].idxmax()] if not filtered_sales.empty else None
worst_month_row = filtered_sales.loc[filtered_sales["monthly_revenue"].idxmin()] if not filtered_sales.empty else None

monthly_sales_missing = monthly_sales.isna().sum().sum()
customer_summary_missing = customer_summary.isna().sum().sum()
monthly_sales_duplicates = monthly_sales.duplicated().sum()
customer_summary_duplicates = customer_summary.duplicated().sum()

# ---------------------------------------------------------
# PROFESSIONAL DESIGN
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(14,165,233,0.12), transparent 22%),
            linear-gradient(180deg, #020617 0%, #081224 45%, #0f172a 100%);
        color: #e2e8f0;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0b1120 100%);
        border-right: 1px solid rgba(96,165,250,0.15);
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    .hero-box {
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.88));
        border: 1px solid rgba(96,165,250,0.22);
        border-radius: 26px;
        padding: 34px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.28);
        position: relative;
        overflow: hidden;
    }

    .hero-box::after {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -80px;
        top: -80px;
        background: radial-gradient(circle, rgba(59,130,246,0.22), transparent 70%);
        pointer-events: none;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 10px;
        line-height: 1.15;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #cbd5e1;
        line-height: 1.8;
        max-width: 1100px;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }

    .badge-chip {
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(59,130,246,0.12);
        border: 1px solid rgba(96,165,250,0.18);
        color: #bfdbfe;
        font-size: 0.88rem;
        font-weight: 500;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(17,24,39,0.94));
        border: 1px solid rgba(96,165,250,0.14);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 14px 26px rgba(0,0,0,0.20);
        margin-bottom: 12px;
        transition: all 0.25s ease;
    }

    .metric-card:hover {
        border-color: rgba(96,165,250,0.35);
        transform: translateY(-2px);
    }

    .metric-label {
        font-size: 0.88rem;
        color: #93c5fd;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
    }

    .section-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.94), rgba(17,24,39,0.92));
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 14px 26px rgba(0,0,0,0.20);
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 1.18rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 14px;
    }

    .info-box {
        background: linear-gradient(135deg, rgba(37,99,235,0.14), rgba(15,23,42,0.30));
        border-left: 4px solid #3b82f6;
        border-radius: 16px;
        padding: 16px;
        color: #dbeafe;
        margin-top: 14px;
    }

    .success-box {
        background: linear-gradient(135deg, rgba(22,163,74,0.14), rgba(15,23,42,0.28));
        border-left: 4px solid #22c55e;
        border-radius: 16px;
        padding: 16px;
        color: #dcfce7;
        margin-top: 14px;
    }

    .warning-box {
        background: linear-gradient(135deg, rgba(249,115,22,0.14), rgba(15,23,42,0.28));
        border-left: 4px solid #f97316;
        border-radius: 16px;
        padding: 16px;
        color: #ffedd5;
        margin-top: 14px;
    }

    div[data-testid="stTabs"] button {
        background: rgba(15,23,42,0.74) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(96,165,250,0.14) !important;
        border-radius: 14px !important;
        padding: 10px 16px !important;
        margin-right: 6px !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        color: white !important;
        box-shadow: 0 8px 18px rgba(37,99,235,0.34);
    }

    .footer-note {
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        padding: 10px 0 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------
st.markdown(f"""
<div class="hero-box">
    <div class="hero-title">Enterprise E-commerce Research Analytics Platform</div>
    <div class="hero-subtitle">
        A professional digital analytics system for processed gold-layer e-commerce data.
        This platform supports revenue monitoring, customer intelligence, segmentation analysis,
        business reporting, technical explanation, and future-ready expansion for the selected year <b>{selected_year}</b>.
    </div>
    <div class="badge-row">
        <div class="badge-chip">Research Dashboard</div>
        <div class="badge-chip">Executive Reporting</div>
        <div class="badge-chip">Customer Intelligence</div>
        <div class="badge-chip">Future Ready</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">{format_currency(total_revenue)}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Monthly Revenue</div>
        <div class="metric-value">{format_currency(avg_revenue)}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    best_month_text = f"Month {int(best_month_row['month'])}" if best_month_row is not None else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Best Month</div>
        <div class="metric-value">{best_month_text}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Customers</div>
        <div class="metric-value">{total_customers:,}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview", "Revenue", "Customers", "Segments",
    "Quality & Export", "Methodology", "Future Scope"
])

with tab1:
    st.subheader("Executive Overview")

    st.write(
        f"For {selected_year}, total revenue is {format_currency(total_revenue)} "
        f"with average monthly revenue of {format_currency(avg_revenue)} "
        f"and median revenue of {format_currency(median_revenue)}."
    )

    if best_month_row is not None and worst_month_row is not None:
        st.write(
            f"The highest revenue month is Month {int(best_month_row['month'])} "
            f"with {format_currency(best_month_row['monthly_revenue'])}, while the lowest revenue month is "
            f"Month {int(worst_month_row['month'])} with {format_currency(worst_month_row['monthly_revenue'])}."
        )

    st.write(
        f"The yearly pattern shows {positive_growth} positive-growth months and "
        f"{negative_growth} negative-growth months."
    )

    if analysis_mode == "Revenue Focus":
        st.markdown("""
        <div class="info-box">
            <b>Revenue Focus:</b> This mode prioritises revenue performance, seasonal movement, and month-on-month change.
        </div>
        """, unsafe_allow_html=True)

    elif analysis_mode == "Customer Focus":
        st.markdown(f"""
        <div class="info-box">
            <b>Customer Focus:</b> The highest customer spending is <b>{format_currency(top_customer_spent)}</b>, showing concentrated customer value.
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="info-box">
            <b>Balanced View:</b> This dashboard combines financial analytics and customer intelligence in one interface.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="success-box">
        <b>Research Value:</b> The dashboard transforms processed data into readable, interactive, and decision-oriented insight.
    </div>
    """, unsafe_allow_html=True)



with tab2:
    a, b = st.columns([2, 1])

    with a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Monthly Revenue Trend</div>', unsafe_allow_html=True)
        st.line_chart(filtered_sales.set_index("month")["monthly_revenue"])
        st.markdown('</div>', unsafe_allow_html=True)

    with b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Revenue Statistics</div>', unsafe_allow_html=True)
        st.write(f"**Maximum revenue:** {format_currency(max_revenue)}")
        st.write(f"**Minimum revenue:** {format_currency(min_revenue)}")
        st.write(f"**Median revenue:** {format_currency(median_revenue)}")
        st.write(f"**Standard deviation:** {format_currency(revenue_std if pd.notna(revenue_std) else 0)}")
        st.markdown("""
        <div class="info-box">
            Revenue variation can indicate seasonality, campaign impact, or operational performance shifts.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    a2, b2 = st.columns(2)

    with a2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Quarterly Revenue Summary</div>', unsafe_allow_html=True)
        st.bar_chart(quarterly_summary.set_index("quarter")["monthly_revenue"])
        st.markdown('</div>', unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Month-on-Month Growth</div>', unsafe_allow_html=True)
        st.dataframe(filtered_sales[["month", "monthly_revenue", "mom_growth_percent"]], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    x, y = st.columns([2, 1])

    with x:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">Top {top_n} Customers by Spending</div>', unsafe_allow_html=True)
        st.bar_chart(top_customers.set_index("short_customer_id")["total_spent"])
        st.markdown('</div>', unsafe_allow_html=True)

    with y:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Customer Metrics</div>', unsafe_allow_html=True)
        st.write(f"**Average spending:** {format_currency(avg_customer_spent)}")
        st.write(f"**Median spending:** {format_currency(median_customer_spent)}")
        st.write(f"**Highest spending:** {format_currency(top_customer_spent)}")
        st.write(f"**Customers shown:** {len(top_customers)}")
        st.markdown("""
        <div class="info-box">
            High-value customers create strong opportunities for retention and targeted marketing analysis.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Customer Detail Table</div>', unsafe_allow_html=True)
    st.dataframe(top_customers[["customer_id", "total_orders", "total_spent"]], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    p, q = st.columns(2)

    with p:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Customer Segment Distribution</div>', unsafe_allow_html=True)
        st.bar_chart(segment_counts)
        st.markdown('</div>', unsafe_allow_html=True)

    with q:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Segment Interpretation</div>', unsafe_allow_html=True)
        st.write("**Low Value:** below 100")
        st.write("**Medium Value:** 100 to 500")
        st.write("**High Value:** above 500")
        st.markdown("""
        <div class="info-box">
            Segmentation supports easier business interpretation and prepares the project for future machine learning use.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    m, n = st.columns(2)

    with m:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Data Quality Summary</div>', unsafe_allow_html=True)
        quality_df = pd.DataFrame({
            "Dataset": ["Monthly Sales", "Customer Summary"],
            "Rows": [len(monthly_sales), len(customer_summary)],
            "Columns": [len(monthly_sales.columns), len(customer_summary.columns)],
            "Missing Values": [monthly_sales_missing, customer_summary_missing],
            "Duplicate Rows": [monthly_sales_duplicates, customer_summary_duplicates]
        })
        st.dataframe(quality_df, use_container_width=True)
        st.markdown("""
        <div class="success-box">
            Data quality checks increase project reliability and strengthen professional presentation.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with n:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Download Processed Outputs</div>', unsafe_allow_html=True)

        sales_csv = filtered_sales.to_csv(index=False).encode("utf-8")
        st.download_button("Download Revenue CSV", sales_csv, f"revenue_analysis_{selected_year}.csv", "text/csv")

        customer_csv = top_customers[["customer_id", "total_orders", "total_spent"]].to_csv(index=False).encode("utf-8")
        st.download_button("Download Customer CSV", customer_csv, "customer_analysis.csv", "text/csv")

        quarterly_csv = quarterly_summary.to_csv(index=False).encode("utf-8")
        st.download_button("Download Quarterly CSV", quarterly_csv, "quarterly_revenue_summary.csv", "text/csv")

        st.markdown('</div>', unsafe_allow_html=True)

    if show_raw_data:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Raw Processed Data</div>', unsafe_allow_html=True)
        with st.expander("Monthly Sales Dataset"):
            st.dataframe(monthly_sales, use_container_width=True)
        with st.expander("Customer Summary Dataset"):
            st.dataframe(customer_summary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab6:
    if show_methodology:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Technical Methodology</div>', unsafe_allow_html=True)

        st.write(
            "The project uses processed gold-layer e-commerce outputs derived from transformed source data. "
            "Monthly revenue and customer summary tables are loaded into the dashboard for analytical presentation."
        )
        st.write(
            "This structure demonstrates a practical pipeline: raw data, transformation, summary generation, and interactive reporting."
        )

        st.markdown("""
        <div class="info-box">
            <b>Pipeline Logic:</b> raw data → cleaned data → gold summary tables → analytical dashboard
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="success-box">
            <b>Technical Strength:</b> This project reflects both data engineering logic and business intelligence presentation.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab7:
    if show_future_scope:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Future Enhancement Scope</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="success-box"><b>1. Predictive Analytics:</b> revenue forecasting models</div>
        <div class="success-box"><b>2. Real-Time Integration:</b> Databricks or cloud connection</div>
        <div class="success-box"><b>3. Product-Level Analysis:</b> category and product insights</div>
        <div class="success-box"><b>4. User Access Layers:</b> analyst, manager, and executive views</div>
        <div class="success-box"><b>5. Machine Learning Expansion:</b> churn prediction and recommendation systems</div>
        <div class="warning-box"><b>Scalability:</b> this prototype can be extended into a full enterprise analytics application.</div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<hr>
<div class="footer-note">
This professional analytics platform demonstrates how processed e-commerce data can be transformed into a modern business intelligence system.
</div>
""", unsafe_allow_html=True)
