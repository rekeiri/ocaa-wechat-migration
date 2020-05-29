from auth import get_oauth_session


def is_access_token_valid():
    


#if token is not valid, retrieve new token
if access_token_valid:

else:
    session = get_oauth_session()

session = get_oauth_session()

def get_posts(session):
    get_url = "https://ohiocaa.org/wp-json/wp/v2/posts"
    r = session.get(get_url)
    print(r)
    print(r.text)
    print(r.headers)
    print("DONE")
    print()
    print("-----------------------")



def create_post(session, date, status, title, content, category):
    post_url = "https://ohiocaa.org/wp-json/wp/v2/posts"
    data = {"date": date, "status": status, "title": title, "content": content, "category": category}
    r = session.post(post_url, data = data)
    print(r)
    print(r.text)
    print(r.headers)
    print("DONE")
    print()
    print("-----------------------")



create_post(oauth, "2020-5-28", "published", "test", "this is a test post", "APAPA Ohio Posts")

get_posts(oauth)