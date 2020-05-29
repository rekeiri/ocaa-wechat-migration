from auth import get_oauth_session
import time
import os
import requests

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
            return access_token


print(time.time())

#if token is not valid, retrieve new token, or else make session with old token
if is_access_token_valid():
    print("access token valid")
    access_token = get_access_token()
    session = requests.Session()#not sure if this code is correct
    headers = {"Authorization": "Bearer: " + access_token}
    session.headers.update = headers
else:
    print("access token not valid, getting new session")
    session = get_oauth_session()



def get_posts(session):
    get_url = "https://ohiocaa.org/wp-json/wp/v2/posts"
    r = session.get(get_url)
    print(r)
    print(r.text)
    print(r.headers)
    print("DONE")
    print()
    print("-----------------------")



def create_post(session, date, status, title, content, category):
    post_url = "https://ohiocaa.org/wp-json/wp/v2/posts"
    data = {"date": date, "status": status, "title": title, "content": content, "category": category}
    r = session.post(post_url, data = data)
    print(r)
    print(r.text)
    print(r.headers)
    print("DONE")
    print()
    print("-----------------------")



#create_post(session, "2020-5-28", "published", "test", "this is a test post", "APAPA Ohio Posts")

get_posts(session)