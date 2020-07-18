from .auth import get_oauth_session
import time
import os
import requests
import datetime

'''
wp-oauth plugin appears to have an error with authenticating through bearer token in request header
does seem to work by appending token as a query string
e.g. https://ohiocaa.org/wp-json/wp/v2/posts/?access_token=gpcmbiyshd7yhw3gxatdwpst9bdtltbm4fuepfcs

authorizing requires logging into wordpress site
'''


class WPAuthLibrary():
    def __init__(self, access_token = None, token_expiration_time = None):
        self.base_url = "https://ohiocaa.org"
        self.access_token = access_token
        self.token_expiration_time = token_expiration_time
        if self.is_access_token_valid():
            self.session = requests.Session()#not sure if this code is correct
            headers = {"Authorization": "Bearer: " + access_token}
            self.session.headers.update(headers)
        else:
            self.update_token()

    def update_token(self):
        self.session = get_oauth_session() #includes writing token to config.py
        self.access_token = self.session.access_token

    def is_access_token_valid(self):
        access_token_exists = False
        expiration_time_exists = False
        expiration_time_valid = False
        if self.access_token:
            access_token_exists = True
        if self.token_expiration_time:
            expiration_time_exists = True
        if expiration_time_exists and time.time()<self.token_expiration_time:
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
        url = self.base_url + "/wp-json/wp/v2/categories"
        url += "?access_token="+self.access_token
        r = self.session.get(url)
        return r.json()

    def get_category_id(self, category_name):
        for category in self.get_categories():
            if category["name"] == category_name:
                category_id = int(category["id"])
                return category_id

    #also doesn't work with dictionary of arguments
    def get_posts(self, page, category):
        url = self.base_url+"/wp-json/wp/v2/posts"
        url += "?access_token="+self.access_token
        url += f"&page={page}"
        url += f"&per_page=100"
        url += f"&categories={category}"
        r = self.session.get(url)
        return r.json()
    
    #for some reason, this endpoint doesn't work with attaching a dictionary of arguments
    def get_images(self, page, search_string):
        url = self.base_url + "/wp-json/wp/v2/media"
        url += "?access_token="+self.access_token
        url += f"&page={page}"
        url += f"&search={search_string}"
        url += f"&per_page=100"
        r = self.session.get(url)
        return r.json()

    def create_post(self, date, status, title, content, categories, excerpt = None):
        url = self.base_url+"/wp-json/wp/v2/posts"
        url += "?access_token="+self.access_token 
        data = {"date": date, "status": status, "title": title, "content": content, "categories": categories, "excerpt":excerpt}
        r = self.session.post(url, data = data)
        print(r.status_code)

    #Date format requirement:
    #"date":"2020-06-03T22:20:23", otherwise we can use None
    def create_date(self, year, month, day, hour = 12, minute = 0, second = 0):
        return f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"

    #example of url: http://www.ohiocaa.org/wp-content/uploads/2018/04/ocaa-david.png
    #example in other languages: https://gist.github.com/ahmadawais/0ccb8a32ea795ffac4adfae84797c19a 
    #resultant url = https://www.ohiocaa.org/wp-content/uploads/{year}/{month}/filename.{file_ext}
    #if the same title is uploaded twice, it will go filename-1.{file_ext}
    #the response contains the url

    def upload_pic(self, file, date, status, title):
        url = self.base_url + "/wp-json/wp/v2/media"
        url += "?access_token="+self.access_token
        data = {"date": date, "status": status, "title": title}
        #wp will throw err 500 if this is not 'file'
        files = {'file': open((file),'rb')}
        r = self.session.post(url, data = data, files = files)
        return r

    def delete_image(self, image_id):
        url = self.base_url + f"/wp-json/wp/v2/media/{image_id}"
        url += "?access_token="+self.access_token
        data = {"force":True}#bypass trash and directly delete image
        r = self.session.delete(url, data = data)

    def delete_post(self, post_id):
        url = self.base_url + f"/wp-json/wp/v2/posts/{post_id}"
        url += "?access_token="+self.access_token
        data = {"force":True}#bypass trash and directly delete image
        r = self.session.delete(url, data = data)





