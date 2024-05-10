import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()


def login_to_linkedin(driver):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )

    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(os.getenv("LOGIN_USERNAME"))

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(os.getenv("LOGIN_PASSWORD"))

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
        By.XPATH,
        "//input[@role='combobox']")))


def search_keyword_and_visit_profiles(driver, keyword):
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}"
    driver.get(search_url)
    try:
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-container")))

        visit_count = 0
        next_count = 0
        while visit_count <= 10: 
            try: 
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)         
                links = driver.find_elements(By.XPATH, "//a[@class='app-aware-link ']//span[@dir='ltr']//span[@aria-hidden='true']") 
                if visit_count != len(links):  
                    for i in range(len(links)):
                        try:
                            ActionChains(driver).click(links[visit_count]).perform()
                            time.sleep(5)
                            visit_count += 1
                            break
                        except StaleElementReferenceException:
                            logging.warning("StaleElementReferenceException occurred. Trying to re-find the elements.")
                            break         
                        except NoSuchElementException:
                            logging.warning("Follow button found but not clickable. Moving to the next button.")
                        finally:
                            driver.back()
                            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-container")))
                else:
                    if next_count < 1:
                        try:
                            next_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
                            )
                            next_button.click()
                            next_count += 1
                            visit_count = 0
                            continue
                        except NoSuchElementException:
                            print("Next button not found or timed out.")
                            break
                    else:
                        break
            except NoSuchElementException:
                logging.warning("Error while scrolling. Moving to the next scroll.")
    except TimeoutException:
        logging.warning("TimeoutException: Element 'search-results-container' not found for keyword:", keyword)


def main():
    with webdriver.Chrome() as driver:
        login_to_linkedin(driver)
        keywords = os.getenv('PROFILE_VISIT_KEYWORDS')
        if ',' in keywords:
            for keyword in keywords.split(','):
                search_keyword_and_visit_profiles(driver, keyword)
        else:
            keyword = keywords
            search_keyword_and_visit_profiles(driver, keyword)


if __name__ == "__main__":
    main()
