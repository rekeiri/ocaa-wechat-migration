from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
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
    oauth = OAuth2Session(get_client_id(), redirect_uri = redirect_uri)
    authorization_url, state = oauth.authorization_url(authorization_base_url)
    print("Please go to %s and authorize access." % authorization_url)
    authorization_response = input("Enter the full callback URL\n")
    print()

    #fetching access token
    token = oauth.fetch_token(token_url,
                                authorization_response = authorization_response,
                                client_secret = get_client_secret())
    write_token_to_config(token)
    return oauth

def write_token_to_config(token):
    token_str = token["access_token"]
    expire_time = str(token["expires_at"])

    dirname = os.path.dirname(__file__)
    config_file = os.path.join(dirname, 'config.xml')
    tree = ET.parse(config_file)
    config_root = tree.getroot()

    token_node = config_root.find('accesstoken')
    token_node.text = token_str

    expire_node = config_root.find('expiresat')
    expire_node.text = expire_time
    
    tree.write(config_file)

def get_client_id():
    dirname = os.path.dirname(__file__)
    config_file = os.path.join(dirname, 'config.xml')
    tree = ET.parse(config_file)
    client_id = tree.find('clientid').text
    return client_id

def get_client_secret():
    dirname = os.path.dirname(__file__)
    config_file = os.path.join(dirname, 'config.xml')
    tree = ET.parse(config_file)
    client_secret = tree.find('clientsecret').text
    return client_secret

#returns token string
def get_auth_token():
    dirname = os.path.dirname(__file__)
    config_file = os.path.join(dirname, 'config.xml')
    tree = ET.parse(config_file)
    token = tree.find('accesstoken').text
    return token

#returns token expiration time (epoch)
def get_token_expiration_time():
    dirname = os.path.dirname(__file__)
    config_file = os.path.join(dirname, 'config.xml')
    tree = ET.parse(config_file)
    expire_time = tree.find('expiresat').text
    #if string is not None, empty, or just whitespace
    if expire_time and not expire_time.isspace():
        return float(expire_time)
    return 0