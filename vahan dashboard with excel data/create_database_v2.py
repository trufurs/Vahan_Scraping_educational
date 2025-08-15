import sqlite3
import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Vehicle categories mapping
VEHICLE_CATEGORIES = {
    '4W': [
        'MOTOR CAB',
        'MOTOR CAR',
        'OMNI BUS (PRIVATE USE)',
        'PRIVATE SERVICE VEHICLE (INDIVIDUAL USE)',
        'QUADRICYCLE (PRIVATE)'
    ],
    '3W': [
        'E-RICKSHAW(P)',
        'E-RICKSHAW WITH CART (G)',
        'THREE WHEELER (GOODS)',
        'THREE WHEELER (PASSENGER)',
        'THREE WHEELER (PERSONAL)'
    ],
    '2W': [
        'M-CYCLE/SCOOTER',
        'M-CYCLE/SCOOTER-WITH SIDE CAR',
        'MOPED',
        'MOTOR CYCLE/SCOOTER-SIDECAR(T)',
        'MOTOR CYCLE/SCOOTER-USED FOR HIRE',
        'MOTOR CYCLE/SCOOTER-WITH TRAILER',
        'MOTORISED CYCLE (CC > 25CC)'
    ]
}

def create_database():
    """Create the SQLite database with two separate tables"""
    conn = sqlite3.connect('vahan_data.db')
    c = conn.cursor()
    
    # Create vehicle class registrations table
    c.execute('''
    CREATE TABLE IF NOT EXISTS vehicle_class_registrations (
        id INTEGER PRIMARY KEY,
        vehicle_class TEXT NOT NULL,
        category TEXT NOT NULL,  -- '2W', '3W', '4W'
        year INTEGER,
        month INTEGER,
        registrations INTEGER,
        UNIQUE(vehicle_class, year, month)
    )
    ''')
    
    # Create manufacturer registrations table
    c.execute('''
    CREATE TABLE IF NOT EXISTS manufacturer_registrations (
        id INTEGER PRIMARY KEY,
        manufacturer TEXT NOT NULL,
        year INTEGER,
        month INTEGER,
        registrations INTEGER,
        UNIQUE(manufacturer, year, month)
    )
    ''')
    
    conn.commit()
    return conn

def clean_numeric_value(value):
    """Clean numeric values by removing commas and converting to integer"""
    if pd.isna(value):
        return 0
    try:
        # Remove commas and convert to integer
        cleaned_value = str(value).replace(',', '').strip()
        return int(cleaned_value) if cleaned_value else 0
    except (ValueError, TypeError):
        logging.warning(f"Invalid numeric value: '{value}', setting to 0")
        return 0

def process_vehicle_class_file(conn, excel_path, year):
    """Process vehicle class data file"""
    logging.info(f"Processing vehicle class data from {excel_path} for year {year}")
    
    try:
        # Read Excel with string dtype to preserve original values
        df = pd.read_excel(excel_path, dtype=str)
        df.columns = df.columns.str.strip()  # Strip whitespace from column names
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        c = conn.cursor()
        
        # Get category mapping
        vehicle_class_mapping = {}
        for category, classes in VEHICLE_CATEGORIES.items():
            for vehicle_class in classes:
                vehicle_class_mapping[vehicle_class] = category
        
        # Process each row
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        
        for _, row in df.iterrows():
            vehicle_class = row.get('Vehicle Class', '').strip()
            if not vehicle_class or vehicle_class not in vehicle_class_mapping:
                logging.warning(f"Skipping unknown vehicle class: {vehicle_class}")
                continue
            
            category = vehicle_class_mapping[vehicle_class]
            
            # Process monthly data
            for month_num, month_name in enumerate(months, 1):
                quantity = clean_numeric_value(row.get(month_name, 0))
                
                c.execute('''
                INSERT OR REPLACE INTO vehicle_class_registrations 
                (vehicle_class, category, year, month, registrations)
                VALUES (?, ?, ?, ?, ?)
                ''', (vehicle_class, category, year, month_num, quantity))
        
        conn.commit()
        logging.info(f"Successfully processed vehicle class data for {year}")
        
    except Exception as e:
        logging.error(f"Error processing vehicle class data: {str(e)}")
        raise

def process_manufacturer_file(conn, excel_path, year):
    """Process manufacturer data file"""
    logging.info(f"Processing manufacturer data from {excel_path} for year {year}")
    
    try:
        # Read Excel with string dtype to preserve original values
        df = pd.read_excel(excel_path, dtype=str)
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df.columns = df.columns.str.strip()  # Strip whitespace from column names
        c = conn.cursor()
        
        # Process each row
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        
        for _, row in df.iterrows():
            manufacturer = row.get('Maker', '').strip()
            if not manufacturer:
                logging.warning("Skipping row with no manufacturer")
                continue
            
            # Process monthly data
            for month_num, month_name in enumerate(months, 1):
                quantity = clean_numeric_value(row.get(month_name, 0))
                
                c.execute('''
                INSERT OR REPLACE INTO manufacturer_registrations 
                (manufacturer, year, month, registrations)
                VALUES (?, ?, ?, ?)
                ''', (manufacturer, year, month_num, quantity))
        
        conn.commit()
        logging.info(f"Successfully processed manufacturer data for {year}")
        
    except Exception as e:
        logging.error(f"Error processing manufacturer data: {str(e)}")
        raise

def process_year_data(conn, data_dir, year):
    """Process both data files for a specific year"""
    processed = False
    
    # Process vehicle class data
    vehicle_file = data_dir / f'VEHICILE_MONTH_{year}.xlsx'
    if vehicle_file.exists():
        process_vehicle_class_file(conn, vehicle_file, year)
        processed = True
        logging.info(f"Successfully processed vehicle class data for {year}")
    else:
        logging.warning(f"Vehicle class file not found for year {year}")
    
    # Process manufacturer data
    maker_file = data_dir / f'MARKER_MONTHWISE_{year}.xlsx'
    if maker_file.exists():
        process_manufacturer_file(conn, maker_file, year)
        processed = True
        logging.info(f"Successfully processed manufacturer data for {year}")
    else:
        logging.warning(f"Manufacturer file not found for year {year}")
    
    if not processed:
        logging.error(f"No data files found for year {year}")
        raise FileNotFoundError(f"No data files found for year {year}")

def main():
    try:
        # Create database and tables
        logging.info("Creating/connecting to database")
        conn = create_database()
        
        # Process data files
        data_dir = Path(__file__).parent / 'data'
        
        # Process available years
        years = [2024]  # Add more years as needed
        
        for year in years:
            logging.info(f"Processing data for year {year}")
            process_year_data(conn, data_dir, year)
        
        logging.info("Database creation completed successfully")
        
    except Exception as e:
        logging.error(f"Error in database creation: {str(e)}")
        raise
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
