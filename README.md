# Vahan Vehicle Registration Analysis Project

This project consists of two main components:
1. Vahan Data Scraper - Automated tool for scraping vehicle registration data
2. Interactive Dashboard - Data visualization and analysis platform

## Project Structure

```
assignment/
├── vahan scraper/             # Data scraping component
│   ├── vahan_scraper_main.py  # Main scraping script
│   ├── exceltodb.py          # Excel to SQLite converter
│   ├── dashboard.py          # Basic dashboard version
│   ├── dashboard_v2.py       # Enhanced dashboard version
│   └── data/                 # Database storage
│       └── vahan_data.db     # SQLite database
├── vahan dashboard with excel data/  # Excel-based dashboard
│   ├── create_database_v2.py # Database creation script
│   ├── dashboard_v3.py       # Dashboard for Excel data
│   └── data/                 # Excel data storage
│       ├── MARKER_MONTHWISE_2024.xlsx
│       └── VEHICILE_MONTH_2024.xlsx
```

## Features

### 1. Data Scraping (vahan scraper)
- Automated web scraping of vehicle registration data
- Intelligent handling of session management
- Excel data processing and database storage
- Logging and error handling

### 2. Interactive Dashboard (dashboard_v2.py)
- Clean, modern user interface
- Comprehensive vehicle registration analysis
- Year-over-Year (YoY) growth analysis
- Quarter-over-Quarter (QoQ) analysis
- Market share visualization
- Category-wise trends

### Vehicle Categories
- **2 Wheelers**
  - 2WN (2 Wheeler Non-Transport)
  - 2WT (2 Wheeler Transport)
- **3 Wheelers**
  - 3WN (3 Wheeler Non-Transport)
  - 3WT (3 Wheeler Transport)
- **4 Wheelers**
  - LMV (Light Motor Vehicle)
  - MMV (Medium Motor Vehicle)
  - HMV (Heavy Motor Vehicle)

## Setup Instructions

1. Install Required Dependencies:
```bash
pip install -r "vahan scraper/requirements.txt"
```

2. Database Setup:
- For scraper: Database is automatically created during scraping
- For Excel dashboard: Run `create_database_v2.py`

3. Running the Dashboard:
```bash
cd "vahan scraper"
streamlit run dashboard_v2.py
```

## Dashboard Features

1. **Overview Tab (📊)**
   - Total registration metrics
   - Category distribution
   - Top manufacturers analysis

2. **Market Analysis Tab (📈)**
   - Registration trends
   - Market share analysis
   - Monthly patterns

3. **Growth Metrics Tab (💹)**
   - YoY growth analysis
   - Category growth trends
   - Quarterly performance

## Data Sources

1. **Scraper Data**
   - Real-time data from Vahan portal
   - Stored in SQLite database
   - Automated updates

2. **Excel Data**
   - Monthly marker data
   - Vehicle registration data
   - Pre-processed datasets

## Investment Insights

The dashboard provides valuable investment insights:
1. Market leader identification
2. Growth trend analysis
3. Category-wise performance
4. Seasonal patterns
5. Market share evolution

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Vahan portal for data availability
- Streamlit for dashboard framework
- Contributors and maintainers

## Support

For support, please open an issue in the repository or contact the maintainers.
