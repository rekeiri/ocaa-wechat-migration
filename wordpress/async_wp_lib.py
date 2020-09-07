import requests
from .credentials import username, password
import aiohttp
import asyncio
from utils import writeline_to_log_async


class WordPressLib():
    def __init__(self):
        self.base_url = "http://www.ohiocaa.org"
        #using the application passwords pluginpip 
        self.auth = aiohttp.BasicAuth(username, password)#session requries BasicAuth() tuple, not a normal tuple
        #wp server appears to have a limit on number of requests -> ends up getting SeverDisconnectError or Content Type Error since server returns 500 internal server error, connection: close
        #was fine after increasing php memory limit. Default = 32MB, increased to 256MB.
        #32 could handle about 20, 256 should be able to handle 160 theoretically.
        #also getting winerror 121 semaphore timeout at 50. Just keep at 20.
        connector = aiohttp.TCPConnector(limit_per_host=20)

        #https://github.com/aio-libs/aiohttp/issues/3904
        #https://github.com/aio-libs/aiohttp/issues/850
        self.session = aiohttp.ClientSession(connector = connector, headers={'Connection': 'keep-alive'}) 


    async def get_categories(self):
        url = self.base_url + "/wp-json/wp/v2/categories"
        #think max is 100, assume we won't exceed this number
        url += '?per_page=100'
        async with self.session.get(url, auth = self.auth) as response:
            return await response.json()
        ''' This syntax is also okay
        response = await self.session.get(url, auth = self.auth)
        return await response.json() #still need await here. Else, in get_category_id, we get 'coroutine' object is not iterable
        '''
    
    async def get_category_id(self, category_name):
        for category in await self.get_categories():
            if category["name"] == category_name:
                category_id = int(category["id"])
                return category_id

    async def get_number_posts(self, category_id = None):
        url = self.base_url + f"/wp-json/wp/v2/posts?per_page=1"
        if category_id:
            url += f"&categories={category_id}"
        async with self.session.get(url, auth = self.auth) as response:
            return response.headers['X-WP-Total']
        
    
    async def get_posts(self, page, category_id):
        url = self.base_url+"/wp-json/wp/v2/posts"
        url += f"?page={page}&per_page=100&categories={category_id}"
        async with self.session.get(url, auth = self.auth) as response:
            return await response.json()
    
    async def get_number_images(self, search_string = None):
        url = self.base_url + "/wp-json/wp/v2/media"
        url += f"?page=1&per_page=1"
        if search_string:
            url += f"&search={search_string}"
        async with self.session.get(url, auth = self.auth) as response:
            return response.headers['X-WP-Total']

    async def get_images(self, page, search_string = None):
        url = self.base_url + "/wp-json/wp/v2/media"
        url += f"?page={page}&per_page=100"
        if search_string:
            url += f"&search={search_string}"
        async with self.session.get(url, auth = self.auth) as response:
            return await response.json()
    
    #Date format requirement:
    #"date":"2020-06-03T22:20:23", otherwise we can use None
    def create_date(self, year, month, day, hour = 12, minute = 0, second = 0):
        return f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"

    async def upload_pic(self, file, date, status, title):
        url = self.base_url + "/wp-json/wp/v2/media"
        data = {"date": date, "status": status, "title": title}
        #wp will throw err 500 if this is not 'file'
        files = {'file': open((file),'rb')}
        async with self.session.post(url, data = data, files = files, auth = self.auth) as response:
            return await response.json()
    
    async def delete_image(self, image_id):
        print(f'deleting image: {image_id}')
        url = self.base_url + f"/wp-json/wp/v2/media/{image_id}"
        data = {"force":True}#bypass trash and directly delete image
        async with self.session.delete(url, data = data, auth = self.auth) as response:
            try:
                r = await response.json()
                print(f'done deleting image: {image_id}')
            except:
                await writeline_to_log_async(str(response))
                raise Exception("wrote error to log")


    async def delete_post(self, post_id):
        print(f'deleting post: {post_id}')
        url = self.base_url + f"/wp-json/wp/v2/posts/{post_id}"
        data = {"force":True}#bypass trash and directly delete post
        async with self.session.delete(url, data = data, auth = self.auth) as response:
            try:
                r = await response.json()
                print(f'done deleting post: {post_id}')
            except:
                await writeline_to_log_async(str(response))
                raise Exception("wrote error to log")
    
    async def close_session(self):
        await self.session.close()



    

