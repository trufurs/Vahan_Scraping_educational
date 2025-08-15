import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import calendar

# Database configuration
base_dir = Path(__file__).parent
db_path = base_dir / "data" / "vahan_data.db"

# Column mappings for vehicle categories
VEHICLE_CATEGORIES = {
    '2W': ['twn', 'twt'],
    '3W': ['thwn', 'thwt'],
    '4W': ['lmv', 'mmv', 'hmv']
}

def connect_to_db():
    return sqlite3.connect(str(db_path))

def get_month_order(month):
    month_order = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    return month_order.get(month, 13)

def get_available_years():
    with connect_to_db() as conn:
        query = "SELECT DISTINCT year FROM vehicle_data ORDER BY year DESC"
        df = pd.read_sql_query(query, conn)
        return df['year'].tolist()

def calculate_growth(df, group_col, value_cols):
    df_grouped = df.groupby(group_col)[value_cols].sum()
    df_pct = df_grouped.pct_change() * 100
    return df_grouped, df_pct

def get_quarter(month):
    return (get_month_order(month) - 1) // 3 + 1

def get_vehicle_data(selected_years, selected_categories):
    # Convert selected years to integers if they're strings
    selected_years = [int(year) for year in selected_years]
    
    # Base columns
    columns = ['maker', 'month', 'year']
    conditions = []
    
    # Add category columns and conditions
    for category, fields in VEHICLE_CATEGORIES.items():
        if category in selected_categories:
            columns.extend(fields)
            conditions.append(
                '(' + ' OR '.join(f'{field} > 0' for field in fields) + ')'
            )
    
    if not conditions:
        return pd.DataFrame()
    
    # Construct the query
    query = f"""
    SELECT {', '.join(columns)}
    FROM vehicle_data
    WHERE ({' OR '.join(conditions)})
    AND year IN ({','.join(map(str, selected_years))})
    """
    
    with connect_to_db() as conn:
        df = pd.read_sql_query(query, conn)
        df['month_order'] = df['month'].apply(get_month_order)
        df = df.sort_values(['year', 'month_order'])
        return df

def get_manufacturers_from_data(df):
    return sorted(df['maker'].unique().tolist())

# Dashboard Layout
st.set_page_config(page_title="Vahan Dashboard", layout="wide")
st.title("Vahan Vehicle Registration Dashboard")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Sidebar - Year Selection
st.sidebar.subheader("1. Select Years")
available_years = get_available_years()
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=available_years,
    default=available_years[-1:],
    key='years'
)

# Sidebar - Category Selection
st.sidebar.subheader("2. Select Vehicle Categories")
vehicle_categories = ['2W', '3W', '4W']
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=vehicle_categories,
    default=[],
    key='categories'
)

