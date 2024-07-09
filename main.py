import requests
import os
from dotenv import load_dotenv

load_dotenv()

link = os.getenv('BU_LINK')
print(link)

r = requests.get(link)
print(r)