"""
Enhanced data processing script for comprehensive Vahan vehicle registration data.
Handles detailed vehicle categories, emission norms, fuel types, and financial year analysis.
"""
import pandas as pd
import numpy as np
from datetime import datetime
import json

def process_enhanced_data():
    """Process enhanced Vahan data with comprehensive categorization"""
    
    print("🔧 Processing Enhanced Vahan Dataset...")
    
    # Try to load the enhanced raw data first, fallback to creating sample
    try:
        df = pd.read_csv('data/raw_vahan_enhanced_data.csv')
        print(f"✅ Loaded raw enhanced data: {df.shape}")
    except FileNotFoundError:
        print("📊 Creating enhanced sample dataset...")
        df = create_comprehensive_sample_data()
    
    print(f"Original shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Enhanced data cleaning and processing
    if not df.empty:
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
        
        # Clean and validate registrations
        if 'registrations' in df.columns:
            df['registrations'] = pd.to_numeric(df['registrations'], errors='coerce').fillna(0)
        
        # Standardize categorical columns
        categorical_columns = ['vehicle_category', 'vehicle_class', 'manufacturer', 
                              'emission_norm', 'fuel_type', 'financial_year']
        
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
        
        # Add derived time columns
        if 'date' in df.columns:
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['month_name'] = df['date'].dt.strftime('%B')
            df['quarter_name'] = 'Q' + df['quarter'].astype(str)
        
        # Create vehicle type mapping for backward compatibility
        vehicle_type_mapping = {
            'TWO WHEELER': '2W',
            'THREE WHEELER': '3W', 
            'FOUR WHEELER': '4W',
            'LIGHT MOTOR VEHICLE': 'LMV',
            'MEDIUM MOTOR VEHICLE': 'MMV',
            'HEAVY MOTOR VEHICLE': 'HMV'
        }
        
        if 'vehicle_category' in df.columns:
            df['vehicle_type'] = df['vehicle_category'].map(vehicle_type_mapping).fillna(df['vehicle_category'])
        
        # Enhanced growth calculations
        df = calculate_enhanced_growth_metrics(df)
        
        # Calculate market share and additional metrics
        df = calculate_market_metrics(df)
        
        # Remove rows with missing critical data
        critical_columns = ['date', 'registrations']
        df = df.dropna(subset=critical_columns)
        
        # Sort by date for time series analysis
        df = df.sort_values(['vehicle_category', 'manufacturer', 'date'])
        
        print(f"✅ Enhanced data processing complete!")
        print(f"   Processed shape: {df.shape}")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Display enhanced statistics
        display_enhanced_statistics(df)
        
        # Save processed data
        save_processed_data(df)
        
    else:
        print("❌ No data to process")
    
    return df

def create_comprehensive_sample_data():
    """Create comprehensive sample data with all detailed categories"""
    import random
    from datetime import datetime, timedelta
    
    # Comprehensive data definitions
    financial_years = ['2022-23', '2023-24', '2024-25']
    
    # Detailed vehicle categories and classes
    vehicle_data = {
        'TWO WHEELER': {
            'classes': ['M-CYCLE/SCOOTER', 'MOPED', 'MOTORISED CYCLE (CC > 25CC)', 'M-CYCLE/SCOOTER-WITH SIDE CAR'],
            'manufacturers': ['Hero MotoCorp', 'Honda Motorcycle', 'Bajaj Auto', 'TVS Motor', 'Royal Enfield', 'Yamaha Motor'],
            'base_volume': (15000, 25000)
        },
        'THREE WHEELER': {
            'classes': ['THREE WHEELER (PERSONAL)', 'THREE WHEELER (PASSENGER)', 'THREE WHEELER (GOODS)', 'E-RICKSHAW(P)', 'E-RICKSHAW WITH CART (G)'],
            'manufacturers': ['Bajaj Auto', 'Mahindra', 'Piaggio', 'Atul Auto', 'TVS Motor'],
            'base_volume': (2000, 5000)
        },
        'FOUR WHEELER': {
            'classes': ['MOTOR CAR', 'LUXURY CAB', 'MOTOR CAB', 'MAXI CAB', 'PRIVATE SERVICE VEHICLE'],
            'manufacturers': ['Maruti Suzuki', 'Hyundai Motor', 'Tata Motors', 'Mahindra', 'Kia Motors', 'Honda Cars'],
            'base_volume': (8000, 15000)
        },
        'LIGHT MOTOR VEHICLE': {
            'classes': ['GOODS CARRIER', 'PRIVATE SERVICE VEHICLE', 'AMBULANCE', 'MOBILE CLINIC', 'CAMPER VAN / TRAILER'],
            'manufacturers': ['Tata Motors', 'Mahindra', 'Ashok Leyland', 'Force Motors', 'Isuzu'],
            'base_volume': (1000, 3000)
        },
        'MEDIUM MOTOR VEHICLE': {
            'classes': ['BUS', 'SCHOOL BUS', 'OMNI BUS', 'EDUCATIONAL INSTITUTION BUS'],
            'manufacturers': ['Tata Motors', 'Ashok Leyland', 'Mahindra', 'Volvo', 'BharatBenz'],
            'base_volume': (500, 1500)
        },
        'HEAVY MOTOR VEHICLE': {
            'classes': ['DUMPER', 'EXCAVATOR (COMMERCIAL)', 'TRAILER (COMMERCIAL)', 'CONSTRUCTION EQUIPMENT VEHICLE', 'ARTICULATED VEHICLE'],
            'manufacturers': ['Tata Motors', 'Ashok Leyland', 'Volvo', 'BharatBenz', 'Scania'],
            'base_volume': (200, 800)
        }
    }
    
    # Comprehensive emission norms and fuel types
    emission_norms = [
        'BHARAT STAGE VI', 'BHARAT STAGE IV', 'BHARAT STAGE III', 'EURO 6D', 'EURO 6C', 
        'EURO 6B', 'EURO 4', 'CEV STAGE IV', 'NOT APPLICABLE'
    ]
    
    fuel_types = [
        'PETROL', 'DIESEL', 'CNG ONLY', 'PURE EV', 'PETROL/CNG', 'DIESEL/HYBRID',
        'PETROL/HYBRID', 'LPG ONLY', 'ETHANOL', 'BIO-CNG/BIO-GAS', 'PLUG-IN HYBRID EV',
        'STRONG HYBRID EV', 'FUEL CELL HYDROGEN', 'SOLAR'
    ]
    
    enhanced_data = []
    
    for fy in financial_years:
        for month in range(1, 13):
            # Determine actual year based on financial year
            fy_start_year = int(fy.split('-')[0])
            if month <= 3:  # Jan-Mar of next year
                year = fy_start_year + 1
            else:  # Apr-Dec of current year
                year = fy_start_year
            
            date = datetime(year, month, 1)
            
            for category, category_data in vehicle_data.items():
                for vehicle_class in category_data['classes']:
                    for manufacturer in category_data['manufacturers']:
                        
                        # Random selection of norm and fuel based on category
                        if category in ['TWO WHEELER', 'THREE WHEELER']:
                            norm = random.choice(['BHARAT STAGE VI', 'BHARAT STAGE IV', 'NOT APPLICABLE'])
                            fuel = random.choice(['PETROL', 'CNG ONLY', 'PURE EV', 'PETROL/CNG'])
                        elif 'EV' in vehicle_class or 'E-RICKSHAW' in vehicle_class:
                            norm = 'NOT APPLICABLE'
                            fuel = 'PURE EV'
                        else:
                            norm = random.choice(emission_norms)
                            fuel = random.choice(fuel_types)
                        
                        # Generate registration numbers with realistic patterns
                        min_vol, max_vol = category_data['base_volume']
                        base_registrations = random.randint(min_vol, max_vol)
                        
                        # Apply growth factors
                        growth_factor = 1.0
                        if fy == '2023-24':
                            growth_factor = random.uniform(1.10, 1.25)  # 10-25% growth
                        elif fy == '2024-25':
                            growth_factor = random.uniform(1.15, 1.35)  # 15-35% growth
                        
                        # Seasonal variations
                        seasonal_factor = 1.0
                        if month in [3, 4, 10, 11]:  # Peak months
                            seasonal_factor = random.uniform(1.1, 1.3)
                        elif month in [6, 7, 8]:  # Monsoon slowdown
                            seasonal_factor = random.uniform(0.8, 0.95)
                        
                        registrations = int(base_registrations * growth_factor * seasonal_factor * random.uniform(0.85, 1.15))
                        
                        enhanced_data.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'financial_year': fy,
                            'vehicle_category': category,
                            'vehicle_class': vehicle_class,
                            'manufacturer': manufacturer,
                            'emission_norm': norm,
                            'fuel_type': fuel,
                            'registrations': registrations,
                            'month': date.strftime('%B'),
                            'quarter': f"Q{((month-1)//3)+1}",
                            'data_source': 'Enhanced_Sample_v2'
                        })
    
    print(f"✅ Created comprehensive sample data: {len(enhanced_data)} records")
    return pd.DataFrame(enhanced_data)

