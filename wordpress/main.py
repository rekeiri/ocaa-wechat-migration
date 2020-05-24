from config import client_id, client_secret
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



authorization_base_url = "http://www.ohiocaa.org/oauth/authorize/"
token_url = "http://www.ohiocaa.org/oauth/token/"
redirect_uri = "http://www.ohiocaa.org/python-redirect/"


#authentication
oauth = OAuth2Session(client_id)
authorization_url, state = oauth.authorization_url(authorization_base_url)
print("Please go to %s and authorize access." % authorization_url)
authorization_response = input("Enter the full callback URL")
print()

#fetching access token
token = oauth.fetch_token(token_url,
                            authorization_response = authorization_response,
                            client_secret = client_secret)
    
