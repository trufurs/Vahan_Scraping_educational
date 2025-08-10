"""
Demo script to showcase the Vahan Dashboard capabilities
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def analyze_data():
    """Analyze the processed data and generate insights"""
    print("🚗 Vahan Vehicle Registration Dashboard - Data Analysis")
    print("=" * 60)
    
    # Load processed data
    try:
        df = pd.read_csv('data/processed_vahan_data.csv', parse_dates=['date'])
        print(f"✅ Data loaded successfully: {df.shape[0]} records")
    except FileNotFoundError:
        print("❌ Processed data not found. Run setup.py first.")
        return
    
    # Basic statistics
    print(f"📅 Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"🏭 Vehicle types: {', '.join(df['vehicle_type'].unique())}")
    print(f"🏢 Manufacturers: {', '.join(df['manufacturer'].unique())}")
    
    # KPI calculations
    total_registrations = df['registrations'].sum()
    avg_yoy_growth = df['yoy_growth'].mean()
    avg_qoq_growth = df['qoq_growth'].mean()
    
    print(f"\n📊 Key Performance Indicators:")
    print(f"   Total Registrations: {total_registrations:,}")
    print(f"   Average YoY Growth: {avg_yoy_growth:.2f}%")
    print(f"   Average QoQ Growth: {avg_qoq_growth:.2f}%")
    
    # Top performers
    manufacturer_totals = df.groupby('manufacturer')['registrations'].sum().sort_values(ascending=False)
    vehicle_totals = df.groupby('vehicle_type')['registrations'].sum().sort_values(ascending=False)
    
    print(f"\n🏆 Top Manufacturers by Volume:")
    for i, (manufacturer, volume) in enumerate(manufacturer_totals.head(3).items(), 1):
        print(f"   {i}. {manufacturer}: {volume:,}")
    
    print(f"\n🚗 Vehicle Type Performance:")
    for vehicle_type, volume in vehicle_totals.items():
        print(f"   {vehicle_type}: {volume:,}")
    
    # Growth analysis
    yoy_by_manufacturer = df.groupby('manufacturer')['yoy_growth'].mean().sort_values(ascending=False)
    print(f"\n📈 Highest YoY Growth:")
    for i, (manufacturer, growth) in enumerate(yoy_by_manufacturer.head(3).items(), 1):
        if not pd.isna(growth):
            print(f"   {i}. {manufacturer}: {growth:.2f}%")
    
    # Investment insights
    print(f"\n💡 Investment Insights:")
    top_growth_manufacturer = yoy_by_manufacturer.index[0]
    top_growth_value = yoy_by_manufacturer.iloc[0]
    dominant_vehicle_type = vehicle_totals.index[0]
    
    print(f"   🚀 Growth Leader: {top_growth_manufacturer} ({top_growth_value:.2f}% YoY)")
    print(f"   👑 Market Dominant: {dominant_vehicle_type} segment")
    
    trend = "Growing 📈" if avg_yoy_growth > 0 else "Declining 📉"
    print(f"   📊 Market Trend: {trend}")
    
    print(f"\n🎯 Recommendation:")
    if avg_yoy_growth > 5:
        print("   Strong growth market - Consider increased investment")
    elif avg_yoy_growth > 0:
        print("   Moderate growth - Stable investment opportunity")
    else:
        print("   Declining market - Exercise caution")

if __name__ == "__main__":
    analyze_data()
