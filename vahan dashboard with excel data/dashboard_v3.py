import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import calendar

# Page config
st.set_page_config(
    page_title="Vahan Registration Analysis Dashboard",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
    }
    .trend-positive {
        color: green;
        font-weight: bold;
    }
    .trend-negative {
        color: red;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_database_connection():
    return sqlite3.connect('vahan_data.db', check_same_thread=False)

conn = get_database_connection()

def load_vehicle_class_data():
    query = """
    SELECT 
        vehicle_class,
        category,
        year,
        month,
        registrations
    FROM vehicle_class_registrations
    ORDER BY year, month
    """
    return pd.read_sql_query(query, conn)

def load_manufacturer_data():
    query = """
    SELECT 
        manufacturer,
        year,
        month,
        registrations
    FROM manufacturer_registrations
    ORDER BY year, month
    """
    return pd.read_sql_query(query, conn)

# Load data
vehicle_class_df = load_vehicle_class_data()
manufacturer_df = load_manufacturer_data()

# Sidebar filters
st.sidebar.header("Filters")
available_years = sorted(pd.concat([vehicle_class_df['year'], manufacturer_df['year']]).unique())
selected_year = st.sidebar.selectbox("Select Year", available_years)
selected_month = st.sidebar.selectbox("Select Month", range(1, 13), format_func=lambda x: calendar.month_name[x])

# Title
st.title("Vehicle Registration Analysis Dashboard")

# Create tabs
vehicle_tab, manufacturer_tab = st.tabs(["Vehicle Class Analysis", "Manufacturer Analysis"])

# Vehicle Class Analysis Tab
with vehicle_tab:
    st.header("Vehicle Class Analysis")
    
    # Filter data for selected period
    vc_period_data = vehicle_class_df[
        (vehicle_class_df['year'] == selected_year) &
        (vehicle_class_df['month'] == selected_month)
    ]
    
    if len(vc_period_data) == 0:
        st.warning(f"No vehicle class data available for {calendar.month_name[selected_month]} {selected_year}")
    else:
        # Category distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Category-wise registrations
            category_data = vc_period_data.groupby('category')['registrations'].sum().reset_index()
            if not category_data.empty:
                fig_category = px.pie(
                    category_data,
                    values='registrations',
                    names='category',
                    title="Registration Distribution by Category (2W/3W/4W)",
                    hole=0.3
                )
                st.plotly_chart(fig_category)
        
        with col2:
            # Vehicle class bar chart
            vehicle_class_data = vc_period_data.sort_values('registrations', ascending=True)
            if not vehicle_class_data.empty:
                fig_vehicle_class = px.bar(
                    vehicle_class_data,
                    x='registrations',
                    y='vehicle_class',
                    color='category',
                    title="Vehicle Class Distribution",
                    orientation='h'
                )
                st.plotly_chart(fig_vehicle_class)
        
        # Monthly trends
        st.subheader("Monthly Registration Trends")
        yearly_data = vehicle_class_df[vehicle_class_df['year'] == selected_year]
        if not yearly_data.empty:
            monthly_trend = yearly_data.groupby(['month', 'category'])['registrations'].sum().reset_index()
            fig_trend = px.line(
                monthly_trend,
                x='month',
                y='registrations',
                color='category',
                title=f"Monthly Registration Trends by Category ({selected_year})",
                labels={'month': 'Month', 'registrations': 'Total Registrations'}
            )
            fig_trend.update_xaxes(
                ticktext=list(calendar.month_name)[1:],
                tickvals=list(range(1, 13))
            )
            st.plotly_chart(fig_trend)

# Manufacturer Analysis Tab
with manufacturer_tab:
    st.header("Manufacturer Analysis")
    
    # Filter data for selected period
    mfg_period_data = manufacturer_df[
        (manufacturer_df['year'] == selected_year) &
        (manufacturer_df['month'] == selected_month)
    ]
    
    if len(mfg_period_data) == 0:
        st.warning(f"No manufacturer data available for {calendar.month_name[selected_month]} {selected_year}")
    else:
        # Top manufacturers
        col3, col4 = st.columns(2)
        
        with col3:
            # Market share of top manufacturers
            top_manufacturers = mfg_period_data.nlargest(10, 'registrations')
            if not top_manufacturers.empty:
                fig_top_mfg = px.pie(
                    top_manufacturers,
                    values='registrations',
                    names='manufacturer',
                    title="Top 10 Manufacturers Market Share",
                    hole=0.3
                )
                st.plotly_chart(fig_top_mfg)
        
        with col4:
            # Manufacturer registration comparison
            if not top_manufacturers.empty:
                fig_mfg_comp = px.bar(
                    top_manufacturers.sort_values('registrations', ascending=True),
                    x='registrations',
                    y='manufacturer',
                    title="Top 10 Manufacturers Registration Volume",
                    orientation='h'
                )
                st.plotly_chart(fig_mfg_comp)
        
        # Monthly manufacturer trends
        st.subheader("Top Manufacturers Monthly Trends")
        
        # Get top 5 manufacturers
        top_5_manufacturers = mfg_period_data.nlargest(5, 'registrations')['manufacturer'].tolist()
        
        yearly_mfg_data = manufacturer_df[
            (manufacturer_df['year'] == selected_year) &
            (manufacturer_df['manufacturer'].isin(top_5_manufacturers))
        ]
        
        if not yearly_mfg_data.empty:
            fig_mfg_trend = px.line(
                yearly_mfg_data,
                x='month',
                y='registrations',
                color='manufacturer',
                title=f"Monthly Registration Trends - Top 5 Manufacturers ({selected_year})",
                labels={'month': 'Month', 'registrations': 'Registrations'}
            )
            fig_mfg_trend.update_xaxes(
                ticktext=list(calendar.month_name)[1:],
                tickvals=list(range(1, 13))
            )
            st.plotly_chart(fig_mfg_trend)

# Key Metrics
st.header("Key Market Insights")
metric_cols = st.columns(4)

with metric_cols[0]:
    total_vc_registrations = vc_period_data['registrations'].sum() if not vc_period_data.empty else 0
    st.metric(
        "Total Vehicle Registrations",
        f"{total_vc_registrations:,}",
        "units"
    )

with metric_cols[1]:
    if not vc_period_data.empty:
        category_totals = vc_period_data.groupby('category')['registrations'].sum()
        top_category = category_totals.idxmax() if not category_totals.empty else "N/A"
        top_category_share = (category_totals.max() / category_totals.sum() * 100) if not category_totals.empty else 0
    else:
        top_category = "N/A"
        top_category_share = 0
        
    st.metric(
        "Leading Category",
        top_category,
        f"{top_category_share:.1f}% market share"
    )

with metric_cols[2]:
    total_manufacturers = len(mfg_period_data['manufacturer'].unique()) if not mfg_period_data.empty else 0
    st.metric(
        "Active Manufacturers",
        total_manufacturers,
        "companies"
    )

with metric_cols[3]:
    if not mfg_period_data.empty:
        top_manufacturer_data = mfg_period_data.nlargest(1, 'registrations').iloc[0]
        top_manufacturer = top_manufacturer_data['manufacturer']
        top_mfg_share = (top_manufacturer_data['registrations'] / mfg_period_data['registrations'].sum() * 100)
    else:
        top_manufacturer = "N/A"
        top_mfg_share = 0
        
    st.metric(
        "Market Leader",
        top_manufacturer,
        f"{top_mfg_share:.1f}% market share"
    )
