from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
from login import Browser
import json

class Scraper:
    def __init__(self, browser):
        self.browser = browser

    def openpage(self, url):
        self.browser.get(url)
        if self.check_need_login():
            self.login_bu(url)

    def check_need_login(self):
        try:
            self.browser.find_element(By.ID, "j_username")
            return True
        except NoSuchElementException:
            return False
        
    def login_bu(self, url):
        self.browser.openpage(url)

        if self.check_need_login():
            username_field = self.browser.find_element(By.ID, "j_username")
            password_field = self.browser.find_element(By.ID, "j_password")
            username_field.send_keys(username)
            password_field.send_keys(password)

            self.browser.find_element(By.CLASS_NAME, "input-submit").click()

            try:
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.ID, "auth-view-wrapper"))
                )
                print("push duo manually now")
                WebDriverWait(self.browser, 20).until(
                    EC.presence_of_element_located((By.ID, "trust-browser-button"))
                )
                self.click_remember()
            except TimeoutException:
                print("No duo needed, logged in")
        else:
            print("didn't need login")


    def get_json_from_page(self, url):
        self.openpage(os.getenv(url))

        json_wrap = self.browser.browser.find_element(By.TAG_NAME, 'pre').text
        return json.loads(json_wrap)

    def get_all_majors(self):
        return self.get_json_from_page(self.browser, os.getenv("CATALOG"))

    def get_courses_from_major(self, major):
        courses_url = os.getenv("COURSES_IN_MAJOR").format(major=major)
        return self.get_json_from_page(self.browser, courses_url)
    
    def get_complementary_details(self, course_id, effdt, subject, catalog_nbr, typ_offr):
        complementary_url = os.getenv("COMPLEMENTARY_COURSE_LINK").format(
            course_id=course_id,
            effdt=effdt,
            crse_offer_nbr="1",
            subject=subject,
            catalog_nbr=catalog_nbr,
            typ_offr=typ_offr
        )
        return self.get_json_from_page(complementary_url)

    def get_course_details(self, course_id, term, crse_offer_nbr):
        course_details_url = os.getenv("COURSE_LINK").format(course_id=course_id, term=term, crse_offer_nbr=crse_offer_nbr)
        primary_details = self.get_json_from_page(self.browser, course_details_url)