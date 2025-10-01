import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import math


url = "https://www.norduserforum.com/index.php"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
post_data = []
unique_id = 1
links = soup.find_all('a', class_= 'forumtitle')
for link in links:
    href = re.sub(r'&sid=[^&]+', '', link['href'])
    href = href.lstrip('.')
    forum_url = f"https://www.norduserforum.com{href}"
    print(forum_url)
    forum_id = forum_url.split('=')[-1]
    response = requests.get(forum_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('div', class_ = 'pagination')
    page = pagination.find_all(string = re.compile("topics"))
    for topic_num in page:
        match = re.search(r"(\d+) topics", topic_num)
        page_num= math.ceil(int(match.group(1))/50)
    for i in range(0, min(page_num, 1)):
        forum_page_url = f"{forum_url}&start={i*50}"
        print(forum_page_url)
        response = requests.get(forum_page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = soup.find_all('a', class_='topictitle')
        # Only process the first thread for testing
        for idx, title in enumerate(titles):
            if idx > 0:
                break
            post_ids = []
            href = title['href']
            href = href.lstrip('.')
            thread_url = f"https://www.norduserforum.com{href}"
            print(thread_url)
            thread_id = thread_url.split('=')[-1]
            response = requests.get(thread_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            for div in soup.find_all('div', class_='post'):
                post_id = div['id']
                post_ids.append(post_id)
            for post_id in post_ids:
                post_div = soup.find('div', id=post_id)
                user_link = post_div.find('span', class_='responsive-hide')
                if user_link and user_link.find('a', href=True):
                    username = user_link.find('a').get_text(strip=True)
                    href = user_link.find('a')['href']
                    if "u=" in href:
                        unique_user_id = href.split("u=")[-1].split("&")[0]
                    else:
                        unique_user_id = "unknown"
                else:
                    username_tag = post_div.find('span', class_='username')
                    username = username_tag.get_text(strip=True) if username_tag else "Unknown"
                    unique_user_id = "deleted"
                datetime = post_div.find('time')['datetime']
                h3tag = post_div.find('h3') if post_div else None
                href = h3tag.find('a', href = True)['href'] if h3tag and h3tag.find('a', href=True) else ''
                href = href.lstrip('.')
                post_link = f"https://www.norduserforum.com{href}" if href else ''
                if post_div and post_div.find('h3', class_='first'):
                    is_it_a_reply = False
                    reply_to = ''
                    first_post = post_link
                else:
                    is_it_a_reply = True
                    reply_to = first_post if 'first_post' in locals() else ''
                if is_it_a_reply:
                    title = f"RE: {soup.find('h2', class_='topic-title').get_text(strip=True)}" if soup.find('h2', class_='topic-title') else ''
                else:
                    title = soup.find('h2', class_='topic-title').get_text(strip=True) if soup.find('h2', class_='topic-title') else ''
                post_data.append({
                    'unique_id': unique_id,
                    'forum_id': forum_id,
                    'thread_id': thread_id,
                    'views': '',
                    'replies': '',
                    'post_id': post_id,
                    'title': title,
                    'unique_user_id': unique_user_id,
                    'username': username,
                    'datetime': datetime,
                    'is_it_a_reply': is_it_a_reply,
                    'reply_to': reply_to,
                    'post_content': post_div.find('div', class_='content').get_text(strip=True) if post_div and post_div.find('div', class_='content') else '',
                    'post_link': post_link
                })
                unique_id += 1

df = pd.DataFrame(post_data)
df.to_csv('norduserforum_data.csv', index=False)



    # print(full_url)

# #get all pages links from each subforum
# for link in forums:
#     response = requests.get(link)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     pagination = soup.find('div', class_ = 'pagination')
#     page = pagination.find_all(string = re.compile("topics"))
#     for topic_num in page:
#         match = re.search(r"(\d+) topics", topic_num)
#         page_num= math.ceil(int(match.group(1))/50)
#     #print(page_num)
#     for i in range(0,page_num):
#         pages.append(f"{link}&start={i*50}")
# print('pages:', len(pages))

# #Get all post links from each page
# for page in pages:
#     response = requests.get(page)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     titles = soup.find_all('a', class_='topictitle')
#     for idx, title in enumerate(titles):
#         if idx >= 1:
#             break
#         href = title['href']
#         href = href.lstrip('.')
#         full_url = f"https://www.norduserforum.com{href}"
#         print(full_url)
#         posts.append(full_url)
# print('posts', len(posts))

# for post_id in post_ids:
#     post_div = soup.find('div', id=post_id)
#     username = post_div.find('a', class_='username')
#     datetime = post_div.find('time')['datetime']
#     h3tag = post_div.find('h3')
#     href = h3tag.find('a', href = True)['href']
#     href = href.lstrip('.')
#     post_link = f"https://www.norduserforum.com{href}"
#     print(post_link)
#     if post_div.find('h3', class_='first'):
#         is_it_a_reply = False
#         reply_to = ''
#         first_post = post_link
#     else:
#         is_it_a_reply = True
#         reply_to = first_post
#     if is_it_a_reply:
#         title = f"RE: {soup.find('h2', class_='topic-title').get_text(strip=True)}"
#     else:
#         title = soup.find('h2', class_='topic-title').get_text(strip=True)
#     #Removed unique_user_id because there is no user id on the forum
#     #Could supplement with link to user profile if needed
#     post_data.append({
#         'unique_id': unique_id,
#         'forum_id': '',
#         'thread_id': '',
#         'views': '',
#         'replies': '',
#         'post_id': post_id,
#         'title': title,
#         'username': username,
#         'datetime': datetime,
#         'is_it_a_reply': is_it_a_reply,
#         'reply_to': reply_to,
#         'post_content': post_div.find('div', class_='content').get_text(strip=True),
#         'post_link': post_link
#     })
#     unique_id += 1

