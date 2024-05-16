import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import logging

from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

def login_to_linkedin(driver):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(os.getenv("LOGIN_USERNAME"))

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(os.getenv("LOGIN_PASSWORD"))

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    try:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@role='combobox']")))
    except TimeoutException as e:
        logging.error("TimeoutException occurred: %s", e)

def visit_profile(driver, profile_link):
    try:
        driver.get(profile_link)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[@data-control-name='contact_see_more']")))
        logging.info(f"Visited profile: {profile_link}")
        time.sleep(5)  # Additional wait to ensure all content is loaded
    except Exception as e:
        logging.error(f"Error visiting profile: {e}")

def search_keyword_and_visit_profiles(driver, keyword, page_limit):
    page_count = 1
    while page_count <= page_limit:
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&page={page_count}"
        driver.get(search_url)
        try:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-container")))

            profile_links = []
            profiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/') and contains(@class, 'app-aware-link')]")
            for profile in profiles:
                profile_link = profile.get_attribute('href')
                if profile_link and profile_link not in profile_links:
                    profile_links.append(profile_link)

            for profile_link in profile_links:
                visit_profile(driver, profile_link)
                driver.back()
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-container")))

            logging.info(f"Visited all profiles on page {page_count} for keyword '{keyword}'")

            page_count += 1
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            logging.warning(f"Error while navigating profiles: {e}")
            break
    logging.info(f"Completed visiting profiles for keyword '{keyword}' up to page {page_limit}")

def wait_for_next_run(delay_seconds):
    logging.info(f"On break for {delay_seconds / 3600:.2f} hours till the next run.")
    time.sleep(delay_seconds)
    logging.info("Resuming execution after the delay.")

def main():
    delay_hours = float(os.getenv('DELAY_HOURS', 5))
    delay_seconds = delay_hours * 3600
    page_limit = int(os.getenv('PAGE_LIMIT', 5))

    with webdriver.Chrome() as driver:
        login_to_linkedin(driver)
        
        while True:
            keywords = os.getenv('PROFILE_VISIT_KEYWORDS', '').split(',')
            for keyword in keywords:
                search_keyword_and_visit_profiles(driver, keyword.strip(), page_limit)
            
            wait_for_next_run(delay_seconds)

if __name__ == "__main__":
    main()