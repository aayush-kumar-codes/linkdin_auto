from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
# Navigate to the LinkedIn login page
driver.get("https://www.linkedin.com/login")
# Wait for the login form to be present
login_form = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "username"))
)
# Enter the username or email
username_field = driver.find_element(By.ID, "username")
username_field.send_keys("saurabh.excel2011@gmail.com")
# Enter the password
password_field = driver.find_element(By.ID, "password")
password_field.send_keys("linkedin@123#")
# Submit the login form
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
login_button.click()
time.sleep(10)
search_url = "https://www.linkedin.com/search/results/content/?keywords=react%20remote%20jobs&origin=FACETED_SEARCH&searchId=e3dd1918-35dd-44ce-9371-bab3052f551c&sid=Xra&sortBy=%22date_posted%22"
driver.get(search_url)
scroll_pause_time = 5
screen_height = driver.execute_script("return window.screen.height;")
i = 1
urls = []
while True:
    driver.execute_script(f"window.scrollTo(0, {screen_height * i});")
    i += 1
    time.sleep(scroll_pause_time)
    # soup = BeautifulSoup(driver.page_source, "html.parser")
    post_urn = driver.find_element(By.XPATH, "//div[@role='region]")
    # for urn in post_urn:
    url = f"https://www.linkedin.com/feed/update/{post_urn['data-urn']}/"
    urls.append(url)
    '''scroll_height = \
        driver.execute_script("return document.body.scrollHeight;")'''
    if len[urls] > 100:
        break
print(urls)
driver.quit()
