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
                self.post_content(link, driver, urn)
                time.sleep(5)

    def login_to_linkedin(self,driver):
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys("saurabh.excel2011@gmail.com")

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("linkedin@123#")

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
            By.XPATH,
            "//input[@role='combobox']")))

    def scrape_linkedin_posts(self, driver):
        search_url = "https://www.linkedin.com/search/results/content/?keywords=react%20remote%20jobs&origin=FACETED_SEARCH&searchId=e3dd1918-35dd-44ce-9371-bab3052f551c&sid=Xra&sortBy=%22date_posted%22"
        driver.get(search_url)

        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        post_elements = driver.find_elements(By.XPATH, "//div[@role='region']")
        post_urns = list(set([post.get_attribute("data-urn") for post in post_elements if post.get_attribute("data-urn")]))
        return post_urns

    def extract_email(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def extract_skills(self, text):
        skills_list = ['Python', 'Java', 'JavaScript', 'React', '.NET', 'C#', 'HTML', 'CSS', 'SQL', 'Machine Learning']
        skills_pattern = '|'.join(skills_list)
        matches = re.findall(skills_pattern, text, flags=re.IGNORECASE)
        return matches if matches else None

    def post_content(self, url, driver, urn):
        driver.get(url)
        print(url)
        time.sleep(10)
        post_content_loaded = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2__description"))
        )
        
        post_content_element = driver.find_element(By.CLASS_NAME, "feed-shared-update-v2__description")
        linkedinprofile = driver.find_elements(By.XPATH, "//a[@class='app-aware-link  update-components-actor__image relative']")
        linkedinprofile_link = list(set([linkedin.get_attribute("href") for linkedin in linkedinprofile if linkedin.get_attribute("href")]))
        linkedin_link = linkedinprofile_link[0]
        post_content = post_content_element.text
        # lines = post_content.split('\n')
        cleaned_content = re.sub(r'#\w+', '', post_content)
        final_content = re.sub(r'hashtag', '', cleaned_content)
        final_content_remove = re.sub(r',\w+', '', final_content)
        content = "".join([s for s in final_content_remove.strip().splitlines(True) if s.strip()])
        print(content)
        email = self.extract_email(post_content)
        skills = set(self.extract_skills(post_content))
        print("------")
        print(email)
        
        string_list = [str(element) for element in skills]
        delimiter = ", "
        result_string = delimiter.join(string_list)
        print("------")
        print(result_string)
        print("------")
        print(linkedin_link)

        linkedinjobs, created = LinkedInJobs.objects.get_or_create(
                                email=email,
                                skills=result_string,
                                linkedin_profile_link=linkedinprofile_link[0],
                                post_profile=url,
                                post_content=content,
                                urn_id=urn
                            )

        '''slack_token = os.getenv("SLACK_BOT_TOKEN")
        client = WebClient(token=slack_token)

        try:
            response = client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL"),
                text=post_content,
                user=os.getenv("USER")
            )
        except SlackApiError as e:
            logging.error(f"Error posting to Slack: {e.response['error']}")'''
