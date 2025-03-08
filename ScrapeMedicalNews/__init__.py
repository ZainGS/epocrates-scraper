from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import logging
import azure.functions as func
import shutil

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching latest medical news using Selenium...')

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")  # Headless mode for performance
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36")

    service = Service(shutil.which("chromedriver"))
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.epocrates.com")

        # Wait for the page to load key elements
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.reactMarkDown p")))

        articles = []
        news_items = driver.find_elements(By.CSS_SELECTOR, "div[data-testid]")

        for item in news_items:
            try:
                # Locate the link
                link_elements = item.find_elements(By.CSS_SELECTOR, "a[data-testid='CardItemLink']")
                link = link_elements[0].get_attribute("href") if link_elements else None

                # Locate the title
                title_elements = item.find_elements(By.XPATH, ".//a[@data-testid='CardItemLink']/div[2]//p")
                if not title_elements:
                    title_elements = item.find_elements(By.CSS_SELECTOR, "a[data-testid='CardItemLink'] p")

                title = title_elements[0].text.strip() if title_elements else None

                # Extract description
                desc_elements = item.find_elements(By.CSS_SELECTOR, "div.reactMarkDown p")
                description = " ".join([d.text.strip() for d in desc_elements]) if desc_elements else None

                # Replace ellipsis Unicode `\u2026` with "..."
                if description:
                    description = description.replace(" \u2026", "...")

                # Only add articles that have all three fields
                if title and description and link:
                    articles.append({
                        "title": title,
                        "description": description,
                        "url": link
                    })

            except Exception as e:
                logging.error(f"Skipping an item due to error: {str(e)}")
                continue

        return func.HttpResponse(json.dumps(articles[:3], indent=4), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Error scraping: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

    finally:
        if driver:
            driver.quit()