# Get filtered data based on selections
if selected_years and selected_categories:
    st.session_state.df = get_vehicle_data(selected_years, selected_categories)
    
    if not st.session_state.df.empty:
        # Get available manufacturers from filtered data
        available_manufacturers = get_manufacturers_from_data(st.session_state.df)
        
        # Manufacturer Selection
        st.sidebar.subheader("3. Select Manufacturers")
        selected_manufacturers = st.sidebar.multiselect(
            "Select Manufacturers",
            options=available_manufacturers,
            default=available_manufacturers[:10],
            key='manufacturers'
        )
        
        # Filter by selected manufacturers
        if selected_manufacturers:
            st.session_state.df = st.session_state.df[
                st.session_state.df['maker'].isin(selected_manufacturers)
            ]
        
        # Create visualization tabs
        tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Details"])
        
        # Get category columns
        category_cols = [col for col in st.session_state.df.columns 
                        if col not in ['maker', 'month', 'year', 'month_order']]
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            
            # Total registrations by category
            with col1:
                st.subheader("Category Totals")
                category_totals = st.session_state.df[category_cols].sum()
                fig = px.bar(x=category_totals.index, y=category_totals.values,
                            title="Total Registrations by Category")
                st.plotly_chart(fig, use_container_width=True, key="category_totals")
            
            # Top manufacturers
            with col2:
                st.subheader("Top Manufacturers")
                manufacturer_totals = st.session_state.df.groupby('maker')[category_cols].sum().sum(axis=1)
                top_manufacturers = manufacturer_totals.sort_values(ascending=False).head(10)
                fig = px.bar(x=top_manufacturers.index, y=top_manufacturers.values,
                            title="Top 10 Manufacturers")
                st.plotly_chart(fig, use_container_width=True, key="top_manufacturers")
            
            # Monthly trend
            with col3:
                st.subheader("Monthly Trend")
                monthly_data = st.session_state.df.groupby(['year', 'month', 'month_order'])[category_cols].sum()
                monthly_data = monthly_data.sum(axis=1).reset_index()
                monthly_data = monthly_data.sort_values(['year', 'month_order'])
                monthly_data['period'] = monthly_data.apply(lambda x: f"{x['year']}-{x['month']}", axis=1)
                fig = px.line(monthly_data, x='period', y=0,
                            title="Monthly Registration Trend")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True, key="monthly_trend")
        
        with tab2:
            # Yearly trend by category
            st.subheader("Yearly Trends")
            yearly_data = st.session_state.df.groupby('year')[category_cols].sum()
            fig = px.line(yearly_data, 
                         title="Yearly Trend by Category",
                         labels={'value': 'Registrations', 'variable': 'Category'})
            st.plotly_chart(fig, use_container_width=True, key="yearly_trends")
            
            # Monthly trend by category
            monthly_category_data = st.session_state.df.groupby(['year', 'month', 'month_order'])[category_cols].sum().reset_index()
            monthly_category_data = monthly_category_data.sort_values(['year', 'month_order'])
            monthly_category_data['period'] = monthly_category_data.apply(
                lambda x: f"{x['year']}-{x['month']}", axis=1)
            
            fig = px.line(monthly_category_data, x='period', y=category_cols,
                         title="Monthly Trend by Category",
                         labels={'value': 'Registrations', 'variable': 'Category'})
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True, key="monthly_category_trends")
        
        with tab3:
            st.subheader("Growth Analysis")
            
            # Add quarter information
            analysis_df = st.session_state.df.copy()
            analysis_df['quarter'] = analysis_df['month'].apply(get_quarter)
            analysis_df['period'] = analysis_df['year'].astype(str) + '-Q' + analysis_df['quarter'].astype(str)
            
            # YoY Growth Analysis
            st.subheader("Year-over-Year Growth")
            yearly_data = analysis_df.groupby('year')[category_cols].sum()
            _, yoy_growth = calculate_growth(analysis_df, 'year', category_cols)
            
            fig = px.bar(yoy_growth,
                        title="YoY Growth by Category (%)",
                        labels={'value': 'Growth %', 'variable': 'Category'})
            st.plotly_chart(fig, use_container_width=True, key="yoy_growth")
            
            # QoQ Growth Analysis
            st.subheader("Quarter-over-Quarter Growth")
            quarterly_data = analysis_df.groupby(['year', 'quarter'])[category_cols].sum()
            _, qoq_growth = calculate_growth(analysis_df.groupby(['year', 'quarter']).sum(), 'quarter', category_cols)
            
            fig = px.bar(qoq_growth,
                        title="QoQ Growth by Category (%)",
                        labels={'value': 'Growth %', 'variable': 'Category'})
            st.plotly_chart(fig, use_container_width=True, key="qoq_growth")
            
            # Manufacturer Growth Analysis
            st.subheader("Top Manufacturers Growth")
            
            # Calculate yearly totals for each manufacturer and category
            manufacturer_totals = []
            
            for year in analysis_df['year'].unique():
                year_data = analysis_df[analysis_df['year'] == year]
                for maker in year_data['maker'].unique():
                    maker_data = year_data[year_data['maker'] == maker]
                    for category in category_cols:
                        total = maker_data[category].sum()
                        manufacturer_totals.append({
                            'year': year,
                            'maker': maker,
                            'category': category,
                            'total': total
                        })
            
            # Convert to DataFrame
            mfg_df = pd.DataFrame(manufacturer_totals)
            
            # Calculate total volume for ranking
            maker_volumes = mfg_df.groupby('maker')['total'].sum()
            top_manufacturers = maker_volumes.nlargest(5).index
            
            # Filter for top manufacturers
            top_mfg_df = mfg_df[mfg_df['maker'].isin(top_manufacturers)]
            
            # Calculate YoY growth
            mfg_growth_data = []
            for maker in top_manufacturers:
                maker_data = top_mfg_df[top_mfg_df['maker'] == maker]
                for category in category_cols:
                    category_data = maker_data[maker_data['category'] == category].sort_values('year')
                    if len(category_data) > 1:  # Ensure we have at least 2 years for growth calculation
                        pct_change = category_data['total'].pct_change() * 100
                        for year, growth in zip(category_data['year'][1:], pct_change[1:]):
                            if not pd.isna(growth):  # Skip NaN values
                                mfg_growth_data.append({
                                    'maker': maker,
                                    'year': year,
                                    'category': category,
                                    'growth': growth
                                })
            
            mfg_growth_df = pd.DataFrame(mfg_growth_data)
            
            # Debug information
            if mfg_growth_df.empty:
                st.warning("No growth data available for the selected criteria")
            else:
                fig = px.bar(mfg_growth_df,
                            x='maker',
                            y='growth',
                            color='category',
                            title="YoY Growth by Top Manufacturers (%)",
                            barmode='group',
                            labels={'growth': 'Growth %', 'maker': 'Manufacturer', 'category': 'Category'})
                st.plotly_chart(fig, use_container_width=True, key="manufacturer_growth")
                
                # Show detailed growth numbers
                st.write("Detailed Growth Numbers (%)")
                pivot_growth = mfg_growth_df.pivot_table(
                    values='growth',
                    index='maker',
                    columns='category',
                    aggfunc='mean'
                ).round(2)
                st.dataframe(pivot_growth)
            st.plotly_chart(fig, use_container_width=True)
            
            # Investment Insights
            st.subheader("Investment Insights")
            
            # Calculate market leaders and growth leaders
            analysis_df['year'] = analysis_df['year'].astype(int)  # Convert year to integer
            latest_year = analysis_df['year'].max()
            current_year_data = analysis_df[analysis_df['year'] == latest_year]
            
            # Market share analysis
            market_share = current_year_data.groupby('maker')[category_cols].sum()
            market_share_pct = market_share.div(market_share.sum()) * 100
            
            # Growth leaders
            previous_year_data = analysis_df[analysis_df['year'] == latest_year - 1]
            
            # Make sure we have data for both years before calculating growth
            common_makers = set(current_year_data['maker']) & set(previous_year_data['maker'])
            
            if common_makers:
                current_totals = current_year_data[current_year_data['maker'].isin(common_makers)].groupby('maker')[category_cols].sum()
                previous_totals = previous_year_data[previous_year_data['maker'].isin(common_makers)].groupby('maker')[category_cols].sum()
                growth_comparison = (current_totals.sum(axis=1) / previous_totals.sum(axis=1) - 1) * 100
            else:
                growth_comparison = pd.Series(dtype=float)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Market Leaders (Current Year)")
                if not market_share_pct.empty:
                    market_leaders = market_share_pct.sum(axis=1).nlargest(5)
                    market_leaders_df = pd.DataFrame({
                        'Manufacturer': market_leaders.index,
                        'Market_Share': market_leaders.values
                    })
                    fig = px.pie(market_leaders_df,
                               values='Market_Share',
                               names='Manufacturer',
                               title="Top 5 Manufacturers by Market Share")
                    st.plotly_chart(fig, use_container_width=True, key="market_share_pie")
                else:
                    st.warning("No market share data available")
            
            with col2:
                st.write("Growth Leaders")
                if not growth_comparison.empty:
                    growth_leaders = growth_comparison.nlargest(5)
                    # Convert Series to DataFrame
                    growth_df = pd.DataFrame({
                        'Manufacturer': growth_leaders.index,
                        'Growth': growth_leaders.values
                    })
                    fig = px.bar(growth_df,
                               x='Manufacturer',
                               y='Growth',
                               title="Top 5 Manufacturers by YoY Growth (%)")
                    fig.update_layout(
                        xaxis_title="Manufacturer",
                        yaxis_title="Growth (%)"
                    )
                    st.plotly_chart(fig, use_container_width=True, key="growth_leaders_bar")
                else:
                    st.warning("No growth data available for comparison")
            
            # Raw data viewer
            if st.checkbox("Show Raw Data"):
                display_cols = ['year', 'month', 'quarter'] + category_cols
                st.dataframe(analysis_df[display_cols].sort_values(['year', 'month_order']))
    else:
        st.warning("No data available for the selected criteria")
else:
    st.info("Please select at least one year and one vehicle category to proceed")
