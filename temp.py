from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import logging
import random

logging.basicConfig(filename='scraping.log', level=logging.ERROR)
# from webdriver_manager.chrome import ChromeDriverManager

# from undetected_chromedriver import Chrome, ChromeOptions

# options = ChromeOptions()
# options.add_argument("--disable-notifications")
# options.add_argument("--headless")  # Keep headless if needed

# driver = Chrome(options=options)

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                     Chrome/120.0.0.0 Safari/537.36')

# options.add_argument("--headless")  # Uncomment for headless mode

# Initialize WebDriver
driver = webdriver.Chrome(options=options)


def scrape_page(id):
    driver.delete_all_cookies()  # Note that this is not ideal, as it may trigger additional bot detection measures
    url = f"https://elibrary.ru/item.asp?id={id}"
    driver.get(url)

    data = {
        'id': id,
        'title': '',
        'authors': '',
        'year': '',
        'type': '',
        'abstract': ''
    }

    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.bigtext"))
        )

        html = driver.page_source

        with open("elibrary/" + id + ".html", "w", encoding="utf-8") as file:
            file.write(html)

        # Extract title
        # title_element = driver.find_element(By.CSS_SELECTOR, "p.bigtext")
        # data['title'] = title_element.text.strip()
        #
        # # Extract authors
        # authors_section = driver.find_element(By.XPATH, "//td[contains(., 'Автор') and @align='center']")
        # authors = authors_section.find_elements(By.XPATH, ".//b//font")
        # data['authors'] = ", ".join([author.text.strip() for author in authors])
        #
        # # Extract year
        # year_element = driver.find_element(By.XPATH, "//td[contains(., 'Год:')]/font")
        # data['year'] = year_element.text.strip()
        #
        # # Extract type
        # type_element = driver.find_element(By.XPATH, "//td[contains(., 'Тип:')]/font")
        # data['type'] = type_element.text.strip()
        #
        # # Extract abstract
        # abstract_element = driver.find_element(By.ID, "abstract1")
        # data['abstract'] = abstract_element.text.strip()

    except Exception as e:
        logging.error(f"Error scraping {id}: {str(e)}", exc_info=True)

    return data


# Read input CSV with IDs
input_csv = "input_ids.csv"
output_csv = "output_data.csv"

ids = []
with open(input_csv, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # Skip header if exists
    for row in reader:
        ids.append(row[0])

# Scrape data for all IDs
results = []
for idx, id in enumerate(ids):
    print(f"Processing ID {id} ({idx + 1}/{len(ids)})")
    results.append(scrape_page(id))
    time.sleep(random.randint(30, 60))  # Be polite with delays between requests

# # Write results to CSV
# with open(output_csv, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=["id", "title", "authors", "year", "type", "abstract"])
#     writer.writeheader()
#     writer.writerows(results)

driver.quit()