def calculate_enhanced_growth_metrics(df):
    """Calculate comprehensive growth metrics"""
    print("📈 Calculating enhanced growth metrics...")
    
    # Group by multiple dimensions
    grouping_cols = ['vehicle_category', 'manufacturer']
    if 'vehicle_class' in df.columns:
        grouping_cols.append('vehicle_class')
    
    # Sort data for time series calculations
    df = df.sort_values(grouping_cols + ['date'])
    
    # Financial Year-based Growth
    if 'financial_year' in df.columns:
        fy_data = df.groupby(grouping_cols + ['financial_year'])['registrations'].sum().reset_index()
        fy_data = fy_data.sort_values(grouping_cols + ['financial_year'])
        fy_data['fy_growth'] = fy_data.groupby(grouping_cols)['registrations'].pct_change() * 100
        df = df.merge(fy_data[grouping_cols + ['financial_year', 'fy_growth']], 
                     on=grouping_cols + ['financial_year'], how='left')
    
    # Monthly growth metrics
    df['yoy_growth'] = df.groupby(grouping_cols)['registrations'].pct_change(12) * 100
    df['qoq_growth'] = df.groupby(grouping_cols)['registrations'].pct_change(3) * 100
    df['mom_growth'] = df.groupby(grouping_cols)['registrations'].pct_change(1) * 100
    
    # Rolling averages - simplified approach
    try:
        for group_name, group_df in df.groupby(grouping_cols):
            group_df = group_df.sort_values('date')
            indices = group_df.index
            
            # 3-month rolling average
            rolling_3m = group_df['registrations'].rolling(window=3, min_periods=1).mean()
            df.loc[indices, 'registrations_3m_avg'] = rolling_3m.values
            
            # 6-month rolling average
            rolling_6m = group_df['registrations'].rolling(window=6, min_periods=1).mean()
            df.loc[indices, 'registrations_6m_avg'] = rolling_6m.values
            
    except Exception as e:
        print(f"Warning: Rolling averages calculation failed: {e}")
        df['registrations_3m_avg'] = df['registrations']
        df['registrations_6m_avg'] = df['registrations']
    
    return df

