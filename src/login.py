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
from dotenv import load_dotenv

load_dotenv()

# options = Options()

# options.add_argument("--window-size=1920,1080")

# options.add_experimental_option("detach", True)

# driver = webdriver.Chrome(options=options)
# driver.get("https://www.youtube.com/")




class Browser:
    # browser, service = None, None

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        driver_path = os.path.join(dir_path, 'chromedriver')

        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("detach", True)

        self.service = Service(executable_path=driver_path)
        self.browser = webdriver.Chrome(service=self.service, options=options)

    def openpage(self, url):
        self.browser.get(url)

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
                EC.presence_of_element_located((By.ID, "trust-browser-button"))
            )
            remember_button.click()
        except Exception as e:
            print(f"{e}")

    def login_bu(self, username, password):
        self.add_input(by=By.ID, value="j_username", text=username)
        self.add_input(by=By.ID, value="j_password", text=password)
        self.click_button(by=By.CLASS_NAME, value="input-submit")


if __name__ == "__main__":
    browser = Browser()

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
    



