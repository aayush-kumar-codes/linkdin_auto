
import os
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

def random_delay(min_seconds=5, max_seconds=30):
    try:
        delay = random.uniform(min_seconds, max_seconds)
        logging.debug(f"Sleeping for {delay:.2f} seconds to simulate human behavior.")
        time.sleep(delay)
    except Exception as e:
        logging.error(f"Error during random delay: {e}")

def move_and_click(driver, element):
    try:
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        random_delay(2, 5)
        actions.click(element).perform()
        random_delay(2, 5)
    except Exception as e:
        logging.error(f"Error during move and click action: {e}")

def type_like_human(element, text, max_delay=3):
    try:
        for char in text:
            element.send_keys(char)
            random_delay(0, max_delay)
    except Exception as e:
        logging.error(f"Error during typing: {e}")

def login_to_linkedin(driver):
    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "username")))

        username_field = driver.find_element(By.ID, "username")
        move_and_click(driver, username_field)
        type_like_human(username_field, os.getenv("LOGIN_USERNAME"))

        random_delay(2, 5)

        password_field = driver.find_element(By.ID, "password")
        move_and_click(driver, password_field)
        type_like_human(password_field, os.getenv("LOGIN_PASSWORD"))

        random_delay(1, 5)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        move_and_click(driver, login_button)

        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@role='combobox']")))
    except Exception as e:
        logging.error(f"Error during login: {e}")

def visit_profile(driver, profile_link):
    try:
        driver.get(profile_link)
        logging.info(f"Visited profile: {profile_link}")
        random_delay(3, 10)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_delay(2, 5)

        buttons = driver.find_elements(By.TAG_NAME, "button")
        if buttons:
            button_to_click = random.choice(buttons)
            move_and_click(driver, button_to_click)

        actions = ActionChains(driver)
        for _ in range(random.randint(1, 3)):
            try:
                actions.move_by_offset(random.randint(-20, 20), random.randint(-20, 20)).perform()
                random_delay(0.5, 2)
            except Exception as e:
                logging.error(f"Error during move action: {e}")

        for _ in range(random.randint(1, 3)):
            if random.choice([True, False]):  
                driver.execute_script("window.scrollBy(0, -window.innerHeight);")
            else:
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
            random_delay(0.5, 2)

        for _ in range(random.randint(1, 3)):
            try:
                actions.move_by_offset(random.randint(-20, 20), random.randint(-20, 20)).perform()
                random_delay(0.5, 2)
            except Exception as e:
                logging.error(f"Error during move action: {e}")

        random_delay(5, 10)
    except Exception as e:
        logging.error(f"Error visiting profile: {e}")

def search_keyword_and_visit_profiles(driver, keyword, page_limit):
    try:
        page_count = 1
        while page_count <= page_limit:
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&page={page_count}"
            random_delay(2, 5)
            driver.get(search_url)
            random_delay(2, 7)
            try:
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-container")))
                actions = ActionChains(driver)
                for _ in range(random.randint(1, 3)):
                    actions.move_by_offset(random.randint(-20, 20), random.randint(-20, 20)).perform()
                    random_delay(0.5, 2)

                profile_links = []
                profiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/') and contains(@class, 'app-aware-link')]")
                for profile in profiles:
                    profile_link = profile.get_attribute('href')
                    if profile_link and profile_link not in profile_links:
                        profile_links.append(profile_link)

                print("===================>",search_url,page_count,profile_links)
                for profile_link in profile_links:
                    visit_profile(driver, profile_link)
                    driver.back()
                    random_delay(2, 6)

                logging.info(f"Visited all profiles on page {page_count} for keyword '{keyword}'")

                page_count += 1
                random_delay(10, 20)
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                logging.warning(f"Error while navigating profiles: {e}")
        logging.info(f"Completed visiting profiles for keyword '{keyword}' up to page {page_limit}")
    except Exception as e:
        logging.error(f"Error during search and visit profiles: {e}")



def wait_for_next_run(delay_seconds):
    try:
        logging.info(f"On break for {delay_seconds / 3600:.2f} hours till the next run.")
        time.sleep(delay_seconds)
        logging.info("Resuming execution after the delay.")
    except Exception as e:
        logging.error(f"Error during wait for next run: {e}")

def main():
    try:
        delay_hours = float(os.getenv('DELAY_HOURS', 5))
        delay_seconds = delay_hours * 3600
        page_limit = int(os.getenv('PAGE_LIMIT', 5))

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        with webdriver.Chrome(options=chrome_options) as driver:
            login_to_linkedin(driver)

            while True:
                keywords = os.getenv('PROFILE_VISIT_KEYWORDS', '').split(',')
                for keyword in keywords:
                    search_keyword_and_visit_profiles(driver, keyword.strip(), page_limit)
                    random_delay(30, 500)
                wait_for_next_run(delay_seconds)
    except Exception as e:
        logging.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()