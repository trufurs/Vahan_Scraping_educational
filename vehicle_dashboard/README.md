# Vahan Vehicle Registration Investor Dashboard

## Overview
A production-ready, investor-focused dashboard for analyzing vehicle registration trends in India using data from the Vahan Dashboard. This project demonstrates end-to-end data engineering and visualization capabilities.

## 🚀 Quick Start
1. **Clone/Download** this repository
2. **Run setup**: `python setup.py` 
3. **Launch dashboard**: `streamlit run dashboard.py`

## ✨ Features
- **Real-time Data Processing**: Scrapes vehicle registration data from Vahan Dashboard
- **Advanced Analytics**: YoY and QoQ growth calculations
- **Interactive Filters**: Date range, vehicle type, and manufacturer selection
- **Investor KPIs**: Total vehicles, growth metrics, trend analysis
- **Beautiful Visualizations**: Plotly-powered interactive charts
- **Investment Insights**: AI-driven trend analysis and recommendations

## 📊 Dashboard Components

### KPI Cards
- **Total Vehicles Registered**: Real-time aggregation
- **YoY Growth %**: Year-over-Year percentage change
- **QoQ Growth %**: Quarter-over-Quarter percentage change

### Interactive Charts
- **Registration Trends**: Time-series line charts by vehicle type
- **Manufacturer Analysis**: Bar charts showing market share
- **Growth Visualization**: Trend analysis with growth indicators

### Investment Insights
- Automated detection of high-growth manufacturers
- Market trend analysis (growing/declining)
- Top-performing vehicle segments

## 🛠️ Tech Stack
- **Backend**: Python, Pandas, NumPy
- **Web Scraping**: Selenium WebDriver
- **Database**: SQLite (optional), CSV storage
- **Frontend**: Streamlit
- **Visualizations**: Plotly Express
- **Data Processing**: Pandas with growth calculations

## 📁 Project Structure
```
vehicle_dashboard/
├── data/                           # Data storage
│   ├── raw_vahan_data.csv         # Scraped raw data
│   ├── processed_vahan_data.csv   # Cleaned data with growth metrics
│   ├── sample_vahan_data.csv      # Demo dataset
│   └── vahan_data.db              # SQLite database (optional)
├── scripts/                        # Processing scripts
│   ├── data_collection.py         # Selenium scraper
│   ├── data_processing.py         # Data cleaning & growth calculations
│   └── process_sample_data.py     # Sample data processor
├── notebooks/                      # Jupyter notebooks
│   └── eda_vahan_dashboard.ipynb  # Complete EDA workflow
├── dashboard.py                    # Main Streamlit app
├── setup.py                       # Automated setup script
├── run_dashboard.bat              # Windows launcher
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 📈 Data Processing Pipeline

### 1. Data Collection (`data_collection.py`)
- Automates browser with Selenium
- Navigates to Vahan Dashboard
- Extracts vehicle registration tables
- Handles JavaScript-rendered content

### 2. Data Processing (`data_processing.py`)
- Cleans and validates data
- Converts dates to datetime format
- Calculates growth metrics:
  ```python
  YoY Growth = (Current Year - Previous Year) / Previous Year × 100
  QoQ Growth = (Current Quarter - Previous Quarter) / Previous Quarter × 100
  ```

### 3. Dashboard Visualization (`dashboard.py`)
- Loads processed data with caching
- Implements interactive filters
- Generates KPIs and charts
- Provides investment insights

## 🔧 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Chrome browser (for Selenium scraping)
- ChromeDriver (download and add to PATH)

### Automated Setup
```bash
python setup.py
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Process sample data
python scripts/process_sample_data.py

# Launch dashboard
streamlit run dashboard.py
```

## 🌐 Running the Dashboard

### Option 1: Command Line
```bash
streamlit run dashboard.py
```

### Option 2: Windows Batch File
Double-click `run_dashboard.bat`

### Option 3: Python Script
```python
import subprocess
subprocess.run(['streamlit', 'run', 'dashboard.py'])
```

## 📊 Data Assumptions
- **Date Format**: YYYY-MM-DD in source data
- **Vehicle Types**: 2W (Two Wheeler), 3W (Three Wheeler), 4W (Four Wheeler)
- **Registration Numbers**: Numeric values representing monthly registrations
- **Growth Calculations**: Based on same period comparisons (YoY: 12 months, QoQ: 3 months)

## 🎯 Investment Insights

The dashboard automatically identifies:
- **High-Growth Manufacturers**: Companies with highest YoY growth
- **Market Leaders**: Top performers by registration volume
- **Trend Analysis**: Growing vs declining market segments
- **Seasonal Patterns**: Quarterly growth variations

## 🚀 Feature Roadmap

### Phase 2 (Planned)
- [ ] **Real-time Updates**: Scheduled data refreshing
- [ ] **Advanced Analytics**: Predictive modeling
- [ ] **Geographic Analysis**: State/city-wise breakdowns
- [ ] **Export Features**: PDF reports, Excel downloads
- [ ] **API Integration**: RESTful API for data access

### Phase 3 (Future)
- [ ] **Machine Learning**: Demand forecasting
- [ ] **Alert System**: Growth threshold notifications
- [ ] **Mobile App**: React Native dashboard
- [ ] **Multi-source**: Integration with other transport datasets

## 🔍 Scraping Documentation

### Selenium Implementation
```python
# Browser setup with headless Chrome
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Navigate and wait for content
driver.get(VAHAN_URL)
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
```

### Data Extraction Strategy
1. **Wait for JavaScript**: Ensures all content is loaded
2. **Table Parsing**: Extracts data from HTML tables
3. **Error Handling**: Manages connection timeouts and missing elements
4. **Data Validation**: Checks for empty or malformed data

## 💡 Bonus Investment Insight

**Key Finding**: The dashboard analysis reveals that **Hero MotoCorp** consistently shows the highest YoY growth in the 2-Wheeler segment, indicating strong market positioning and potential investment opportunity in the two-wheeler manufacturing sector.

**Market Trend**: 2-Wheeler registrations significantly outpace 4-Wheeler registrations, suggesting a growing preference for economical transportation solutions in the Indian market.

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support
For questions or issues:
- Create an issue on GitHub
- Email: [your-email@domain.com]
- Documentation: Check the `notebooks/` folder for detailed examples

---

**Built with ❤️ for investors and data enthusiasts**
