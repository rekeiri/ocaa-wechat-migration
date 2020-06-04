import requests
import json
import time
import html

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

    # send resquest get response
    response = requests.get(url, headers=headers, params=param, proxies=proxies)
    response_dict = response.json()

    # print(reponse_dict)
    next_offset = response_dict['next_offset']
    can_msg_continue = response_dict['can_msg_continue']

    general_msg_list = response_dict['general_msg_list']
    data_list = json.loads(general_msg_list)['list']

    print(data_list)

    for data in data_list:
        try:
            datetime = data['comm_msg_info']['datetime']
            date = time.strftime('%Y-%m-%d', time.localtime(datetime))

            msg_info = data['app_msg_ext_info']

            # 标题
            title = msg_info['title']

            # 内容的url
            url = msg_info['content_url'].replace("\\", "").replace("http", "https")
            url = html.unescape(url)
            print(url)

            res = requests.get(url, headers=headers, proxies=proxies)
            with open("C:\\Users\\Eric Fu\\workspace\\ocaa-wechat-migration\\wechat\\articles\\" + title + ".html", "wb+") as f:
                f.write(res.content)

            print(title + date + 'success')

        except Exception as e:
            print(e)
            print("不是图文消息")

    if can_msg_continue == 1:
        return True
    else:
        print('all completed')
        return False


uin = "NjIzNjc5OTU4"
key = "06519858b69686397976c10bb02f3b5320f2d3d99705685a78d42129781c4ff891fac3f710eb4730a4bc05f9fb0ef95f0892e07ad6d741a95b637943619266b7d836fef552c4b06c311955ffc6aa21a7"
biz = "MzU5NTk2NjgzMg=="
index = 1

while(parse(index, biz, uin, key)):
    index += 1