import json
import os

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from login import Browser


def save_json_to_file(data, filename):
    os.makedirs("json", exist_ok=True)
    with open(os.path.join("json", filename), "w") as f:
        json.dump(data, f, indent=2)


class Scraper:
    def __init__(self, browser):
        self.browser = browser

    def openpage(self, url):
        print(f"Attempting to open URL: {url[-5:]}")
        self.browser.openpage(url)
        if self.check_need_login():
            print(f"Successfully opened URL: {url[-5:]}")
            self.login_bu(url)

    def check_need_login(self):
        try:
            self.browser.browser.find_element(By.ID, "j_username")
            return True
        except NoSuchElementException:
            return False

    def login_bu(self, url):
        self.browser.openpage(url)

        if self.check_need_login():
            username_field = self.browser.browser.find_element(By.ID, "j_username")
            password_field = self.browser.browser.find_element(By.ID, "j_password")

            username = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")

            username_field.send_keys(username)
            password_field.send_keys(password)

            self.browser.browser.find_element(By.CLASS_NAME, "input-submit").click()

            try:
                WebDriverWait(self.browser.browser, 10).until(
                    EC.presence_of_element_located((By.ID, "auth-view-wrapper"))
                )
                print("push duo manually now")
                WebDriverWait(self.browser.browser, 20).until(
                    EC.presence_of_element_located((By.ID, "trust-browser-button"))
                )
                self.click_remember()
            except TimeoutException:
                print("No duo needed, logged in")
        else:
            print("didn't need login")

    def get_json_from_page(self, url):
        self.openpage(url)
        json_wrap = self.browser.browser.find_element(By.TAG_NAME, "pre").text
        return json.loads(json_wrap)

    def get_all_majors(self):
        return self.get_json_from_page(os.getenv("CATALOG"))

    def get_courses_from_major(self, major):
        courses_url = os.getenv("COURSES_IN_MAJOR").format(major=major)
        data = self.get_json_from_page(courses_url)
        save_json_to_file(data, f"{major}_courses.json")
        return data

    def get_complementary_details(
        self, course_id, effdt, subject, catalog_nbr, typ_offr
    ):
        complementary_url = os.getenv("COMPLEMENTARY_COURSE_LINK").format(
            course_id=course_id.strip(),
            effdt=effdt.strip(),
            crse_offer_nbr="1",
            subject=subject.strip(),
            catalog_nbr=catalog_nbr.strip(),
            typ_offr=typ_offr.strip(),
        )
        print(f"Complementary URL: {complementary_url}")
        if not complementary_url:
            raise ValueError("Complementary URL is not formed correctly.")

        data = self.get_json_from_page(complementary_url)

        course_details = data.get("course_details", {})

        hub_attributes = []
        for attr in course_details.get("attributes", []):
            if attr.get("crse_attribute") == "HUB":
                hub_value = attr.get("crse_attribute_value_descr", "")
                if hub_value.startswith("HUB "):
                    hub_attributes.append(hub_value[4:])

        units = str(course_details.get("units_minimum", ""))

        data["processed_hub_attributes"] = hub_attributes
        data["processed_units"] = units

        return data

    def get_course_details(self, course_id, term, crse_offer_nbr):
        course_url = os.getenv("COURSE_LINK").format(
            course_id=course_id, term=term, crse_offer_nbr=crse_offer_nbr
        )
        data = self.get_json_from_page(course_url)
        return data
