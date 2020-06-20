from auth import get_oauth_session
import time
import os
import requests
import datetime

'''
wp-oauth plugin appears to have an error with authenticating through bearer token in request header
does seem to work by appending token as a query string
e.g. https://ohiocaa.org/wp-json/wp/v2/posts/?access_token=gpcmbiyshd7yhw3gxatdwpst9bdtltbm4fuepfcs
'''


class WPAuthLibrary():
    def __init__(self, access_token = None, token_expiration_time = None):
        self.access_token = access_token
        self.token_expiration_time = token_expiration_time
        if self.is_access_token_valid():
            self.session = requests.Session()#not sure if this code is correct
            headers = {"Authorization": "Bearer: " + access_token}
            session.headers.update(headers)
        else:
            update_token()

    def update_token(self):
        self.session = get_oauth_session() #includes writing token to config.py
        self.access_token = session.access_token

    def is_access_token_valid(self):
        access_token_exists = False
        expiration_time_exists = False
        expiration_time_valid = False
        if self.access_token:
            access_token_exists = True
        if self.token_expiration_time:
            expiration_time_exists = True
        if expiration_time_exists and time.time()<expiration_time:
                expiration_time_valid = True
        '''
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
        f.close()
        '''
        return access_token_exists and expiration_time_exists and expiration_time_valid

    def get_access_token(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "config.py")
        f = open(filename, "r") 
        for line in f.readlines():
            if line.startswith("access_token ="):
                access_token = line.strip().split()[-1]
                #because we didn't import it but read it directly, it reads it as a string instead, so need to strip quotes
                self.access_token = access_token.strip('"')

    #category is a list of integers, likely of the id number that belongs to each category
    def get_categories(self):
        url = "https://ohiocaa.org/wp-json/wp/v2/categories"
        url += "?access_token="+self.access_token
        r = self.session.get(url)
        return r.json()

    def get_category_id(self, category_name):
        for category in self.get_categories:
            if category["name"] == category_name:
                category_id = int(category["id"])
                return category_id

    def get_posts(self):
        url = "https://ohiocaa.org/wp-json/wp/v2/posts"
        url += "?access_token="+self.access_token
        r = self.session.get(url)
        return r.json()


    def create_post(self, date, status, title, content, categories):
        url = "https://ohiocaa.org/wp-json/wp/v2/posts"
        url += "?access_token="+self.access_token 
        data = {"date": date, "status": status, "title": title, "content": content, "categories": categories}
        r = self.session.post(url, data = data)

    #Date format requirement:
    #"date":"2020-06-03T22:20:23", otherwise we can use None
    def create_date(self, year, month, day, hour = 12, minute = 0, second = 0):
        return f"{year}-{month:02d}T{hour:02d}:{min:02d}:{second:02d}"







