# from selenium import webdriver
# from selenium.webdriver.common.keys import keys
# import time

# driver = 

from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_argument("--window-size=1920,1080")

options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://www.youtube.com/")



