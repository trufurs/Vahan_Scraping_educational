import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Vehicle Registration Analysis Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 16px;
        white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

# Database configuration
base_dir = Path(__file__).parent
db_path = base_dir / "data" / "vahan_data.db"

# Vehicle category mappings
VEHICLE_CATEGORIES = {
    '2W': ['twn', 'twt'],
    '3W': ['thwn', 'thwt'],
    '4W': ['lmv', 'mmv', 'hmv']
}

# Category display names
CATEGORY_DISPLAY_NAMES = {
    'twn': '2WN (2 Wheeler Non-Transport)',
    'twt': '2WT (2 Wheeler Transport)',
    'thwn': '3WN (3 Wheeler Non-Transport)',
    'thwt': '3WT (3 Wheeler Transport)',
    'lmv': 'LMV (Light Motor Vehicle)',
    'mmv': 'MMV (Medium Motor Vehicle)',
    'hmv': 'HMV (Heavy Motor Vehicle)'
}

def get_display_name(col):
    return CATEGORY_DISPLAY_NAMES.get(col, col)

# Helper functions
def connect_to_db():
    return sqlite3.connect(str(db_path))

def get_month_order(month):
    month_order = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    return month_order.get(month, 13)

def get_quarter(month):
    return (get_month_order(month) - 1) // 3 + 1

def get_available_years():
    with connect_to_db() as conn:
        query = "SELECT DISTINCT year FROM vehicle_data ORDER BY year DESC"
        df = pd.read_sql_query(query, conn)
        return df['year'].tolist()

def calculate_growth(df, group_col, value_cols):
    df_grouped = df.groupby(group_col)[value_cols].sum()
    df_pct = df_grouped.pct_change() * 100
    return df_grouped, df_pct

def get_vehicle_data(selected_years, selected_categories):
    columns = ['maker', 'month', 'year']
    conditions = []
    
    for category, fields in VEHICLE_CATEGORIES.items():
        if category in selected_categories:
            columns.extend(fields)
            conditions.append('(' + ' OR '.join(f'{field} > 0' for field in fields) + ')')
    
    if not conditions:
        return pd.DataFrame()
    
    query = f"""
    SELECT {', '.join(columns)}
    FROM vehicle_data
    WHERE ({' OR '.join(conditions)})
    AND year IN ({','.join(map(str, selected_years))})
    """
    
    with connect_to_db() as conn:
        df = pd.read_sql_query(query, conn)
        df['month_order'] = df['month'].apply(get_month_order)
        df['quarter'] = df['month'].apply(get_quarter)
        df['period'] = df.apply(lambda x: f"{x['year']}-{x['month']}", axis=1)
        df = df.sort_values(['year', 'month_order'])
        return df

# Dashboard Header
st.title("🚗 Vehicle Registration Analysis Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Dashboard Controls")
    
    # Year Selection
    st.subheader("1️⃣ Time Period")
    available_years = get_available_years()
    selected_years = st.multiselect(
        "Select Years",
        options=available_years,
        default=available_years[-2:] if len(available_years) > 1 else available_years,
        key='years'
    )
    
    # Category Selection
    st.subheader("2️⃣ Vehicle Categories")
    vehicle_categories = ['2W', '3W', '4W']
    selected_categories = st.multiselect(
        "Select Categories",
        options=vehicle_categories,
        default=['2W'],
        key='categories'
    )
    
    # Show category legend
    if selected_categories:
        st.markdown("#### Category Legend")
        for category in selected_categories:
            if category == '2W':
                st.markdown("""
                - **2WN**: 2 Wheeler Non-Transport
                - **2WT**: 2 Wheeler Transport
                """)
            elif category == '3W':
                st.markdown("""
                - **3WN**: 3 Wheeler Non-Transport
                - **3WT**: 3 Wheeler Transport
                """)
            elif category == '4W':
                st.markdown("""
                - **LMV**: Light Motor Vehicle
                - **MMV**: Medium Motor Vehicle
                - **HMV**: Heavy Motor Vehicle
                """)

