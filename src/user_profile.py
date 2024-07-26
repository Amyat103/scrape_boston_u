import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

load_dotenv()


def create_driver():
    options = Options()
    options.add_argument(f"user-data-dir={os.getenv('USER_PROFILE')}")
    options.add_argument("--headless")  # Add this line to enable headless mode

    dir_path = os.path.dirname(os.path.realpath(__file__))
    driver_path = os.path.join(dir_path, "chromedriver")

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver
