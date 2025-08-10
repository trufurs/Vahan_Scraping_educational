"""
Script for processing sample vehicle registration data with YoY and QoQ calculations.
"""
import pandas as pd
import numpy as np

def process_sample_data():
    # Load sample data
    df = pd.read_csv('data/sample_vahan_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Add year and quarter columns
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.to_period('Q')
    
    # Calculate YoY growth (12 months)
    df['yoy_growth'] = df.groupby(['vehicle_type', 'manufacturer'])['registrations'].pct_change(12) * 100
    
    # Calculate QoQ growth (3 months) 
    df['qoq_growth'] = df.groupby(['vehicle_type', 'manufacturer'])['registrations'].pct_change(3) * 100
    
    # Save processed data
    df.to_csv('data/processed_vahan_data.csv', index=False)
    print("Sample data processed and saved to data/processed_vahan_data.csv")
    print(f"Data shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Vehicle types: {df['vehicle_type'].unique()}")
    print(f"Manufacturers: {df['manufacturer'].unique()}")

if __name__ == "__main__":
    process_sample_data()
