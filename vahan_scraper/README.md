# Vahan Dashboard Scraper

A Streamlit-based web application for extracting and visualizing vehicle registration data from the Vahan Dashboard.

## Features

- Scrapes vehicle registration data for:
  - Vehicle types (2W, 3W, 4W)
  - Manufacturer-wise registrations
  - All available years and months
- Saves both structured CSV data and raw HTML responses
- Handles dynamic content loading
- Includes error handling and logging
- Supports headless operation

## Installation

1. Make sure you have Python 3.x installed
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The web application will:
1. Open in your default browser
2. Provide an interface to:
   - Start new scraping sessions
   - View existing data
   - Filter and analyze results
   - Download filtered data
   - View interactive visualizations

When you start a scraping session, the app will:
1. Launch Chrome in headless mode
2. Navigate through vehicle types, manufacturers, years, and months
3. Extract and save data continuously

## Output Files

- `data/vahan_data.csv`: Contains the structured data with columns for:
  - All table columns from the dashboard
  - Vehicle type
  - Manufacturer
  - Year
  - Month

- `raw_responses/*.html`: Raw HTML files named as:
  `<vehicle_type>_<manufacturer>_<year>_<month>.html`

- `errors.log`: Log file containing any errors encountered during scraping

## Resuming Interrupted Scraping

The scraper appends data to the CSV file rather than overwriting it. If the script is interrupted:

1. The existing CSV file will contain all successfully scraped data
2. Raw HTML files will be preserved
3. Simply restart the script - it will continue adding new data

## Notes

- The scraper runs in headless mode by default for better performance
- HTML files are stored with sanitized filenames (spaces replaced with underscores)
- WebDriverWait is used to handle dynamic content loading
- Each request has appropriate delays to avoid overwhelming the server
- Failed requests are logged with details in errors.log