# Main Content
if selected_years and selected_categories:
    df = get_vehicle_data(selected_years, selected_categories)
    
    if not df.empty:
        # Get category columns
        category_cols = [col for col in df.columns 
                        if col not in ['maker', 'month', 'year', 'month_order', 'quarter', 'period']]
        
        # Get available manufacturers
        available_manufacturers = sorted(df['maker'].unique().tolist())
        
        # Manufacturer Selection in Sidebar
        with st.sidebar:
            st.subheader("3️⃣ Manufacturers")
            selected_manufacturers = st.multiselect(
                "Select Manufacturers",
                options=available_manufacturers,
                default=available_manufacturers[:5],
                key='manufacturers'
            )
        
        # Filter by selected manufacturers
        if selected_manufacturers:
            df = df[df['maker'].isin(selected_manufacturers)]
        
        # Main Dashboard Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Market Analysis", "💹 Growth Metrics"])
        
        with tab1:
            st.header("Market Overview")
            
            # Key Metrics
            total_registrations = df[category_cols].sum().sum()
            unique_manufacturers = df['maker'].nunique()
            latest_month = df.sort_values(['year', 'month_order']).iloc[-1]['period']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Registrations", f"{total_registrations:,.0f}")
            with col2:
                st.metric("Active Manufacturers", unique_manufacturers)
            with col3:
                st.metric("Latest Data", latest_month)
            
            st.markdown("---")
            
            # Category Distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Category Distribution")
                category_totals = df[category_cols].sum()
                category_totals.index = [get_display_name(col) for col in category_totals.index]
                fig = px.pie(
                    values=category_totals.values,
                    names=category_totals.index,
                    title="Registration Distribution by Category"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key="category_dist")
            
            with col2:
                st.subheader("Top Manufacturers")
                manufacturer_totals = df.groupby('maker')[category_cols].sum().sum(axis=1)
                top_manufacturers = manufacturer_totals.nlargest(10)
                fig = px.bar(
                    x=top_manufacturers.index,
                    y=top_manufacturers.values,
                    title="Top 10 Manufacturers by Volume",
                    labels={"x": "Manufacturer", "y": "Total Registrations"}
                )
                st.plotly_chart(fig, use_container_width=True, key="top_mfg")
        
        with tab2:
            st.header("Market Analysis")
            
            # Time Series Analysis
            st.subheader("Registration Trends")
            
            # Monthly trend by category
            monthly_category_data = df.groupby(['period', 'year', 'month_order'])[category_cols].sum().reset_index()
            monthly_category_data = monthly_category_data.sort_values(['year', 'month_order'])
            
            # Rename columns for display
            plot_data = monthly_category_data.copy()
            plot_data = plot_data.rename(columns={col: get_display_name(col) for col in category_cols})
            
            fig = px.line(
                plot_data,
                x='period',
                y=[get_display_name(col) for col in category_cols],
                title="Monthly Registration Trends by Category",
                labels={'value': 'Registrations', 'variable': 'Category Type'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True, key="monthly_trend")
            
            # Manufacturer Market Share
            st.subheader("Market Share Analysis")
            
            latest_year = df['year'].max()
            latest_data = df[df['year'] == latest_year]
            
            market_share = latest_data.groupby('maker')[category_cols].sum()
            market_share_pct = market_share.div(market_share.sum()) * 100
            
            top_market_share = market_share_pct.sum(axis=1).nlargest(5)
            
            fig = px.pie(
                values=top_market_share.values,
                names=top_market_share.index,
                title=f"Top 5 Manufacturers Market Share ({latest_year})"
            )
            st.plotly_chart(fig, use_container_width=True, key="market_share")
        
        with tab3:
            st.header("Growth Analysis")
            
            # YoY Growth
            if len(selected_years) > 1:
                st.subheader("Year-over-Year Growth")
                
                yearly_data = df.groupby(['year', 'maker'])[category_cols].sum()
                manufacturer_growth = yearly_data.groupby('maker').pct_change() * 100
                
                # Get the latest year's growth for each manufacturer
                latest_growth = manufacturer_growth.groupby('maker').last()
                top_growth = latest_growth.mean(axis=1).nlargest(5)
                
                fig = px.bar(
                    x=top_growth.index,
                    y=top_growth.values,
                    title="Top 5 Manufacturers by Growth Rate (%)",
                    labels={"x": "Manufacturer", "y": "Growth Rate (%)"}
                )
                st.plotly_chart(fig, use_container_width=True, key="growth_rate")
                
                # Category Growth Trends
                st.subheader("Category Growth Trends")
                
                yearly_category = df.groupby('year')[category_cols].sum()
                category_growth = yearly_category.pct_change() * 100
                
                # Rename columns for display
                category_growth_display = category_growth.copy()
                category_growth_display.columns = [get_display_name(col) for col in category_growth.columns]
                
                fig = px.bar(
                    category_growth_display,
                    title="Category-wise YoY Growth (%)",
                    labels={"value": "Growth Rate (%)", "variable": "Category Type"}
                )
                st.plotly_chart(fig, use_container_width=True, key="category_growth")
            else:
                st.info("Please select multiple years to view growth analysis")
            
            # Quarterly Analysis
            st.subheader("Quarterly Performance")
            quarterly_data = df.groupby(['year', 'quarter'])[category_cols].sum()
            
            # Prepare data with display names
            quarterly_plot_data = quarterly_data.reset_index()
            quarterly_plot_data = quarterly_plot_data.rename(
                columns={col: get_display_name(col) for col in category_cols}
            )
            
            fig = px.line(
                quarterly_plot_data,
                x='quarter',
                y=[get_display_name(col) for col in category_cols],
                color='year',
                title="Quarterly Registration Trends",
                labels={"quarter": "Quarter", "value": "Registrations", "variable": "Category Type"}
            )
            st.plotly_chart(fig, use_container_width=True, key="quarterly_trend")
    else:
        st.warning("No data available for the selected criteria")
else:
    st.info("👈 Please select at least one year and one vehicle category from the sidebar to begin")