def calculate_market_metrics(df):
    """Calculate market share and competitive metrics"""
    print("📊 Calculating market metrics...")
    
    # Market share by category
    monthly_totals = df.groupby(['date', 'vehicle_category'])['registrations'].sum().reset_index()
    monthly_totals['total_monthly'] = monthly_totals.groupby('date')['registrations'].transform('sum')
    monthly_totals['market_share'] = (monthly_totals['registrations'] / monthly_totals['total_monthly']) * 100
    
    df = df.merge(monthly_totals[['date', 'vehicle_category', 'market_share']], 
                 on=['date', 'vehicle_category'], how='left')
    
    # Manufacturer market share within category
    mfg_share = df.groupby(['date', 'vehicle_category', 'manufacturer'])['registrations'].sum().reset_index()
    category_totals = mfg_share.groupby(['date', 'vehicle_category'])['registrations'].transform('sum')
    mfg_share['mfg_market_share'] = (mfg_share['registrations'] / category_totals) * 100
    
    df = df.merge(mfg_share[['date', 'vehicle_category', 'manufacturer', 'mfg_market_share']], 
                 on=['date', 'vehicle_category', 'manufacturer'], how='left')
    
    # Seasonal indicators
    df['is_peak_season'] = df['month'].isin([3, 4, 10, 11])
    df['is_festival_quarter'] = df['quarter'].isin([2, 4])
    
    return df

