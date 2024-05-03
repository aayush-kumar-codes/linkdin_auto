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
from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

class Command(BaseCommand):
    help = 'scrapping the Linkedin Jobs'

    def handle(self, *args, **options):
        keywords = ['python', 'react']
        with webdriver.Chrome() as driver:
            self.login_to_linkedin(driver)
            for keyword in keywords:
                self.search_keyword_and_visit_profiles(driver, keyword)
                # Reset visit_count for the next keyword search
                visit_count = 0

    def login_to_linkedin(self, driver):
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

    def search_keyword_and_visit_profiles(self, driver, keyword):
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}"
        driver.get(search_url)

        try:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-container")))

            visit_count = 0
            next_count = 0
            while visit_count < 10: 
                try:  
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(5)            
                    links = driver.find_elements(By.XPATH, "//a[@class='app-aware-link ']//span[@dir='ltr']//span[@aria-hidden='true']")   
                    for i in range(len(links)):
                        try:
                            ActionChains(driver).click(links[visit_count]).perform()
                            time.sleep(5)
                            visit_count += 1
                            if visit_count >= 10 and next_count < 9:
                                next_button = driver.find_element(By.ID, "ember634")
                                next_button.click()
                                next_count += 1
                                visit_count = 0
                                break
                            break
                        except StaleElementReferenceException:
                            logging.warning("StaleElementReferenceException occurred. Trying to re-find the elements.")
                            break         
                        except NoSuchElementException:
                            logging.warning("Follow button found but not clickable. Moving to the next button.")
                        finally:
                            driver.back()
                            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-container")))
                except NoSuchElementException:
                    logging.warning("Error while scrolling. Moving to the next scroll.")
        except TimeoutException:
            logging.warning("TimeoutException: Element 'search-results-container' not found for keyword:", keyword)
            return 