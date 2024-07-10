import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import login

load_dotenv()

def test_link():
    os.getenv("TEST_LINK")

    r = requests.get(test_link)

    response = r.json()
    print(response)


def main():
    











if __name__ == "__main__":

    # login initial from login.py
    login.main()
    test_link()

    main()



