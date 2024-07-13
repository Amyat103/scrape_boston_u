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
            self.browser = webdriver.Chrome(options=options)

    def openpage(self, url):
        print(url)
        self.browser.get(url)
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("Failed to load the login page. Current URL:", self.browser.current_url)
        
        return self.browser.current_url

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
            remember_button = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "trust-browser-button"))
            )
            remember_button.click()
        except Exception as e:
            print(f"{e}")

    def check_need_login(self):
        try:
            self.browser.find_element(By.ID, "j_username")
            print("Needs to login")
            return True
        except NoSuchElementException:
            return False

    def login_bu(self, url, username, password):

        access_url = self.openpage(url)

        if self.check_need_login():
            print(self.browser.current_url)
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
        
        return access_url
    
    def wait_for_auth(self):
        try:
            WebDriverWait(self.browser, 100).until(
                EC.presence_of_all_elements_located((By.ID, "post_login_element"))
            )
            print("login success")
        except:
            print("Auth error, duo manual step")



# ONLY FOR TESTING BROWSER CLASS
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



