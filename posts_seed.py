import os
import time
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

def login_to_linkedin(driver):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )

    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(os.getenv("USERNAME"))

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(os.getenv("PASSWORD"))

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
        By.XPATH,
        "//input[@role='combobox']")))

def scrape_linkedin_posts(driver):
    search_url = "https://www.linkedin.com/search/results/content/?keywords=react%20remote%20jobs&origin=FACETED_SEARCH&searchId=e3dd1918-35dd-44ce-9371-bab3052f551c&sid=Xra&sortBy=%22date_posted%22"
    driver.get(search_url)

    for _ in range(int(os.getenv("SCROLL"))):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    post_elements = driver.find_elements(By.XPATH, "//div[@role='region']")
    post_urns = list(set([post.get_attribute("data-urn") for post in post_elements if post.get_attribute("data-urn")]))
    return post_urns

def post_content(url, driver):
    driver.get(url)
    print(url)
    time.sleep(10)
    post_content = driver.find_element(By.XPATH, "//p[@data-test-id='main-feed-activity-card__commentary']").text
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel=os.getenv("SLACK_CHANNEL"),
            text=post_content,
            user=os.getenv("USER")
        )
    except SlackApiError as e:
        logging.error(f"Error posting to Slack: {e.response['error']}")

def main():
    with webdriver.Chrome() as driver:
        login_to_linkedin(driver)
        post_urns = scrape_linkedin_posts(driver)
        for urn in post_urns:
            link = f"https://www.linkedin.com/feed/update/{urn}/"
            post_content(link, driver)
            time.sleep(5)

if __name__ == "__main__":
    main()