import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, TimeoutException, NoSuchWindowException
import logging
from datetime import datetime
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

    try:
        # Increase wait time for the combobox to be visible
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@role='combobox']")))
    except TimeoutException as e:
        print("TimeoutException occurred:", e)
   



def withdraw_request(driver):
    search_url = "https://www.linkedin.com/mynetwork/invitation-manager/sent/"
    driver.get(search_url)
    time.sleep(2)
    try:
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            # Locate the elements within the loop
            withdraw_buttons = driver.find_elements(By.CLASS_NAME, "artdeco-button--tertiary")
            durations = driver.find_elements(By.CLASS_NAME, "time-badge")
            zipped = zip(withdraw_buttons, durations)
            for button, duration in zipped:
                try:
                    sent_duration = duration.text
                    if sent_duration == "Sent 1 month ago":
                        # Scroll to the button's position
                        driver.execute_script("arguments[0].scrollIntoView();", button)
                        time.sleep(1)  # Adding a small delay for scrolling
                        # Try clicking the button, handle if click is intercepted
                        try:
                            button.click()
                            
                            time.sleep(1)  
                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "artdeco-button--primary"))).click()
                            time.sleep(3)  # Wait for the popup to close
                        except ElementClickInterceptedException:
                            # If click is intercepted, log a warning and continue to the next button
                            logging.warning("Click intercepted. Skipping this button.")
                            continue
                except StaleElementReferenceException:
                    # If element becomes stale, log a warning and continue to the next button
                    logging.warning("Stale element reference. Skipping this button.")
                    continue
                except (TimeoutException, NoSuchElementException) as e:
                    # Log any other exceptions and continue to the next button
                    logging.warning(f"Error occurred: {e}")
                    continue
            last_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
    except NoSuchWindowException:
        logging.warning("Window closed unexpectedly. Terminating script.")


def follow_posts_while_scrolling(driver, keyword, follow_count_limit):
    search_url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=CLUSTER_EXPANSION"
    driver.get(search_url)

    follow_count = 0
    while follow_count < follow_count_limit:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            follow_buttons = driver.find_elements(By.CLASS_NAME, "follow")
            for button in follow_buttons:
                try:
                    button.click()
                  
                    time.sleep(3)
                    follow_count += 1
                    if follow_count >= follow_count_limit:
                        break
                except ElementClickInterceptedException:
                    logging.warning("Follow button found but not clickable. Moving to the next button.")
        except NoSuchElementException:
            logging.warning("Follow button not found. Moving to the next scroll.")


def main():
    with webdriver.Chrome() as driver:
        login_to_linkedin(driver)
        withdraw_request(driver)
        keywords = os.getenv('POSTS_FOLLOW_KEYWORDS')
       
        keyword_list = keywords.split(',')
        
        # Number of people to follow per iteration
        follow_per_iteration = os.getenv('POST_FOLLOW_COUNT')
        waiting_time =int(os.getenv('WAITING_TIME'))
        while True:
            for keyword in keyword_list:
                follow_posts_while_scrolling(driver, keyword, int(follow_per_iteration))
                time.sleep(3)
            current_time = datetime.now().strftime("%H:%M:%S")  # Format current time
            print("now waiting for ",waiting_time," sec and current time is =>  ", current_time)
            time.sleep(waiting_time) 



if __name__ == "__main__":
    main()

