from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from .login import Browser
import json

class Scraper:
    def __init__(self, browser):
        self.browser = browser

    def get_json_from_page(self, url):
        self.browser.openpage(os.getenv("CATALOG"))

        json_wrap = self.browser.browser.find_element(By.TAG_NAME, 'pre')
        return json.loads(json_wrap)

    def get_all_majors(self):
        return self.get_json_from_page(self.browser, os.getenv("CATALOG"))

    def get_courses_from_major(self, major):
        courses_url = os.getenv("COURSES_IN_MAJOR").format(major=major)
        return self.get_json_from_page(self.browser, courses_url)

    def get_course_details(self, course_id, term, crse_offer_nbr):
        course_details_url = os.getenv("COURSE_LINK").format(course_id=course_id, term=term, crse_offer_nbr=crse_offer_nbr)
        return self.get_json_from_page(self.browser, course_details_url)