def display_enhanced_statistics(df):
    """Display comprehensive statistics about the processed data"""
    print(f"\n📊 Enhanced Dataset Statistics:")
    
    if 'vehicle_category' in df.columns:
        print(f"   Vehicle Categories: {df['vehicle_category'].nunique()}")
        category_counts = df['vehicle_category'].value_counts()
        for category, count in category_counts.head(5).items():
            print(f"     {category}: {count:,} records")
    
    if 'manufacturer' in df.columns:
        print(f"   Manufacturers: {df['manufacturer'].nunique()}")
        
    if 'emission_norm' in df.columns:
        print(f"   Emission Norms: {df['emission_norm'].nunique()}")
        norm_counts = df['emission_norm'].value_counts()
        for norm, count in norm_counts.head(3).items():
            print(f"     {norm}: {count:,} records")
    
    if 'fuel_type' in df.columns:
        print(f"   Fuel Types: {df['fuel_type'].nunique()}")
        fuel_counts = df['fuel_type'].value_counts()
        for fuel, count in fuel_counts.head(3).items():
            print(f"     {fuel}: {count:,} records")
    
    if 'financial_year' in df.columns:
        print(f"   Financial Years: {sorted(df['financial_year'].unique())}")
        fy_summary = df.groupby('financial_year')['registrations'].sum()
        for fy, total in fy_summary.items():
            print(f"     {fy}: {total:,} total registrations")

def save_processed_data(df):
    """Save processed data with metadata"""
    # Save main processed data
    processed_csv_path = 'data/processed_vahan_enhanced_data.csv'
    df.to_csv(processed_csv_path, index=False)
    print(f"✅ Enhanced processed data saved to {processed_csv_path}")
    
    # Save metadata
    metadata = {
        'processing_timestamp': datetime.now().isoformat(),
        'total_records': len(df),
        'data_columns': list(df.columns),
        'date_range': {
            'start': df['date'].min().isoformat() if 'date' in df.columns else None,
            'end': df['date'].max().isoformat() if 'date' in df.columns else None
        },
        'summary_stats': {
            'vehicle_categories': df['vehicle_category'].nunique() if 'vehicle_category' in df.columns else 0,
            'manufacturers': df['manufacturer'].nunique() if 'manufacturer' in df.columns else 0,
            'fuel_types': df['fuel_type'].nunique() if 'fuel_type' in df.columns else 0,
            'emission_norms': df['emission_norm'].nunique() if 'emission_norm' in df.columns else 0,
            'total_registrations': int(df['registrations'].sum()) if 'registrations' in df.columns else 0
        }
    }
    
    with open('data/processing_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f"📋 Processing metadata saved to data/processing_metadata.json")

if __name__ == "__main__":
    processed_df = process_enhanced_data()
    print(f"\n🎉 Enhanced data processing complete!")
    print(f"   Final dataset: {processed_df.shape}")
    print(f"   Ready for dashboard: streamlit run dashboard.py")
