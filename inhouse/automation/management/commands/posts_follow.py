import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import logging
from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

class Command(BaseCommand):
    help = 'scrapping the Linkedin Jobs'

    def handle(self, *args, **options):
        with webdriver.Chrome() as driver:
            self.login_to_linkedin(driver)
            self.follow_posts_while_scrolling(driver)

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

    def follow_posts_while_scrolling(self, driver):
        search_url = "https://www.linkedin.com/search/results/content/?keywords=react%20remote%20jobs&origin=FACETED_SEARCH&searchId=e3dd1918-35dd-44ce-9371-bab3052f551c&sid=Xra&sortBy=%22date_posted%22"
        driver.get(search_url)

        follow_count = 0
        while follow_count < 10: 
            try:

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                follow_buttons = driver.find_elements(By.CLASS_NAME, "follow")
                for button in follow_buttons:
                    button.click()
                    time.sleep(4)  
                    follow_count += 1
                    if follow_count >= 10:
                        break

            except NoSuchElementException:
                logging.warning("Follow button not found. Moving to the next scroll.")
            finally:
                time.sleep(2)

