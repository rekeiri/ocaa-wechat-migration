import sqlite3
from sqlite3 import Error
import os

#generally used for changing data
def update_values(conn, query, tup):
	cursor = conn.cursor()
	cursor.execute(query, tup)
	conn.commit()
	cursor.close()

#generally used for queries (reading data)
def execute_query(conn, query, tup = None): 
	cursor = conn.cursor()
	if tup:
		cursor.execute(query, tup)
	else:
		cursor.execute(query)
	conn.commit()
	results = []
	for line in cursor:
		results.append(line)
	cursor.close()
	return results


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn

def delete_db(dbfile):
    try:
        os.remove(dbfile)
        print(dbfile)
    except FileNotFoundError:
        print(dbfile + 'didn\'t exist')



def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def article_exists(conn, url):
    tup = (url,)
    query = "SELECT 1 FROM"

def image_exists(conn, url):
    tup = (url,)
    query = "SELECT 1 FROM image_urls WHERE original_url = ?"
    res = execute_query(conn, query, tup)
    return len(res)>0

def get_new_image_id(conn):
    query = "SELECT MAX(id) FROM image_urls"
    res = execute_query(conn, query)
    #res = [(None,)], since execute_query returns list of tupes
    if res[0][0] is not None:
        return res[0][0] +1
    return 0

def get_new_image_link(conn, orig_url):
    tup = (orig_url,)
    query = "SELECT wordpress_url FROM image_urls WHERE original_url = ?"
    res = execute_query(conn, query, tup)
    if res[0][0] is not None:
        return res[0][0]
    print("image url not found")
    return -1

def insert_image(conn, orig_url, new_url, image_id):
    tup = (orig_url, new_url, image_id)
    query = "INSERT INTO image_urls VALUES(?, ?, ?)"
    update_values(conn, query, tup)

#longer sql statements
image_table_sql = """CREATE TABLE IF NOT EXISTS image_urls(
                    original_url text PRIMARY_KEY,
                    wordpress_url text NOT NULL,
                    id integer NOT NULL
                    )"""

article_table_sql = """CREATE TABLE IF NOT EXISTS article_links(
                    original_url text PRIMARY_KEY,
                    wordpress_url text
                    )"""
