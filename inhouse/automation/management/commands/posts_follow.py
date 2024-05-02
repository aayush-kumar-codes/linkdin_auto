import os
import re
import time
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from automation.models import LinkedInJobs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.DEBUG)
load_dotenv()


class Command(BaseCommand):
    help = 'scrapping the Linkedin Jobs'

    def handle(self, *args, **options):
        with webdriver.Chrome() as driver:
            self.login_to_linkedin(driver)
            post_urns = self.scrape_linkedin_posts(driver)
            for urn in post_urns:
                link = f"https://www.linkedin.com/feed/update/{urn}/"
                self.post_follow(link, driver)
                time.sleep(5)

    def login_to_linkedin(self,driver):
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

    def scrape_linkedin_posts(self, driver):
        search_url = "https://www.linkedin.com/search/results/content/?keywords=react%20remote%20jobs&origin=FACETED_SEARCH&searchId=e3dd1918-35dd-44ce-9371-bab3052f551c&sid=Xra&sortBy=%22date_posted%22"
        driver.get(search_url)

        for _ in range(20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        post_elements = driver.find_elements(By.XPATH, "//div[@role='region']")
        post_urns = list(set([post.get_attribute("data-urn") for post in post_elements if post.get_attribute("data-urn")]))
        return post_urns

    def post_follow(self, url, driver):
        driver.get(url)
        print(url)
        time.sleep(10)
        post_content_loaded = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2__description"))
        )
        follow_count = 0
        if follow_count <=10:
            follow_button = driver.find_element(By.CLASS_NAME, "follow")
            follow_button.click()
            time.sleep(3)
        else:
            driver.quit()