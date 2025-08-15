# Vahan Dashboard Analysis

This project provides an interactive dashboard for analyzing vehicle registration data from the Vahan Dashboard, focusing on vehicle type-wise and manufacturer-wise registration data.

## Features

- Interactive data visualization using Streamlit
- Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) growth analysis
- Vehicle category-wise analysis (2W/3W/4W)
- Manufacturer-wise performance tracking
- Date range selection
- Dynamic filtering by vehicle category and manufacturer
- Trend analysis with interactive graphs

## Setup Instructions

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## Data Sources

- Data is collected from the Vahan Dashboard using automated scraping
- Data is stored in SQLite database (`data/vahan_data.db`)
- Includes vehicle registration data categorized by:
  - Vehicle types (2W/3W/4W)
  - Manufacturers
  - Time periods

## Data Assumptions

- All registration numbers are considered final and verified
- Vehicle categories are standardized across different time periods
- Manufacturer names are consistent across the dataset
- Missing or null values are handled as zeros in aggregations

## Feature Roadmap

Future enhancements planned:

1. Advanced Analytics:
   - Seasonal trend analysis
   - Market share predictions
   - Segment-wise growth forecasting

2. Additional Visualizations:
   - Heat maps for regional analysis
   - Interactive drill-down capabilities
   - Custom comparison periods

3. Data Enhancements:
   - Real-time data updates
   - Historical data expansion
   - Additional vehicle categories

4. Export Capabilities:
   - Custom report generation
   - Data export in multiple formats
   - Scheduled report delivery

## Usage Instructions

1. **Date Range Selection:**
   - Use the sidebar to select start and end dates
   - Format: YYYY-MM (e.g., 2024-01)

2. **Manufacturer Selection:**
   - Choose specific manufacturers from the dropdown
   - Multiple selections allowed
   - Default shows top 5 manufacturers

3. **Interactive Graphs:**
   - Hover over data points for detailed information
   - Click and drag to zoom
   - Double-click to reset view

4. **Data Table:**
   - Scroll through detailed statistics
   - Sort by any column
   - Search functionality available

## Key Insights

The dashboard provides valuable insights for investors:

- Trend analysis for market growth
- Manufacturer performance comparison
- Vehicle category distribution
- Growth rates (YoY and QoQ)
- Market share analysis
