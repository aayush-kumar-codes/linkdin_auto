import os
import re
import time
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
import logging
import smtplib

load_dotenv()

conn = psycopg2.connect(database=os.getenv('NAME'),
                        user=os.getenv('USER'),
                        host=os.getenv('HOST'),
                        password=os.getenv('PASSWORD'),
                        port=os.getenv('PORT'))

cur = conn.cursor()


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


def scrape_linkedin_posts(driver, keyword):
    search_url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&sortBy=%22date_posted%22"
    driver.get(search_url)

    for _ in range(int(os.getenv('scroll'))):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    post_elements = driver.find_elements(By.XPATH, "//div[@role='region']")
    post_urns = list(set([post.get_attribute("data-urn") for post in post_elements if post.get_attribute("data-urn")]))
    return post_urns


def extract_email(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_skills(text):
    skills_list = ['Python', 'Java', 'JavaScript', 'React', '.NET', 'HTML', 'CSS', 'SQL', 'Machine Learning']
    skills_pattern = '|'.join(skills_list)
    matches = re.findall(skills_pattern, text, flags=re.IGNORECASE)
    return matches if matches else []


def post_content(url, driver, urn):
    driver.get(url)
    print(url)
    time.sleep(10)
    post_content_loaded = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2__description")))

    post_content_element = driver.find_element(By.CLASS_NAME, "feed-shared-update-v2__description")
    linkedinprofile = driver.find_elements(By.XPATH, "//a[@class='app-aware-link  update-components-actor__image relative']")
    linkedinprofile_link = list(set([linkedin.get_attribute("href") for linkedin in linkedinprofile if linkedin.get_attribute("href")]))
    post_content = post_content_element.text
    cleaned_content = re.sub(r'#\w+', '', post_content)
    final_content = re.sub(r'hashtag', '', cleaned_content)
    final_content_remove = re.sub(r',\w+', '', final_content)
    content = "".join([s for s in final_content_remove.strip().splitlines(True) if s.strip()])
    email = extract_email(post_content)
    skills = set(extract_skills(post_content))
    string_list = [str(element) for element in skills]
    delimiter = ", "
    result_string = delimiter.join(string_list)
    if email is not None:
        linkedinjobs_select_query = "SELECT id FROM linkedin_jobs WHERE urn_id = %s;"
        cur.execute(linkedinjobs_select_query, (urn,))
        row = cur.fetchone()
        if row is None:
            linkedinjobs_insert_query = '''
            INSERT INTO linkedin_jobs (email, skills, linkedin_profile_link, post_profile, post_content, urn_id)
            VALUES (%s, %s, %s, %s, %s, %s);
            '''
            cur.execute(linkedinjobs_insert_query, (email, result_string, linkedinprofile_link, url, content, urn))
            conn.commit()
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        client = WebClient(token=slack_token)

        try:
            response = client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL"),
                text=f"Job Found E: {email} skills: {result_string}    FTE: full time  Remote: yes  Years: 10   Company: asiaselect.com.ph",
                user=os.getenv("USER")
            )

            response = client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL"),
                text=content,
                thread_ts=response['ts'],
                user=os.getenv("USER")
            )
        except SlackApiError as e:
            logging.error(f"Error posting to Slack: {e.response['error']}")

        EMAIL = """
Dear ,

I hope this email finds you well. I am writing to express my interest in the Ract Developer role at your esteemed organization.

As a seasoned web developer with 5+ years of experience, I am well-versed in the skills and technologies required for this position, including AWS Lambda, Node.js, Kafka, serverless applications, and event-driven architectures. My expertise in these areas, combined with my proficiency in AWS services, microservices, Docker, and Kubernetes, makes me an ideal candidate for this role.

I am currently a freelancer, but I am now looking for remote job opportunities that align with my skills and experience. I believe my background and passion for building robust, scalable, and efficient web applications would be a valuable asset to your team.

Please find my resume attached:

I am excited about the prospect of discussing this opportunity further and demonstrating how I can contribute to the success of your organization.

Thank you for your consideration.

Rakesh
        """
        server = smtplib.SMTP(os.getenv('EMAIL_HOST'), os.getenv('EMAIL_PORT'))
        server.connect(os.getenv('EMAIL_HOST'), os.getenv('EMAIL_PORT'))
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))

        subject = 'Applying for the job'
        message = EMAIL
        sender_email = os.getenv('EMAIL_HOST_USER')
        recipient_email = email

        server.sendmail(sender_email, recipient_email, f"Subject: {subject}\n\n{message}")
        server.quit()


def main():
    with webdriver.Chrome() as driver:
        login_to_linkedin(driver)
        keywords = os.getenv('POSTS_SEED_KEYWORDS')
        if ',' in keywords:
            for keyword in keywords.split(','):
                post_urns = scrape_linkedin_posts(driver, keyword)
        else:
            keyword = keywords
            post_urns = scrape_linkedin_posts(driver, keyword)
        keywords = os.getenv('POST_SEED_KEYWORDS')
        for keyword in keywords:
            scrape_linkedin_posts(driver, keyword)
            for urn in post_urns:
                link = f"https://www.linkedin.com/feed/update/{urn}/"
                post_content(link, driver, urn)
                time.sleep(5)


if __name__ == "__main__":
    main()
