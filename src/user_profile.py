from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
from dotenv import load_dotenv

load_dotenv()

def create_driver(profile_directory, driver_path):
    options = Options()
    options.add_argument(f"user-data-dir={os.getenv("USER_PROFILE")}")

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver



