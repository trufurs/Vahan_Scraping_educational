from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from pathlib import Path
from datetime import datetime

YEAR_OPTIONS = {
    "Select Year": "selectedYear_0",
    "Till Today": "selectedYear_1",
    "2025": "selectedYear_2",
    "2024": "selectedYear_3",
    "2023": "selectedYear_4",
    "2022": "selectedYear_5",
    "2021": "selectedYear_6",
    "2020": "selectedYear_7",
    "2019": "selectedYear_8",
    "2018": "selectedYear_9",
    "2017": "selectedYear_10",
    "2016": "selectedYear_11",
    "2015": "selectedYear_12",
    "2014": "selectedYear_13",
    "2013": "selectedYear_14",
    "2012": "selectedYear_15",
    "2011": "selectedYear_16",
    "2010": "selectedYear_17",
    "2009": "selectedYear_18",
    "2008": "selectedYear_19",
    "2007": "selectedYear_20",
    "2006": "selectedYear_21",
    "2005": "selectedYear_22",
    "2004": "selectedYear_23",
    "2003": "selectedYear_24",
    "2002": "selectedYear_25"
}

def setup_chrome():
    """Configure and initialize Chrome in headless mode"""
    # Set up custom download directory
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    print(f"Downloads will be saved to: {download_dir}")

    # Configure Chrome options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # Initialize Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver, download_dir

def wait_for_download(download_dir, timeout=30):
    """Wait for download to complete by monitoring file count"""
    time.sleep(2)  # Initial wait
    initial_count = len(list(Path(download_dir).glob("*.xls*")))
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_count = len(list(Path(download_dir).glob("*.xls*")))
        if current_count > initial_count:
            time.sleep(1)  # Give extra second for file to complete
            return True
        time.sleep(1)
    return False

def main():
    BASE_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
    MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    
    try:
        print("Starting Vahan data scraper...")
        driver, download_dir = setup_chrome()
        print("Chrome initialized successfully")

        # Load the page
        print("Loading Vahan Dashboard...")
        driver.get(BASE_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "yaxisVar")))
        print("Page loaded successfully")

        # Set Y-axis (Vehicle Class)
        print("Setting Y-axis...")
        driver.find_element(By.ID, "yaxisVar").click()
        time.sleep(2)
        driver.find_element(By.ID, "yaxisVar_4").click()
        time.sleep(2)

        # Set X-axis
        print("Setting X-axis...")
        driver.find_element(By.ID, "xaxisVar").click()
        time.sleep(2)
        driver.find_element(By.ID, "xaxisVar_0").click()
        time.sleep(2)

        # Set Year
        print("Setting Year...")
        driver.find_element(By.ID, "selectedYear").click()
        time.sleep(2)
        driver.find_element(By.ID, YEAR_OPTIONS[input("Enter year (e.g., 2024) between 2002 and 2024: ")]).click()
        time.sleep(2)

        # Click refresh
        print("Clicking refresh button...")
        refresh = driver.find_element(By.ID, "j_idt71")
        refresh.click()
        time.sleep(3)

        # Download data for each month
        for month in MONTHS:
            try:
                print(f"\nProcessing {month}...")
                
                # Select month
                driver.find_element(By.ID, "groupingTable:selectMonth").click()
                time.sleep(2)
                month_option_id = f"groupingTable:selectMonth_{MONTHS.index(month) + 1}"
                driver.find_element(By.ID, month_option_id).click()
                time.sleep(2)

                # Download
                print(f"Downloading data for {month}...")
                download_btn = driver.find_element(By.ID, "groupingTable:xls")
                download_btn.click()

                # Wait for download and rename
                downloaded_file = wait_for_download(download_dir)
                if downloaded_file:
                    year = driver.find_element(By.ID, "selectedYear_input").get_attribute("value")
                    new_name = f"vahan_data_{year}_{month}.xls"
                    new_path = downloaded_file.parent / new_name
                    
                    if new_path.exists():
                        new_name = f"vahan_data_{year}_{month}_{datetime.now():%Y%m%d_%H%M%S}.xls"
                        new_path = downloaded_file.parent / new_name
                    
                    downloaded_file.rename(new_path)
                    print(f"Successfully downloaded: {new_name}")
                else:
                    print(f"Download failed for {month}")

                time.sleep(2)

            except Exception as e:
                print(f"Error processing {month}: {str(e)}")
                continue

        print("\nDownload process completed!")
        print(f"Files are saved in: {download_dir}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        try:
            driver.quit()
            print("Browser closed successfully")
        except:
            pass

if __name__ == "__main__":
    main()
