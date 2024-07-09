import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# login process
login_url = 'https://mybustudent.bu.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1'  # Modify this as needed
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

session = requests.Session()

initial_page = session.get(login_url)
initial_content = initial_page.text

soup = BeautifulSoup(initial_content, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')

login_data = {
    'j_username': username,
    'j_password': password,
    'csrf_token': csrf_token
}

login_response = session.post(login_url, data=login_data)

if login_response.ok:
    # base_url = os.getenv("COURSE_LINK")
    print(login_response.text)
    base_url = os.getenv("BASE_URL")

    # test 101
    course_id = "102484"
    term = "2248"
    crse_offer_nbr = "1"

    course_url = base_url.format(course_id=course_id, term=term, crse_offer_nbr=crse_offer_nbr)

    response = requests.get(course_url)

    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code}")
else:
    print("login failed")
    print(login_response.text) 

