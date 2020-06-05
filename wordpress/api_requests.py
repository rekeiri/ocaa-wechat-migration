from auth import get_oauth_session
import time
import os
import requests
import datetime

'''
appears to have an error with authenticating through bearer token in request header
does seem to work by appending token as a query string
e.g. https://ohiocaa.org/wp-json/wp/v2/posts/?access_token=gpcmbiyshd7yhw3gxatdwpst9bdtltbm4fuepfcs
'''

def is_access_token_valid():
    access_token_exists = False
    expiration_time_exists = False
    expiration_time_valid = False
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "config.py")
    f = open(filename, "r") 
    for line in f.readlines():
        if line.startswith("access_token ="):
            access_token_exists = True
        elif line.startswith("expires_at = "):
            expiration_time_exists = True
            expiration_time = line.strip()
            expiration_time = float(expiration_time.split()[-1])
    if expiration_time_exists:
        if time.time()<expiration_time:
            expiration_time_valid = True
    f.close()
    return access_token_exists and expiration_time_exists and expiration_time_valid

def get_access_token():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "config.py")
    f = open(filename, "r") 
    for line in f.readlines():
        if line.startswith("access_token ="):
            access_token = line.strip().split()[-1]
            #because we didn't import it but read it directly, it reads it as a string instead, so need to strip quotes
            access_token = access_token.strip('"')
            return access_token


print(time.time())

#if token is not valid, retrieve new token, or else make session with old token
if is_access_token_valid():
    print("access token valid")
    access_token = get_access_token()
    session = requests.Session()#not sure if this code is correct
    headers = {"Authorization": "Bearer: " + access_token}
    session.headers.update(headers)
    print(session.headers)
    print("done validating access token and creating session")
else:
    print("access token not valid, getting new session")
    session = get_oauth_session()
    access_token = session.access_token
    print(access_token)

def get_categories(session, access_token):
    url = "https://ohiocaa.org/wp-json/wp/v2/categories"
    url += "?access_token="+access_token
    r = session.get(url)
    return r.json()

def get_posts(session, access_token):
    url = "https://ohiocaa.org/wp-json/wp/v2/posts"
    url += "?access_token="+access_token
    r = session.get(url)
    return r.json()


def create_post(session, access_token, date, status, title, content, categories):
    url = "https://ohiocaa.org/wp-json/wp/v2/posts"
    url += "?access_token="+access_token 
    data = {"date": date, "status": status, "title": title, "content": content, "categories": categories}
    r = session.post(url, data = data)
    print("Done Creating Post")

def create_date(year, month, day):
    return ""


categories = get_categories(session, access_token)

#getting category id
category_id = 0
for category in categories:
    if category["name"] == "APAPA Ohio Posts":
        category_id = int(category["id"])
        break

#Date format requirement:
#"date":"2020-06-03T22:20:23", otherwise we can pass in None
#category is a list of integers, likely of the id number that belongs to each category
print("category id: " + str(category_id))

create_post(session, access_token, "2020-05-28T00:00:00" , "publish", "test", "this is a test post", [category_id])

'''
r = get_posts(session, access_token)
print(len(r))
for post in r:
    print()
    print(post)
'''
