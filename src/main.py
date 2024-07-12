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
    scraper = Scraper(browser)

    # login.py
    # browser.openpage(os.getenv("TEST_LINK"))
    browser.login_bu(os.getenv("TEST_LINK") ,os.getenv('USERNAME'), os.getenv('PASSWORD'))

    # get data
    majors = scraper.get_all_majors()
    print(majors)

    for major in majors['subjects']:
        print(f"working on {major['subject']}")
        courses = scraper.get_courses_from_major(major['subject'])
        for course in courses['courses']:
            comp_details = scraper.get_complementary_details(course['crse_id'], course['effdt'], major['subject'], course['catalog_nbr'].strip(), course['typ_offr'])
            term = comp_details['offerings'][0]['open_terms'][0]['strm']

            course_details = scraper.get_course_details(course['crse_id'], term, course)

            print(course_details)

    # close after
    driver.quit()


if __name__ == "__main__":
    # login initial from login.py
    # login.main()
    # test_link()
    main()



