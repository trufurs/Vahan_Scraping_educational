"""
Script to scrape vehicle registration data from Vahan Dashboard using Selenium.
"""
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

VAHAN_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"


def fetch_vahan_data(output_csv_path):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(VAHAN_URL)
    wait = WebDriverWait(driver, 20)

    # Wait for the main table to load (update selector as needed)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    time.sleep(5)  # Allow JS to finish rendering

    # Scrape table data (update selectors as per actual site structure)
    tables = driver.find_elements(By.TAG_NAME, "table")
    data = []
    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cols = [col.text for col in row.find_elements(By.TAG_NAME, "td")]
            if cols:
                data.append(cols)

    driver.quit()
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False)
    print(f"Data saved to {output_csv_path}")

if __name__ == "__main__":
    fetch_vahan_data("../data/raw_vahan_data.csv")
