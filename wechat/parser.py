import requests
import json
import time
import html
import os
import fileinput
import sys
import html2text
import re
import wechat.auth as auth

class Parser():
    def __init__(self, biz, uin, key):
        self.biz = auth.get_biz()
        self.uin = auth.get_uin()
        self.key = auth.get_key()
        self.html2text_parser = html2text.HTML2Text()
        self.html2text_parser.images_as_html = True

    def download_all_html(self):
        index = 1
        while(self.download_html(index)):
            index += 1

    def download_html(self, index):

        # url prefix
        url = "https://mp.weixin.qq.com/mp/profile_ext"

        # request headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
                        "Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 "
                        "QQBrowser/9.0.2524.400",
        }

        proxies = {
            'https': None,
            'http': None,
        }

        # important parameters
        param = {
            'action': 'getmsg',
            '__biz': self.biz,
            'f': 'json',
            'offset': index * 10,
            'count': '10',
            'is_ok': '1',
            'scene': '124',
            'uin': self.uin,
            'key': self.key,
            'wxtoken': '',
            'x5': '0',
        }
        while(True):
            try:
                # send request get response
                response = requests.get(url, headers=headers, params=param, proxies=proxies)
                print(response.status_code)
                response_dict = response.json()

                #print(response_dict)
                next_offset = response_dict['next_offset']
                can_msg_continue = response_dict['can_msg_continue']

                general_msg_list = response_dict['general_msg_list']
                data_list = json.loads(general_msg_list)['list']

                print(data_list)
            except KeyError:
                print("Incorrect JSON has been returned, key is likely outdated/wrong")
                self.key = input("Please enter new key value:\n")
                param['key'] = self.key
                auth.write_key(self.key)
            except Exception as e:
                print("An unexpected error occurred:")
                print(e)
                return False

        for data in data_list:
            try:
                datetime = data['comm_msg_info']['datetime']
                date = time.strftime('%Y-%m-%d', time.localtime(datetime))

                msg_info = data['app_msg_ext_info']

                #title
                title = msg_info['title']

                # content url
                url = msg_info['content_url'].replace("\\", "").replace("http", "https")
                url = html.unescape(url)
                print(url)

                res = requests.get(url, headers=headers, proxies=proxies)
                with open("C:\\Users\\Eric Fu\\workspace\\ocaa-wechat-migration\\wechat\\articles\\" + title + ".html", "wb+") as f:
                    f.write(res.content)

                print(title + date + 'success')

            except Exception as e:
                print(e)
                print("likely not an article")

        if can_msg_continue == 1:
            return True
        else:
            print('all completed')
            return False


    #a helper method for get_article_html_and_images
    def find_nth(self, string, substring, n):
        start = string.find(substring)
        while start >= 0 and n > 1:
            start = string.find(substring, start+len(substring))
            n -= 1
        return start

    def get_article_html_and_images(self, article_string):
        #replace wechat 'data-src' attributes to fix images
        article_string = re.sub("data-src=", "src=", article_string)

        #get the text and images
        article_string = self.html2text_parser.handle(article_string)

        #remove remaining (javascript:void;) like text
        article_string = re.sub("\(javascript:.*[\r?\n|\r]", "", article_string)

        #we can actually remove all things before second img (firstimge is empty, second img is the banner)
        #index = article_string.index("<img")
        index = self.find_nth(article_string, "<img", 2)
        article_string = article_string[index:]

        #remove all things after **【近期文章】
        #some don't have so just keep the whole thing, ex: S.386又卷土重来，现在我们该怎么办？.html
        try:
            index = article_string.index("**【近期文章】")
            article_string = article_string[:index]
        except ValueError:
            print("this article doesn't contain substring **【近期文章】 ")
        
        #insert paragraph tags
        article_list = article_string.strip().split("\n")
        article_list = [string for string in article_list if string != '']
        #can only insert around text, not img info
        for i in reversed(range(len(article_list))):
            valid_par = True
            for substring in ['<img', 'src=', '/>']:
                if substring in article_list[i]:
                    valid_par = False
                    break
            if valid_par:
                #insert </p> after and <p> before
                article_list.insert(i+1, "</p>")
                article_list.insert(i, "<p>")
        article_string = "\n".join(article_list)

        return article_string

        #get the urls from already cleaned string
    def get_image_urls(self, article_string):
        #some assumptions go into how the string is formatted
        pattern = re.compile("src='.*[\r?\n|\r]*\/>")
        links = re.findall(pattern, article_string)
        #obtain the src url from the html tag
        for i in range(len(links)):
            #there should only be two
            quotes = [i for i, letter in enumerate(links[i]) if letter == "'"]
            links[i] = links[i][quotes[0]+1:quotes[1]]

        links = list(filter(lambda x: not x.strip() == '', links)) #appears to work now, removes empty links
        #todo-make sure links are well-formed
        
        return links

    #find the date located in the full/initial article string
    def find_date(self, article_string):
        pattern = re.compile("20(\d){2}-(\d){1,2}-(\d){1,2}")
        res = re.search(pattern, article_string)
        if res:
            return res.group(0).split('-')
        print("date not found in file")
        return None
    
    def get_excerpt(self, article_string):
        length = 250
        res = []
        inside_paragraph = False
        i = 0
        punctuation_pattern = re.compile("[.!?\\-。:：，,]")
        print('getting excerpt')
        while i < len(article_string): 
            if length <= 0:
                break
            if article_string[i:i+3] == '<p>':
                inside_paragraph = True
                i += 3
            elif article_string[i:i+4] == '</p>':
                inside_paragraph = False
                i += 4
            elif inside_paragraph:
                #if we encounter new line character
                if article_string[i:i+2] == '\n':
                    i += 2
                #if is a chinese character
                elif u'\u4e00' < article_string[i] < u'\u9fff':
                    res.append(article_string[i])
                    length -= 1
                    i+= 1
                #if encounter english/number
                elif article_string[i].isalnum():
                    word_length = 1
                    while article_string[i+word_length].isalnum():
                        word_length += 1
                    res.append(article_string[i:i+word_length])
                    length -= word_length
                    i += word_length
                #encounter punctuation
                elif punctuation_pattern.match(article_string[i]):
                    res.append(article_string[i])
                    length -= 1
                    i += 1
                else:
                    i+= 1
            else:#outside paragraph
                i+= 1
        #add space before each english word
        for i in range(len(res)):
            if res[i].isalnum():
                res.insert(i, " ")
        return "".join(res) + "..."


