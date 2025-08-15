import pandas as pd
import warnings
import sqlite3
from pathlib import Path
import re
import os

# Suppress the openpyxl warning about default styles
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Global path setup
base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
data_dir = base_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)
db_path = data_dir / "vahan_data.db"

def create_db_and_table():
    """Create SQLite database and table if they don't exist"""
    global db_path
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create table with all the columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicle_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT,
        year TEXT,
        maker TEXT,
        twic INTEGER,  -- 2WIC
        twn INTEGER,   -- 2WN
        twt INTEGER,   -- 2WT
        thwic INTEGER, -- 3WIC
        thwn INTEGER,  -- 3WN
        thwt INTEGER,  -- 3WT
        fwic INTEGER,  -- 4WIC
        hgv INTEGER,   -- HGV
        hmv INTEGER,   -- HMV
        hpv INTEGER,   -- HPV
        lgv INTEGER,   -- LGV
        lmv INTEGER,   -- LMV
        lpv INTEGER,   -- LPV
        mgv INTEGER,   -- MGV
        mmv INTEGER,   -- MMV
        mpv INTEGER,   -- MPV
        oth INTEGER,   -- OTH
        total INTEGER  -- TOTAL
    )
    ''')
    
    # Create index on month and year for faster queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_month_year 
    ON vehicle_data (month, year)
    ''')
    
    conn.commit()
    return conn

def check_data_exists(cursor, month, year):
    """Check if data for given month and year already exists"""
    cursor.execute('''
        SELECT COUNT(*) FROM vehicle_data 
        WHERE month = ? AND year = ?
    ''', (month, year))
    count = cursor.fetchone()[0]
    return count > 0

def storeindb(df, month, year):
    """Store DataFrame in SQLite database with month and year"""
    try:
        conn = create_db_and_table()
        cursor = conn.cursor()
        
        # Check if data already exists
        if check_data_exists(cursor, month, year):
            print(f"Data for {month} {year} already exists in database. Skipping...")
            return
        
        # Convert column names to match database schema
        column_mapping = {
            'Maker': 'maker',
            '2WIC': 'twic',
            '2WN': 'twn',
            '2WT': 'twt',
            '3WIC': 'thwic',
            '3WN': 'thwn',
            '3WT': 'thwt',
            '4WIC': 'fwic',
            'HGV': 'hgv',
            'HMV': 'hmv',
            'HPV': 'hpv',
            'LGV': 'lgv',
            'LMV': 'lmv',
            'LPV': 'lpv',
            'MGV': 'mgv',
            'MMV': 'mmv',
            'MPV': 'mpv',
            'OTH': 'oth',
            'TOTAL': 'total'
        }
        
        # Set DataFrame columns to match the database schema (excluding id, month, year)
        df.columns = [
            'sno','maker', 'twic', 'twn', 'twt', 'thwic', 'thwn', 'thwt', 'fwic',
            'hgv', 'hmv', 'hpv', 'lgv', 'lmv', 'lpv', 'mgv', 'mmv', 'mpv',
            'oth', 'total'
        ]
        
        # Convert any non-numeric values to 0
        numeric_columns = list(column_mapping.values())
        numeric_columns.remove('maker')  # Exclude the maker column
        for col in numeric_columns:
            if col in df.columns:
                # Remove commas and convert to numeric
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Add month and year columns
        df['month'] = month
        df['year'] = year
        
        # Insert data into database
        for _, row in df.iterrows():
            cursor.execute('''
            INSERT INTO vehicle_data (
                month, year, maker, twic, twn, twt, thwic, thwn, thwt,
                fwic, hgv, hmv, hpv, lgv, lmv, lpv, mgv, mmv, mpv, oth, total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['month'], row['year'], row['maker'],
                row['twic'], row['twn'], row['twt'],
                row['thwic'], row['thwn'], row['thwt'],
                row['fwic'], row['hgv'], row['hmv'], row['hpv'],
                row['lgv'], row['lmv'], row['lpv'], row['mgv'],
                row['mmv'], row['mpv'], row['oth'], row['total']
            ))
        
        conn.commit()
        print(f"Successfully stored data for {month} {year} in database")
        print(f"Added {len(df)} records")
        
        print(f"Successfully stored {len(df)} records for {month} {year} in database")
        
    except Exception as e:
        print(f"Error storing data in database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def query_data(month=None, year=None, maker=None):
    """Query data from the database with optional filters"""
    global db_path
    conn = sqlite3.connect(str(db_path))
    try:
        query = "SELECT * FROM vehicle_data WHERE 1=1"
        params = []
        
        if month:
            query += " AND month = ?"
            params.append(month)
        if year:
            query += " AND year = ?"
            params.append(year)
        if maker:
            query += " AND maker LIKE ?"
            params.append(f"%{maker}%")
            
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()

def get_summary_stats():
    """Get summary statistics from the database"""
    global db_path
    conn = sqlite3.connect(str(db_path))
    try:
        # Total vehicles by year
        yearly_stats = pd.read_sql_query('''
            SELECT year, 
                   SUM(total) as total_vehicles,
                   COUNT(DISTINCT maker) as unique_makers,
                   SUM(twic + twn + twt) as total_2w,
                   SUM(thwic + thwn + thwt) as total_3w,
                   SUM(fwic + lmv + mmv + hmv) as total_4w
            FROM vehicle_data 
            GROUP BY year
            ORDER BY year DESC
        ''', conn)
        
        # Top makers by total vehicles
        top_makers = pd.read_sql_query('''
            SELECT maker, 
                   SUM(total) as total_vehicles
            FROM vehicle_data 
            GROUP BY maker
            ORDER BY total_vehicles DESC
            LIMIT 10
        ''', conn)
        
        return {
            'yearly_stats': yearly_stats,
            'top_makers': top_makers
        }
    finally:
        conn.close()

def process_excel_file(file_path):
    """Process a single Excel file and store its data in the database"""
    try:
        print(f"\nProcessing file: {file_path.name}")
        
        # Read the Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Extract month and year from the first column name
        first_col = df.columns[0]
        match = re.search(r'\((\w+),(\d{4})\)', first_col)
        if match:
            month = match.group(1)
            year = match.group(2)
            print(f"Found data for Month: {month}, Year: {year}")
            
            # Skip header rows and store in database
            df = df[3:]
            storeindb(df, month, year)
            return True
        else:
            print(f"Warning: Month and year not found in {file_path.name}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return False

def main():
    try:
        # Use Path for better path handling
        downloads_dir = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads"))
        
        if not downloads_dir.exists():
            raise FileNotFoundError(f"Downloads directory not found at {downloads_dir}")
        
        # Get all Excel files in the downloads directory
        excel_files = list(downloads_dir.glob("*.xls*"))  # This will get both .xls and .xlsx files
        
        if not excel_files:
            print("No Excel files found in downloads directory")
            return
            
        print(f"Found {len(excel_files)} Excel files to process")
        
        # Process each Excel file
        successful_files = 0
        for file_path in excel_files:
            if process_excel_file(file_path):
                successful_files += 1
                
        print(f"\nProcessing complete!")
        print(f"Successfully processed {successful_files} out of {len(excel_files)} files")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()