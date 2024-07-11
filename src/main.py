import requests
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import login
import user_profile
import json
from scraper import Scraper

load_dotenv()

def test_link(driver):
    test_link = os.getenv("TEST_LINK")

    driver.get(test_link)

    old_data = driver.find_element(By.TAG_NAME, "body").text
    data = json.loads(old_data)
    print(data)
    return data


def main():
    # use profile
    driver = user_profile.create_driver()
    browser = login.Browser(driver)

    # login.py
    # browser.openpage(os.getenv("TEST_LINK"))
    url_to_access = os.getenv("TEST_LINK")

    browser.login_bu(url_to_access ,os.getenv('USERNAME'), os.getenv('PASSWORD'))

    # get data
    data = test_link(driver)

    # close after
    driver.quit()


if __name__ == "__main__":
    # login initial from login.py
    # login.main()
    # test_link()
    main()



