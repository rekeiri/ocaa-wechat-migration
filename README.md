# ocaa-wechat-migration
The goal of this program is to take all articles posted on a WeChat Official Account, and upload them as posts to a WordPress Site.

## Part 1: Collecting the WeChat articles
WeChat articles can be accessed through the WeChat app or through the desktop app. There is no way to log into WeChat through a browser and view the articles there, so that removes the possibility of web scraping. The WeChat API documentation also isn't very good, and it appears that in order to use the API, I need to request access through the Official Account, which I don't have the credentials through. Much of the documentation and websites are in Chinese, which would make it very difficult.

The other way is obtained through analyzing the web traffic when viewing the Official Account through the desktop app. Using Fiddler, we can see what kind of request is being sent and the necessary parameters. First. install Fiddler, and then make sure to enable HTTPS decryption. Then click on the link to the Official Account. You should see the interface in the picture below.

![WeChat Official Account Screenshot](pic1.png?raw=true "Official Account Screenshot")

Now, let us look at the request through Fiddler.  Looking at the order of requests and the URLs, it becomes quite apparent that the "profile_ext" URL is likely the one that grabs most of the data regarding the articles. 

![Initial Fiddler Request Screenshot](pic2.png?raw=true "Initial Fiddler Request for Articles")

When we scroll down and the application gathers another few articles, it is clear that this definitely is the request that gathers the articles. 

![Second Fiddler Request Screenshot](pic3.png?raw=true "Second Fiddler Request for Articles")

After some testing with the different parameters, it became apparent that the necessary unique parameters include __biz, uin, and key. The can_message_continue value returned in the JSON is also important, as it lets us know if there are any more articles to be obtained. And finally, the offset lets us control which articles we obtain (it is the offset of the number of the article starting from the most recent), and the count lets us control how many articles we retrieve. 

Sometimes while testing, we get a KeyError while trying to obtain next_offset from the response. In the respose body, there is an attribute "errmsg": "no session", so obviously the incorrect response is being returned. This is due to the key having expired/changed. Requests at different times contain different key values. There doesn't appear to be a way to programmatically retrieve an updated key-the initial request to WeChat servers already contains this key. It is likely that it is algorithmically created through some combination of the userid (uin), time, and maybe some other account specific parameters. So the only way is to go back through fiddler and get a new key.

After we successfully request for all of the articles and download them as HTML files, it seems quite easy to upload all of the content straight into WordPress. However, there are several issues.

1. When you open up the html file in a browser, none of the images load. They will load, if you go to the original WeChat link in a browser. The cause is that each img has an attribute data-src, so in order to view/get the images, we need to change the attribute to src, since we won't be including the javascript to process data-src.

2. How do we download the video?

3. we need to back up the images. We cannot just directly upload the article, since all the images are still hosted on WeChat servers. So, we need to grab all the images, upload them to the WordPress server, and then replace the image URLs with the new URLs from the WordPress server.

4. There is a lot of obfuscated JavaScript in the HTML file. This will slow down the server significantly. Also, if you try to include the JS in a post, it will change the formatting of the page in WordPress. Removing all the script tags from the file cause the article to not display properly. So we need to figure out how to get only the text and images from the file.

5. (Optional) There are "recent articles" linked at the bottom of the article. If we decide to include this section in the backup, then it is necessary to replace these links with the new URLs to the articles on the WordPress server.

To solve issues 1 and 4, we can use html2text and regex to get the necessary information. 

In terms of issue 2, there is an <iframe> in the page where they download their own video player. The video player has a src. If you ...



## Part 2: Uploading to WordPress

The first issue is authenticating to the REST API. As I prefer to work with python, we need some way of authenticating to the REST API. I found the plugin "WP OAuth Server" and it seemed adequate.

The first issue is authenticating to the server, and the free version only allows the authorization code grant type. Using the requests-oauthlib library, I was successful in getting the access token. however, trying to send a basic request to the WP REST API gave my response 401 even though the bearer token was included in the authorization header.

The solution to this was including the access token in the url as a query string, as it appears there are some bugs on the plugin side.

The REST API documentation is also not very good. The exact format of certain parameters is not clearly defined. TODO.....


requirements:
status needs to be of type string with value: publish, future, draft, pending, private, refunded, failed, revoked, cancelled, abandoned, processing, preapproval.
date needs to be of type string with format: "2020-06-03T22:20:23"