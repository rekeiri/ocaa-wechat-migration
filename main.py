import os
import re
from wechat.parser import Parser
from wechat.config import uin as w_uin, key as w_key, biz as w_biz
from wordpress.wp_auth_library import WPAuthLibrary
try:
    from wordpress.config import access_token, expires_at
except:
    access_token, expires_at = None, None


#wechat code
parser = Parser(w_biz, w_uin, w_key)

#grab all wechat articles, download them to folder
#parser.download_all_html

#grab article(s) names
file_path = os.path.dirname(__file__)
dirname = os.path.join(file_path, ".\\wechat\\articles")
articles = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]

#for test, only take first article
articles = articles[0:1]

for article in articles:
    article_path = os.path.join(dirname, article)

    #get article string
    f = open(article_path, "r", encoding = "utf-8")
    article_string = f.read()
    f.close()

    #start scraping the text/images
    article_string = parser.get_html_and_images(article_string)


    #write new formatted file
    print("writing file")
    f = open(re.sub("articles", "modified_articles", article_path), "w", encoding = "utf-8")
    f.write(article_string)
    f.close()



#WordPress code
wp_auth_lib = WPAuthLibrary(access_token, expires_at)

category_id = wp_auth_lib.get_category_id("APAPA Ohio Posts")
my_date = wp_auth_lib.create_date(2020, 5, 28, 0, 0, 0) # should be "2020-05-28T00:00:00"
print(my_date)
#wp_auth_lib.create_post(my_date , "publish", "test", "this is a test post", [category_id])

'''
r = wp_auth_lib.get_posts()
print(len(r))
for post in r:
    print()
    print(post)
'''