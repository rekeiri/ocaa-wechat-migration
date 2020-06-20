from wechat.parse import Parser
from wechat.config import uin as w_uin, key as w_key, biz as w_biz
import os
import re

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

