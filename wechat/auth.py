import xml.etree.ElementTree as ET
import os

dirname = os.path.dirname(__file__)
config_file = os.path.join(dirname, 'config.xml')

def get_uin():
    tree = ET.parse(config_file)
    uin = tree.find('uin').text
    return uin

def write_uin(uin):
    tree = ET.parse(config_file)
    tree.find('uin').text = uin
    tree.write(config_file)

def get_biz():
    tree = ET.parse(config_file)
    biz = tree.find('biz').text
    return biz

def write_biz(biz):
    tree = ET.parse(config_file)
    tree.find('biz').text = biz
    tree.write(config_file)

def get_key():
    tree = ET.parse(config_file)
    key = tree.find('key').text
    return key

def write_key(key):
    tree = ET.parse(config_file)
    tree.find('key').text = key
    tree.write(config_file)

