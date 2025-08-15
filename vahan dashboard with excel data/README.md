# Vahan Dashboard with Excel Data

This component provides dashboard functionality using pre-processed Excel data files.

## Files Description

- `create_database_v2.py`: Database creation from Excel files
- `dashboard_v3.py`: Dashboard implementation for Excel data
- `vahan_data.db`: SQLite database for processed data

## Data Files

### 1. MARKER_MONTHWISE_2024.xlsx
- Monthly marker data
- Time series information
- Category-wise breakdowns

### 2. VEHICILE_MONTH_2024.xlsx
- Vehicle registration data
- Manufacturer information
- Monthly aggregations

## Setup Instructions

1. Database Creation:
```bash
python create_database_v2.py
```

2. Launch Dashboard:
```bash
streamlit run dashboard_v3.py
```

## Data Processing

The `create_database_v2.py` script:
1. Reads Excel files
2. Processes and cleans data
3. Creates SQLite database
4. Performs data validation

## Dashboard Features

The dashboard provides:
1. Interactive visualizations
2. Time series analysis
3. Category-wise breakdown
4. Market share analysis

## Data Categories

### Vehicle Types
- 2 Wheelers (Transport & Non-Transport)
- 3 Wheelers (Transport & Non-Transport)
- 4 Wheelers (LMV, MMV, HMV)

### Analysis Metrics
- Registration counts
- Growth rates
- Market share
- Seasonal patterns
