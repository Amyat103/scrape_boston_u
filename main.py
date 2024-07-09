import requests
import os
from dotenv import load_dotenv

load_dotenv()

# link = os.getenv('BU_LINK')
# print(link)
# catalog = os.getenv('COURSE_CATALOG')

course_link = os.getenv("COURSE_LINK")

# r = requests.get(link)
# print(r)

r = requests.get(course_link)
soup = BeautifulSoup(r.content, 'lxml')
# print(response)