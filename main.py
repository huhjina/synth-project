import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import math


url = "https://www.norduserforum.com/index.php"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
forums = []
pages = []
posts = []
#Get all subforum links
links = soup.find_all('a', class_= 'forumtitle')
for link in links:
    href = re.sub(r'&sid=[^&]+', '', link['href'])
    href = href.lstrip('.')
    full_url = f"https://www.norduserforum.com{href}"
    forums.append(full_url)
    # print(full_url)

#get all pages links from each subforum
for link in forums:
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('div', class_ = 'pagination')
    page = pagination.find_all(string = re.compile("topics"))
    for topic_num in page:
        match = re.search(r"(\d+) topics", topic_num)
        page_num= math.ceil(int(match.group(1))/50)
    #print(page_num)
    for i in range(0,page_num):
        pages.append(f"{link}&start={i*50}")
print(len(pages))

#Get all post links from each page
for page in pages:
    response = requests.get(page)
    soup = BeautifulSoup(response.content, 'html.parser')
    titles = soup.find_all('a', class_='topictitle')
    for idx, title in enumerate(titles):
        if idx >= 1:
            break
        href = title['href']
        href = href.lstrip('.')
        full_url = f"https://www.norduserforum.com{href}"
        print(full_url)
        posts.append(full_url)
print(len(posts))


