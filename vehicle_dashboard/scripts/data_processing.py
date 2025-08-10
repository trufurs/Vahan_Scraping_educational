"""
Script for cleaning and processing Vahan vehicle registration data.
"""
import pandas as pd
import numpy as np

def process_data(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # Example cleaning: drop empty columns, rename, convert dates
    df = df.dropna(axis=1, how='all')
    # Assume columns: ['Date', 'Vehicle_Type', 'Manufacturer', 'Registrations']
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['registrations'] = pd.to_numeric(df['registrations'], errors='coerce').fillna(0)

    # Calculate YoY and QoQ growth
    df = df.sort_values('date')
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.to_period('Q')

    # YoY Growth
    df['yoy_growth'] = df.groupby(['vehicle_type', 'manufacturer'])['registrations'].pct_change(12) * 100
    # QoQ Growth
    df['qoq_growth'] = df.groupby(['vehicle_type', 'manufacturer'])['registrations'].pct_change(3) * 100

    df.to_csv(output_csv, index=False)
    print(f"Processed data saved to {output_csv}")

if __name__ == "__main__":
    process_data("../data/raw_vahan_data.csv", "../data/processed_vahan_data.csv")
