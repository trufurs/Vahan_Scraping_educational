import os
import time
import logging
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    filename='errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VahanScraper:
    def __init__(self):
        self.url = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
        self.setup_driver()
        self.data_dir = "data"
        self.raw_dir = "raw_responses"
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)

    def setup_driver(self):
        """Configure and initialize Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def get_dropdown_options(self, dropdown_id):
        """Get all options from a dropdown menu."""
        try:
            dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, dropdown_id))
            )
            options = dropdown.find_elements(By.TAG_NAME, "option")
            return [(opt.get_attribute("value"), opt.text) for opt in options if opt.get_attribute("value")]
        except Exception as e:
            logging.error(f"Error getting options for dropdown {dropdown_id}: {str(e)}")
            return []

    def select_dropdown_option(self, dropdown_id, value):
        """Select an option from a dropdown menu."""
        try:
            dropdown = self.wait.until(
                EC.element_to_be_clickable((By.ID, dropdown_id))
            )
            dropdown.click()
            option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//option[@value='{value}']"))
            )
            option.click()
            time.sleep(2)  # Allow for dynamic content update
            return True
        except Exception as e:
            logging.error(f"Error selecting option {value} in dropdown {dropdown_id}: {str(e)}")
            return False

    def save_raw_html(self, vehicle_type, manufacturer, year, month):
        """Save the raw HTML response to a file."""
        try:
            filename = f"{vehicle_type}_{manufacturer}_{year}_{month}.html".replace(" ", "_")
            filepath = os.path.join(self.raw_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception as e:
            logging.error(f"Error saving raw HTML: {str(e)}")

    def extract_table_data(self):
        """Extract data from the table and return as a DataFrame."""
        try:
            table = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
            )
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            data = []
            headers = []
            
            # Get headers
            header_row = rows[0]
            headers = [th.text for th in header_row.find_elements(By.TAG_NAME, "th")]
            
            # Get data rows
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                data.append([cell.text for cell in cells])
                
            return pd.DataFrame(data, columns=headers)
        except Exception as e:
            logging.error(f"Error extracting table data: {str(e)}")
            return pd.DataFrame()

    def scrape(self):
        """Main scraping function."""
        try:
            self.driver.get(self.url)
            
            # Vehicle categories to scrape
            vehicle_types = ["2W", "3W", "4W"]
            
            for vehicle_type in tqdm(vehicle_types, desc="Vehicle Types"):
                # Select vehicle type
                if not self.select_dropdown_option("form_vehicleType", vehicle_type):
                    continue
                
                # Get manufacturer options
                manufacturers = self.get_dropdown_options("form_manufacturer")
                
                for manufacturer_value, manufacturer_name in tqdm(manufacturers, desc="Manufacturers"):
                    if not self.select_dropdown_option("form_manufacturer", manufacturer_value):
                        continue
                    
                    # Get year options
                    years = self.get_dropdown_options("form_year")
                    
                    for year_value, year_name in tqdm(years, desc="Years"):
                        if not self.select_dropdown_option("form_year", year_value):
                            continue
                        
                        # Get month options
                        months = self.get_dropdown_options("form_month")
                        
                        for month_value, month_name in tqdm(months, desc="Months"):
                            if not self.select_dropdown_option("form_month", month_value):
                                continue
                            
                            # Extract and save data
                            df = self.extract_table_data()
                            
                            if not df.empty:
                                # Add metadata columns
                                df["vehicle_type"] = vehicle_type
                                df["manufacturer"] = manufacturer_name
                                df["year"] = year_name
                                df["month"] = month_name
                                
                                # Save to CSV
                                csv_path = os.path.join(self.data_dir, "vahan_data.csv")
                                df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
                                
                                # Save raw HTML
                                self.save_raw_html(vehicle_type, manufacturer_name, year_name, month_name)
            
        except Exception as e:
            logging.error(f"Error in main scraping function: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = VahanScraper()
    scraper.scrape()
