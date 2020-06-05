from wechat.parse import parse
from wechat.config import uin as w_uin, key as w_key, biz as w_biz
import os

#grab all wechat articles, download them to folder
'''
index = 1
while(parse(index, w_biz, w_uin, w_key)):
    index += 1
'''

#for each article, grab all the images and upload them to wordpress
#change the article to reflect the new image sources
#change the "data-src" tag to "src" so the img is properly displayed
#sometimes there are links to recent articles toward bottom of page, so we would need to relace those links with the new links of posts on wordpress
#cant really remove any of the javascript, because some is used to display the actual page content
#need to test if pasting the entirety of the html files works in wordpress
#would like a database to correlate new article links with old links for easy replacement
#maybe also store new img links with old img links?

#so html has a lot of obfuscated js in there. What we want is really just result of copy the article and pasting into word or something (but with the imgs working)
#how can we do that-copy and pasting imgs work if we just change the data-src to src

dirname = os.path.dirname(__file__)
dirname = os.path.join(dirname, ".\\wechat\\articles")
#print(dirname)
#print(os.listdir(dirname))
files = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]
print(files)