# from selenium import webdriver
# from selenium.webdriver.common.keys import keys
# import time

# driver = 

from selenium import webdriver
import os
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dotenv import load_dotenv

load_dotenv()

# options = Options()

# options.add_argument("--window-size=1920,1080")

# options.add_experimental_option("detach", True)

# driver = webdriver.Chrome(options=options)
# driver.get("https://www.youtube.com/")

class Browser:
    def __init__(self, driver=None):
        if driver is not None:
            self.browser = driver
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            driver_path = os.path.join(dir_path, 'chromedriver')

            options = Options()
            options.add_experimental_option("detach", True)

            self.service = Service(executable_path=driver_path)
            self.browser = webdriver.Chrome(service=self.service, options=options)

    def openpage(self, url):
        self.browser.get(url)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))


    def close_browser(self):
        self.browser.close()
    
    def add_input(self, by, value, text):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)
        time.sleep(2)

    def click_button(self, by, value):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        time.sleep(2)

    def click_remember(self):
        try:
            remember_button = WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.ID, "j_username"))
            )
            remember_button.click()
        except Exception as e:
            print(f"{e}")

    def check_need_login(self):
        try:
            self.browser.find_element(By.ID, "logged_in_element_id")
            print("Already logged in.")
            return True
        except NoSuchElementException:
            return False

    def login_bu(self, username, password):
        if self.check_need_login():
            print("No need to login.")
            return
        
        try:
            username_field = self.browser.find_element(By.ID, "j_username")
            password_field = self.browser.find_element(By.ID, "j_password")

            username_field.send_keys(username)
            password_field.send_keys(password)

            self.browser.find_element(By.CLASS_NAME, "input-submit").click()

            self.wait_for_auth()

            self.click_remember_device()

            WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "element_after_login"))
            )
            print("Logged in successfully.")

            self.click_remember()

        except TimeoutException as e:
            print("Timeout while waiting for login elements: ", e)
            print("Page source:", self.browser.page_source[:2000])  # print first 2000 characters of the page source
        except NoSuchElementException as e:
            print("Element not found on the page: ", e)
            print("Page source:", self.browser.page_source[:2000])  # print first 2000 characters of the page source
        except Exception as e:
            print("An error occurred during login: ", e)
    
    def wait_for_auth(self):
        try:
            WebDriverWait(self.browser, 100).until(
                EC.presence_of_all_elements_located((By.ID, "post_login_element"))
            )
            print("login success")
        except:
            print("Auth error, duo manual step")
    # def login_if_required(self):
    #     try:
    #         username_field = self.browser.find_element(By.ID, "j_username")
    #         password_field = self.browser.find_element(By.ID, "j_password")
    #         username_field.send_keys(os.getenv('USERNAME'))
    #         password_field.send_keys(os.getenv('PASSWORD'))
    #         login_button = self.browser.find_element(By.CLASS_NAME, "input-submit")
    #         login_button.click()

    #         WebDriverWait(self.browser, 10).until(
    #             EC.presence_of_element_located((By.ID, "duo_iframe"))
    #         )

    #         try:
    #             remember_button = WebDriverWait(self.browser, 5).until(
    #                 EC.element_to_be_clickable((By.ID, "trust-browser-button"))
    #             )
    #             remember_button.click()
    #         except TimeoutException:
    #             print("No 'Remember Device' button found.")
    #     except NoSuchElementException:
    #         print("Already logged in or no login needed.")


def perform_login():
    browser = Browser()

    # TEST URL
    base_url = os.getenv("BASE_URL")
    course_id = "102484"
    term = "2248"
    crse_offer_nbr = "1"

    course_url = base_url.format(course_id=course_id, term=term, crse_offer_nbr=crse_offer_nbr)

    browser.openpage(course_url)
    print(course_url)
    time.sleep(3)

    my_username = os.getenv('USERNAME')
    my_password = os.getenv('PASSWORD')
    browser.login_bu(my_username, my_password)
    time.sleep(10)

    browser.click_remember()

    time.sleep(10)
    browser.close_browser()



