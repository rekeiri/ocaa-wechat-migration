import requests
import json
import time
import html
import os
import fileinput
import sys

def parse(index, biz, uin, key):

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
        '__biz': biz,
        'f': 'json',
        'offset': index * 10,
        'count': '10',
        'is_ok': '1',
        'scene': '124',
        'uin': uin,
        'key': key,
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
            key = input("Please enter new key value:\n")
            param['key'] = key
            write_key_to_config(key)
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


def write_key_to_config(key):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "config.py")
    changed_key = False
    for line in fileinput.input(filename, inplace = True):
        if line.strip().startswith("key ="):
            line = "key = " + "\"" + key + "\""
            changed_key = True
        sys.stdout.write(line)
    if not changed_key:
        f = open(filename, "a")
        f.write("\nkey = "+ "\"" + key + "\"\n")
        f.close()

#some adjustments to the html we need to do
def correct_html(html_content):
    pass