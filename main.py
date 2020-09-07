import os
import re

import requests
import exceptions as ex
import json
from datetime import datetime

import database.main_operations as db
from wechat.parser import Parser
from wordpress.wp_auth_library import WPAuthLibrary


#constant file paths
db_path = r"C:\Users\Eric Fu\workspace\ocaa-wechat-migration\database\my_database.db"
file_path = os.path.dirname(__file__)
article_dir = os.path.join(file_path, ".\\wechat\\articles")


#initialize db
#db.delete_db(db_path)
conn = db.create_connection(db_path)
db.create_table(conn, db.image_table_sql)
db.create_table(conn, db.article_table_sql)

#constant objects
wp_auth_lib = WPAuthLibrary()
parser = Parser()

#other constants
#category_id = wp_auth_lib.get_category_id("APAPA Ohio Posts")
category_id = wp_auth_lib.get_category_id("俄州亚太联盟公众号文章列表")
categories = wp_auth_lib.get_categories()
for category in categories:
    print(category["name"])
input("press a key to continue")

def main():
    write_to_log(f"Started running program at {datetime.now()}")

    #parser.download_all_html()
    #input("Done downloading wechat articles, press a key to continue")

    #print("resetting everything in wp")
    reset_progress()

    print("importing articles")
    #import_articles()
    print("done")
    


def import_articles():
    
    #grab article(s) names
    articles = [f for f in os.listdir(article_dir) if os.path.isfile(os.path.join(article_dir, f))]

    #for testing, only take a few articles
    #articles = articles[0:10]

    for article_name in articles:
        #todo-filter if article is already in the db
        if not db.article_exists(conn, article_name):
            print(f"processing: {article_name}")
            process_article(article_name)
            db.insert_article(conn, article_name)
        else:
            print(f"skipped: {article_name}")


def process_article(article_name):
    article_path = os.path.join(article_dir, article_name)
    #get article string
    f = open(article_path, "r", encoding = "utf-8")
    article_string = f.read()
    f.close()
    
    #get article date (in js) before we remove it from article
    article_date = parser.find_date(article_string)

    #no date means it is either empty file or article was censored
    if not article_date:
        write_to_log(f'Error: the article {article_name} did not have a date')
        return

    #process text and image links
    article_string = parser.get_article_html_and_images(article_string)
    img_links = parser.get_image_urls(article_string)

    #post images and add to db
    for img_link in img_links:
        #this url is used for wechat specific things, not media. Is not well formed, and is usually cut out of page when we process it, sometimes gets through
        if img_link.strip().startswith("//res.wx.qq"):
            continue
        new_link = ''
        if not db.image_exists(conn, img_link):
            new_link = upload_image(img_link)
            if new_link == '':
                write_to_log(f"Error: {img_link} in article {article_name} was not uploaded correctly")
        #link exists in db
        else: 
            new_link = db.get_new_image_link(conn, img_link)
        img_index = article_string.find(img_link)
        article_string = article_string.replace(img_link, new_link)
    #write/upload new formatted file
    with open(re.sub("articles", "modified_articles", article_path), "w", encoding = "utf-8") as f:
        f.write(article_string)
    upload_article(article_name, article_string, article_date)

#uploads image, returns new image link
def upload_image(img_link):
    #get next id #
    new_link = ""
    image_id = db.get_new_image_id(conn)
    print(f"id is: {image_id}")
    #download image (with new name), can't directly upload image.content to wp rest api so need to do this, says can't accept for security reasons
    image_path = os.path.join(file_path, f'.\\img\\wx_{image_id}.jpg')
    with open(image_path,'wb+') as image_file:
        try:
            r = requests.get(img_link)
            image_file.write(r.content)
        except:
            write_to_log(f"Error: something went wrong with getting image url: {img_link}")
            return new_link #will be empty and also trigger other log 
    #upload file
    res = wp_auth_lib.upload_pic(image_path, None, "publish", f"wx_{image_id}") 
    os.remove(image_path)
    #if successful, add to db
    #several possible links work: https://www.ohiocaa.org/?attachment_id=1707, https://www.ohiocaa.org/wx_1-4/, http://www.ohiocaa.org/wp-content/uploads/2020/07/test.jpg
    if res.status_code == 201:
        res_content = res.json()
        new_link = res_content['guid']['rendered']
        db.insert_image(conn, img_link, new_link, image_id)
    else:
        write_to_log(f"Error: uploading {img_link} to wordpress, status code: {res.status_code}, text: {res.text}")
    return new_link


def upload_article(article_name, article_string, article_date):
    my_date = wp_auth_lib.create_date(int(article_date[0]), int(article_date[1]), int(article_date[2]), 0, 0, 0) # should be "2020-05-28T00:00:00"
    #remove.html from wordpress title
    index = article_name.find(".html")
    wp_title = article_name[:index]
    #article_excerpt = parser.get_excerpt(article_string)
    article_excerpt = " " #want an empty excerpt, need whitespace not empty string

    #todo-should also create a new url because the automated url is really long due to the chinese characters in unicode

    wp_auth_lib.create_post(my_date , "publish", wp_title, article_string, [category_id], article_excerpt)


def reset_progress():
    print("deleting images")
    delete_images()
    print("deleting posts")
    delete_posts()

def delete_images():
    image_ids_to_delete = set()
    pattern = re.compile("wx_\d*")
    page = 1
    while True:
        images = wp_auth_lib.get_images(page, "wx_")
        #print("printing get images response")
        #print(json.dumps(images))
        try:
            if len(images)==0:
                break
            for image in images:
                #if pattern.match(image["title"]["rendered"]):#shouldn't really need this since no one else will use this naming convention
                #search also checks url. so if i changed title of pic so it doesn't match it won't come up if i use the regex
                image_ids_to_delete.add(image["id"])
            page += 1
        except:
            #will get a TypeError if the json response doesn't match what we expect
            break
    print(len(image_ids_to_delete))
    input()
    for image_id in image_ids_to_delete:
        wp_auth_lib.delete_image(image_id)

def delete_posts():
    post_ids_to_delete = set()
    page = 1
    while True:
        posts = wp_auth_lib.get_posts(page, category_id)
        try:
            if len(posts)==0:
                break
            for post in posts:
                post_ids_to_delete.add(post["id"])
            page += 1
        except:
            break
    for post_id in post_ids_to_delete:
        wp_auth_lib.delete_post(post_id)


def write_to_log(string):
    with open('logs/log.txt', 'a', encoding = "utf-8") as f:
        f.write(string+'\n')


if __name__ == '__main__':
    main()
