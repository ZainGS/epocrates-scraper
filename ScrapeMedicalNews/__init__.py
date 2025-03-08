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
    logging.info("🚀 Starting ScrapeMedicalNews function...")

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")  # Run in headless mode
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36")

    try:
        chromedriver_path = shutil.which("chromedriver")
        logging.info(f"🔎 Chromedriver found at: {chromedriver_path}")
        
        if not chromedriver_path:
            raise FileNotFoundError("❌ Chromedriver not found! Make sure it's installed in Azure.")

        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        logging.info("🌍 Navigating to Epocrates website...")
        driver.get("https://www.epocrates.com")

        # Wait for elements to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.reactMarkDown p")))
        logging.info("✅ Page loaded successfully!")

        articles = []
        news_items = driver.find_elements(By.CSS_SELECTOR, "div[data-testid]")
        logging.info(f"📰 Found {len(news_items)} news items")

        for index, item in enumerate(news_items):
            try:
                logging.info(f"🔍 Processing article {index+1}")

                # Locate the link
                link_elements = item.find_elements(By.CSS_SELECTOR, "a[data-testid='CardItemLink']")
                link = link_elements[0].get_attribute("href") if link_elements else None
                logging.info(f"🔗 Link: {link}")

                # Locate the title
                title_elements = item.find_elements(By.XPATH, ".//a[@data-testid='CardItemLink']/div[2]//p")
                if not title_elements:
                    title_elements = item.find_elements(By.CSS_SELECTOR, "a[data-testid='CardItemLink'] p")

                title = title_elements[0].text.strip() if title_elements else None
                logging.info(f"📝 Title: {title}")

                # Extract description
                desc_elements = item.find_elements(By.CSS_SELECTOR, "div.reactMarkDown p")
                description = " ".join([d.text.strip() for d in desc_elements]) if desc_elements else None
                if description:
                    description = description.replace(" \u2026", "...")
                logging.info(f"📄 Description: {description}")

                # Only add valid articles
                if title and description and link:
                    articles.append({
                        "title": title,
                        "description": description,
                        "url": link
                    })
                    logging.info(f"✅ Article {index+1} added successfully")

            except Exception as e:
                logging.error(f"⚠️ Skipping article {index+1} due to error: {str(e)}")
                continue

        logging.info(f"📦 Returning {len(articles[:3])} articles")
        return func.HttpResponse(json.dumps(articles[:3], indent=4), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"❌ Critical error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

    finally:
        if 'driver' in locals():
            driver.quit()
            logging.info("🛑 WebDriver session closed")
