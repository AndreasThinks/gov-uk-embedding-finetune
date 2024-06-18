import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# Function to get document URLs from a page
def get_document_urls():
    document_links = driver.find_elements(By.CSS_SELECTOR, '.gem-c-document-list--no-underline .gem-c-document-list__item-title .govuk-link')
    return [link.get_attribute('href') for link in document_links]

# Initialize an empty list to store results
results = []

# Iterate through pages
page_number = 1
while True:
    starter_url = f"https://www.gov.uk/search/policy-papers-and-consultations?content_store_document_type%5B%5D=policy_papers&order=updated-newest&page={page_number}"
    logging.info(f"Opening URL: {starter_url}")
    driver.get(starter_url)
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gem-c-document-list--no-underline')))
    except:
        logging.info("No more pages found.")
        break
    
    document_urls = get_document_urls()
    if not document_urls:
        logging.info("No more document links found on this page.")
        break
    
    logging.info(f"Found {len(document_urls)} document URLs on page {page_number}")

    for url in document_urls:
        logging.info(f"Processing document URL: {url}")
        driver.get(url)
        
        # Find all sections with the specified class
        sections = driver.find_elements(By.CSS_SELECTOR, 'div.gem-c-attachment__details')
        logging.info(f"Found {len(sections)} sections in document")

        for section in sections:
            # Find the span with the specified class
            spans = section.find_elements(By.CSS_SELECTOR, '.gem-c-attachment__attribute')
            
            for span in spans:
                if span.text == "HTML":
                    try:
                        # Find the relevant header and click it
                        header = section.find_element(By.CSS_SELECTOR, 'h3.gem-c-attachment__title a')
                        header_text = header.text
                        logging.info(f"Clicking on header: {header_text}")
                        header.click()
                        
                        # Wait for the new page to load and find the text within the div with the specified class
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.govspeak')))
                        
                        try:
                            content_div = driver.find_element(By.CSS_SELECTOR, 'div.govspeak')
                            content_text = content_div.text
                        except Exception as e:
                            logging.error(f"Error finding content div: {e}")
                            content_text = ""

                        # Store the result
                        result = {
                            "url": url,
                            "header": header_text,
                            "content": content_text
                        }
                        results.append(result)
                        logging.info(f"Stored result for header: {header_text}")
                        
                        # Go back to the original document page
                        driver.back()
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gem-c-attachment__details')))
                        break  # Exit after finding the first "HTML" span
                    except Exception as e:
                        logging.error(f"Error processing section: {e}")
    
    # Save the results to a JSON file after processing each page
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"Results saved to results.json after page {page_number}")

    page_number += 1

# Close the WebDriver
driver.quit()
logging.info("WebDriver closed")
