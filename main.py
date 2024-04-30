import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from slack_sdk import WebClient
from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError
import logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()


def scrap_post_urn():
    driver = webdriver.Chrome()

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

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH,
        "//input[@role='combobox']")))

    search_url = "https://www.linkedin.com/search/results/content/?keywords=react%20remote%20jobs&origin=FACETED_SEARCH&searchId=e3dd1918-35dd-44ce-9371-bab3052f551c&sid=Xra&sortBy=%22date_posted%22"
    driver.get(search_url)

    time.sleep(5)

    scroll_count = 0
    while scroll_count < 50:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        scroll_count += 1

    post_elements = driver.find_elements(By.XPATH, "//div[@role='region']")

    post_urns = []
    for post_element in post_elements[:100]:
        post_urn = post_element.get_attribute("data-urn")
        if post_urn:
            post_urns.append(post_urn)
    driver.quit()
    return post_urns


def post_content(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
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
        assert e.response["error"]


post_urn = scrap_post_urn()
for urn in post_urn:
    link = f"https://www.linkedin.com/feed/update/{urn}/"
    post_content(link)
    time.sleep(5)
