import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from dbconnector import get_engine

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Retail Pulse | Pro Analytics", 
    page_icon="🌌", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- ADVANCED CSS INJECTION ----------------
custom_css = """
<style>
    /* Animated Gradient Title */
    .title-glow {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #818cf8, #c084fc, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    /* Hover Effects for Metric Cards */
    [data-testid="stMetric"] {
        background-color: #1e293b;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #334155;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
        border-color: #6366f1;
    }
    
    /* Clean up top padding */
    [data-testid="block-container"] {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Initialize engine globally
engine = get_engine()

# ---------------- CACHING & DATA FETCHING ----------------
@st.cache_data(show_spinner=False, ttl=600)
def run_query(query: str, params: dict = None) -> pd.DataFrame:
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)
    except SQLAlchemyError as e:
        st.error(f"Database connection error: {e}")
        st.stop()

# ---------------- MAIN APPLICATION ----------------
def main():
    # Header Section
    st.markdown("<h1 class='title-glow'>🌌 Retail Pulse Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 2rem;'>Real-time AI-Enhanced Operations Analytics</p>", unsafe_allow_html=True)

    # --- INITIAL DATA LOAD ---
    try:
        date_bounds = run_query("SELECT MIN(sale_date) as min_date, MAX(sale_date) as max_date FROM retail_sales;").iloc[0]
        gender_list = run_query("SELECT DISTINCT gender FROM retail_sales;")["gender"].tolist()
        category_list = run_query("SELECT DISTINCT category FROM retail_sales;")["category"].tolist()
    except Exception:
        st.warning("Could not load database. Please check your connection.")
        st.stop()

    # --- SIDEBAR FILTERS ---
    with st.sidebar:
        st.markdown("### 🎛️ Mission Control")
        st.markdown("---")
        
        date_range = st.date_input("📅 Date Range", [date_bounds['min_date'], date_bounds['max_date']])
        gender_filter = st.multiselect("👥 Demographics", gender_list, default=gender_list)
        category_filter = st.multiselect("📦 Product Categories", category_list, default=category_list)
        
        st.markdown("---")
        if st.button("↻ Reset Views", use_container_width=True):
            st.rerun()

    # Validation
    if len(date_range) != 2 or not gender_filter or not category_filter:
        st.info("💡 Adjust the filters in the sidebar to populate the dashboard.")
        st.stop()

    params = {
        "start_date": date_range[0],
        "end_date": date_range[1],
        "gender": tuple(gender_filter),
        "category": tuple(category_filter)
    }
    
    base_where_clause = "WHERE sale_date BETWEEN :start_date AND :end_date AND gender IN :gender AND category IN :category"

    # --- KPI METRIC CARDS ---
    kpi_query = f"""
    SELECT SUM(total_sale) AS total_sales, 
           COUNT(DISTINCT customer_id) AS total_customers, 
           COUNT(transaction_id) AS total_orders 
    FROM retail_sales {base_where_clause}
    """
    kpi_df = run_query(kpi_query, params)
    
    # Calculate Average Order Value (AOV)
    sales_val = kpi_df['total_sales'].iloc[0] or 0
    orders_val = kpi_df['total_orders'].iloc[0] or 1
    aov_val = sales_val / orders_val

    # 4 Columns for Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gross Revenue", f"${sales_val:,.0f}")
    col2.metric("Total Transactions", f"{orders_val:,}")
    col3.metric("Unique Customers", f"{kpi_df['total_customers'].iloc[0]:,}")
    col4.metric("Avg Order Value (AOV)", f"${aov_val:,.2f}")
        
    st.write("---") # Spacer line

    # --- ADVANCED CHARTS SECTION ---
    # We will query a daily aggregated dataset once to build multiple charts (faster than multiple SQL queries)
    daily_query = f"""
    SELECT sale_date, category, gender, SUM(total_sale) AS daily_sales
    FROM retail_sales {base_where_clause}
    GROUP BY sale_date, category, gender
    """
    df_daily = run_query(daily_query, params)

    if not df_daily.empty:
        df_daily['sale_date'] = pd.to_datetime(df_daily['sale_date'])
        df_daily['day_of_week'] = df_daily['sale_date'].dt.day_name()
        
        plotly_template = "plotly_dark"
        chart_bg_color = 'rgba(0,0,0,0)' 
        custom_indigo_colors = ['#3730a3', '#4f46e5', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe']

        # ROW 1: Trend Line & Donut
        row1_col1, row1_col2 = st.columns([2, 1])

        with row1_col1:
            st.markdown("### 📈 Revenue Trajectory")
            trend_df = df_daily.groupby('sale_date')['daily_sales'].sum().reset_index()
            fig_area = px.area(
                trend_df, x="sale_date", y="daily_sales", 
                template=plotly_template, color_discrete_sequence=["#818cf8"]
            )
            fig_area.update_layout(
                plot_bgcolor=chart_bg_color, paper_bgcolor=chart_bg_color,
                xaxis=dict(showgrid=False, title=""), 
                yaxis=dict(showgrid=True, gridcolor='#334155', title="Revenue ($)"),
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_area, use_container_width=True)

        with row1_col2:
            st.markdown("### 📦 Category Share")
            cat_df = df_daily.groupby('category')['daily_sales'].sum().reset_index()
            fig_donut = px.pie(
                cat_df, values="daily_sales", names="category", hole=0.7,
                template=plotly_template, color_discrete_sequence=custom_indigo_colors
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent')
            fig_donut.update_layout(
                plot_bgcolor=chart_bg_color, paper_bgcolor=chart_bg_color,
                margin=dict(l=0, r=0, t=10, b=0), showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        # ROW 2: Heatmap & Stacked Bar
        row2_col1, row2_col2 = st.columns([1, 1])

        with row2_col1:
            st.markdown("### 🔥 Sales Intensity (Day vs. Category)")
            heatmap_df = df_daily.groupby(['day_of_week', 'category'])['daily_sales'].sum().reset_index()
            # Order days logically
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            fig_heat = px.density_heatmap(
                heatmap_df, x="category", y="day_of_week", z="daily_sales",
                category_orders={"day_of_week": days_order},
                color_continuous_scale="Purples", template=plotly_template
            )
            fig_heat.update_layout(
                plot_bgcolor=chart_bg_color, paper_bgcolor=chart_bg_color,
                xaxis_title="", yaxis_title="", margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        with row2_col2:
            st.markdown("### 👥 Demographic Preferences")
            demo_df = df_daily.groupby(['category', 'gender'])['daily_sales'].sum().reset_index()
            fig_bar = px.bar(
                demo_df, x="daily_sales", y="category", color="gender", 
                orientation='h', template=plotly_template,
                color_discrete_sequence=['#c084fc', '#6366f1', '#38bdf8']
            )
            fig_bar.update_layout(
                plot_bgcolor=chart_bg_color, paper_bgcolor=chart_bg_color,
                xaxis_title="Revenue ($)", yaxis_title="", barmode="stack",
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.info("No data available for these visualizations.")

    st.write("---")

    # --- RAW DATA TABLE WITH CONDITIONAL FORMATTING ---
    with st.expander("📄 View Transaction Ledger"):
        raw_query = f"SELECT sale_date, customer_id, gender, category, total_sale FROM retail_sales {base_where_clause} ORDER BY sale_date DESC LIMIT 500"
        df_raw = run_query(raw_query, params)
        
        if not df_raw.empty:
            # Add a gradient background to the total_sale column to act as a data bar
            st.dataframe(
                df_raw.style.background_gradient(subset=['total_sale'], cmap='Purples'),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No transactions found.")

if __name__ == "__main__":
    main()