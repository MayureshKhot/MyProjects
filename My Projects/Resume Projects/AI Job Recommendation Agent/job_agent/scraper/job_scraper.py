import requests
from bs4 import BeautifulSoup
import config

jobs_list = []

url = config.TARGET_URL
def scrape_jobs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    job_postings = soup.find_all('a', class_='zReHs')
    for posting in job_postings:
        