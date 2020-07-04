import os
import re
import requests
from wechat.parser import Parser
from wechat.config import uin as w_uin, key as w_key, biz as w_biz
from wordpress.wp_auth_library import WPAuthLibrary
try:
    from wordpress.config import access_token, expires_at
except:
    access_token, expires_at = None, None
import database.main_operations as db

db_path = r"C:\Users\Eric Fu\workspace\ocaa-wechat-migration\database\my_database.db"

file_path = os.path.dirname(__file__)
db.delete_db(db_path)
conn = db.create_connection(db_path)
db.create_table(conn, db.image_table_sql)
db.create_table(conn, db.article_table_sql)
wp_auth_lib = WPAuthLibrary(access_token, expires_at)
parser = Parser(w_biz, w_uin, w_key)

def main():
    #print("running wechat code")
    wechat()
    #print("running wordpress code")
    #wordpress()
    


def wechat():
    #wechat code

    #grab all wechat articles, download them to folder
    #parser.download_all_html

    #grab article(s) names
    dirname = os.path.join(file_path, ".\\wechat\\articles")
    articles = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]

    #for test, only take first article
    articles = articles[0:1]

    for article_name in articles:
        #filter if article is already in the db

        article_path = os.path.join(dirname, article_name)

        #get article string
        f = open(article_path, "r", encoding = "utf-8")
        article_string = f.read()
        f.close()

        #start scraping the text/images
        article_string = parser.get_article_html_and_images(article_string)
        img_links = parser.get_image_urls(article_string)

        print("working with images")
        #post images and add to db
        for img_link in img_links:
            print(img_link)
            new_link = ''
            if not db.image_exists(conn, img_link):
                #get next id #
                image_id = db.get_new_image_id(conn)
                print(f"id is: {image_id}")
                #download image (with new name)
                image_path = os.path.join(file_path, f'.\\img\\wx_{image_id}.jpg')
                with open(image_path,'wb+') as image_file:
                    try:
                        r = requests.get(img_link)
                        image_file.write(r.content)
                    except:
                        print("something went wrong with getting image")
                        print(f"image url: {img_link}")
                        input()
                        continue
                #upload file
                res = wp_auth_lib.upload_pic(image_path, None, "publish", f"wx_{image_id}") 
                #if successful, add to db
                #several possible links work: https://www.ohiocaa.org/?attachment_id=1707, https://www.ohiocaa.org/wx_1-4/, http://www.ohiocaa.org/wp-content/uploads/2020/07/test.jpg
                if res.status_code == 201:
                    res_content = res.json()
                    new_link = res_content['guid']['rendered']
                    print(new_link)
                    db.insert_image(conn, img_link, new_link, image_id)
                else:
                    print("something went wrong with uploading the image to wordpress")
                    input()
                    continue
            #replace old image url with new wordpress url in article_string
            if new_link == '':
                new_link = db.get_new_image_link(conn, img_link)
            re.sub(img_link, new_link, article_string)
                


        #write new formatted file
        print("writing file")
        f = open(re.sub("articles", "modified_articles", article_path), "w", encoding = "utf-8")
        f.write(article_string)
        #upload file to wordpress
        category_id = wp_auth_lib.get_category_id("APAPA Ohio Posts")
        my_date = wp_auth_lib.create_date(2020, 7, 2, 0, 0, 0) # should be "2020-05-28T00:00:00"
        print(my_date)
        #remove.html from wordpress title
        index = article_name.find(".html")
        wp_title = article_name[:index]
        #should also create a new url because the automated url is really long due to the chinese characters in unicode
        wp_auth_lib.create_post(my_date , "publish", wp_title, article_string, [category_id])

        #if success, add title to db
        #else, return error



        f.close()


def wordpress():
    
    #WordPress code
    

    '''
    category_id = wp_auth_lib.get_category_id("APAPA Ohio Posts")
    my_date = wp_auth_lib.create_date(2020, 7, 2, 0, 0, 0) # should be "2020-05-28T00:00:00"
    print(my_date)
    wp_auth_lib.create_post(my_date , "publish", "test", "this is a test post", [category_id])

    '''

    '''
    r = wp_auth_lib.get_posts()
    print(len(r))
    for post in r:
        print()
        print(post)
    '''
    '''
    res = wp_auth_lib.upload_pic(os.path.join(file_path, r".\img\test.jpg"), 
                            None,
                            "publish",
                            "wx_1")
    '''

if __name__ == '__main__':
    print("running main")
    main()