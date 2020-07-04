from .config import client_id, client_secret
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import os
import sys
import fileinput
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

authorization_base_url = "http://www.ohiocaa.org/oauth/authorize/"
token_url = "http://www.ohiocaa.org/oauth/token/"
redirect_uri = "/python-redirect/"

#returns oauth session after authenticating to server
def get_oauth_session():
    #authentication
    oauth = OAuth2Session(client_id, redirect_uri = redirect_uri)
    authorization_url, state = oauth.authorization_url(authorization_base_url)
    print("Please go to %s and authorize access." % authorization_url)
    authorization_response = input("Enter the full callback URL\n")
    print()

    #fetching access token
    token = oauth.fetch_token(token_url,
                                authorization_response = authorization_response,
                                client_secret = client_secret)

    write_token_to_config(token)

    return oauth

#writes access token and expiration time to config.py
def write_token_to_config(token):
    token_str = token["access_token"]
    expire_time = str(token["expires_at"])
    changed_token = False
    changed_time = False
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "config.py")
    #look to fix this later, maybe use different method or iterate thorugh lines twice. Is often buggy.
    for line in fileinput.input(filename, inplace = True):
        if line.strip().startswith("access_token ="):
            line = "access_token = "+ "\"" + token_str + "\""
            changed_token = True
        elif line.strip().startswith("expires_at ="):
            line = "expires_at = "+ expire_time
            changed_time = True
        sys.stdout.write(line)
    if not changed_token or not changed_time: #one of the fields didn't exist already in file
        f = open(filename, "a")
        if not changed_token:
            f.write("access_token = "+ "\"" + token_str+"\"\n")
        if not changed_time:
            f.write("\nexpires_at = " + expire_time+"\n")
        f.close()