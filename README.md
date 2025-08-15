# Vahan Vehicle Registration Analysis Project

A comprehensive solution for scraping, analyzing, and visualizing vehicle registration data from the Vahan portal.

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for web scraping)
- Git (for version control)

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/trufurs/Vahan_Scraping_educational.git
cd Vahan_Scraping_educational

# Create and activate virtual environment
python -m venv venv
# For Windows
.\venv\Scripts\activate
# For Unix/MacOS
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# For Scraper
cd "vahan scraper"
pip install -r requirements.txt

# For Dashboard
pip install streamlit pandas plotly sqlite3
```

### 3. Chrome WebDriver Setup
- Download ChromeDriver matching your Chrome version
- Place the executable in the `vahan scraper` directory
- Or add to system PATH

### 4. Database Setup
```bash
# For scraped data
python exceltodb.py

# For Excel data
cd "../vahan dashboard with excel data"
python create_database_v2.py
```

### 5. Running the Dashboard
```bash
cd "../vahan scraper"
streamlit run dashboard_v2.py
```

## 📊 Data Assumptions

### 1. Data Structure
- Vehicle categories are predefined (2W, 3W, 4W)
- Each category has subcategories:
  ```
  2W: 2WN (Non-Transport), 2WT (Transport)
  3W: 3WN (Non-Transport), 3WT (Transport)
  4W: LMV, MMV, HMV
  ```
- Manufacturers are consistently named across periods
- Timestamps follow YYYY-MM format

### 2. Data Quality
- No duplicate entries for same vehicle/month
- Non-negative registration numbers
- No missing values in critical fields
- Month names are in uppercase (JAN, FEB, etc.)

### 3. Time Series
- Monthly data is sequential
- No gaps in monthly data
- Years are complete (all 12 months)
- Latest data is current year

### 4. Database
- SQLite database for storage
- Single database file per dataset
- Tables maintain referential integrity
- Backup files are maintained

## 🎯 Feature Roadmap

### Phase 1: Enhanced Data Collection (Q3 2025)
- [ ] Multi-threaded scraping
- [ ] Proxy rotation support
- [ ] Automated CAPTCHA handling
- [ ] Rate limiting and retry mechanisms
- [ ] Data validation pipeline

### Phase 2: Advanced Analytics (Q4 2025)
- [ ] Machine learning predictions
- [ ] Seasonal trend analysis
- [ ] Manufacturer performance scoring
- [ ] Market segment analysis
- [ ] Competition analysis dashboard

### Phase 3: Enhanced Visualization (Q1 2026)
- [ ] Interactive map visualizations
- [ ] Custom report generator
- [ ] PDF export functionality
- [ ] Real-time updates
- [ ] Mobile-responsive design

### Phase 4: Enterprise Features (Q2 2026)
- [ ] Multi-user support
- [ ] Role-based access control
- [ ] API integration
- [ ] Data export in multiple formats
- [ ] Automated reporting system

### Phase 5: Integration & Optimization (Q3 2026)
- [ ] Cloud database integration
- [ ] Performance optimization
- [ ] Automated testing suite
- [ ] CI/CD pipeline
- [ ] Documentation generation

## 🔄 Maintenance Plan

### Regular Updates
- Weekly data synchronization
- Monthly performance optimization
- Quarterly feature releases
- Annual major version updates

### Monitoring
- Error tracking and logging
- Performance metrics
- Usage statistics
- Data quality checks

### Backup Strategy
- Daily incremental backups
- Weekly full backups
- Monthly archive storage
- Automated recovery testing

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
