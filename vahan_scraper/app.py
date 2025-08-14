import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import VahanScraper
import os
import time
from datetime import datetime

st.set_page_config(page_title="Vahan Dashboard Scraper", layout="wide")

def load_existing_data():
    """Load existing scraped data if available."""
    csv_path = os.path.join("data", "vahan_data.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

def create_visualizations(df):
    """Create visualizations from the scraped data."""
    st.header("Data Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vehicle type distribution
        fig1 = px.pie(df, names='vehicle_type', title='Distribution by Vehicle Type')
        st.plotly_chart(fig1)
        
        # Monthly trend
        monthly_data = df.groupby(['year', 'month']).size().reset_index(name='count')
        fig2 = px.line(monthly_data, x='month', y='count', color='year', 
                       title='Monthly Registration Trends')
        st.plotly_chart(fig2)
    
    with col2:
        # Manufacturer distribution
        fig3 = px.bar(df.groupby('manufacturer').size().reset_index(name='count'),
                      x='manufacturer', y='count', title='Registrations by Manufacturer')
        st.plotly_chart(fig3)
        
        # Vehicle type by manufacturer
        pivot_data = df.pivot_table(
            index='manufacturer', 
            columns='vehicle_type',
            aggfunc='size',
            fill_value=0
        ).reset_index()
        
        fig4 = px.bar(pivot_data, x='manufacturer', y=['2W', '3W', '4W'],
                      title='Vehicle Types by Manufacturer')
        st.plotly_chart(fig4)

def main():
    st.title("Vahan Dashboard Data Scraper")
    
    st.markdown("""
    This application scrapes vehicle registration data from the Vahan Dashboard.
    You can start a new scraping session or view existing data.
    """)
    
    # Initialize session state
    if 'scraping_complete' not in st.session_state:
        st.session_state.scraping_complete = False
    
    # Sidebar
    st.sidebar.header("Controls")
    
    if st.sidebar.button("Start New Scraping Session"):
        st.sidebar.warning("Scraping in progress... This may take a while.")
        
        try:
            scraper = VahanScraper()
            scraper.scrape()
            st.session_state.scraping_complete = True
            st.sidebar.success("Scraping completed successfully!")
            
        except Exception as e:
            st.sidebar.error(f"An error occurred: {str(e)}")
            
    # View existing data
    st.header("Scraped Data")
    
    df = load_existing_data()
    if df is not None:
        st.write(f"Total records: {len(df)}")
        
        # Data filters
        st.subheader("Data Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            vehicle_type = st.multiselect(
                "Vehicle Type",
                options=sorted(df['vehicle_type'].unique()),
                default=sorted(df['vehicle_type'].unique())
            )
        
        with col2:
            manufacturer = st.multiselect(
                "Manufacturer",
                options=sorted(df['manufacturer'].unique()),
                default=sorted(df['manufacturer'].unique())
            )
        
        with col3:
            year = st.multiselect(
                "Year",
                options=sorted(df['year'].unique()),
                default=sorted(df['year'].unique())
            )
        
        # Filter data
        filtered_df = df[
            (df['vehicle_type'].isin(vehicle_type)) &
            (df['manufacturer'].isin(manufacturer)) &
            (df['year'].isin(year))
        ]
        
        # Show filtered data
        st.subheader("Filtered Data")
        st.dataframe(filtered_df)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"vahan_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Create visualizations
        create_visualizations(filtered_df)
        
    else:
        st.info("No data available. Click 'Start New Scraping Session' to begin scraping.")
    
    # Show raw HTML files
    st.header("Raw HTML Responses")
    raw_files = os.listdir("raw_responses") if os.path.exists("raw_responses") else []
    if raw_files:
        st.write(f"Number of raw HTML files: {len(raw_files)}")
        if st.checkbox("Show raw HTML filenames"):
            st.write(raw_files)
    else:
        st.info("No raw HTML files available yet.")

if __name__ == "__main__":
    main()
