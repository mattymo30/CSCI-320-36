# This is the main application file.
# Pushing out to github to have a starting point

import psycopg2
from sshtunnel import SSHTunnelForwarder
from psycopg2.extensions import cursor

def main_loop(cursor):
    while 1:
        user_input = input ("Press q to quit")
        if user_input == 'q':
            break
        else:
            cursor.execute("SELECT * FROM genre")
            results = cursor.fetchall()
            print (results)

# Adds movie to collection
def add_movie(curs:cursor):
    pass

# Deletes movie from collection
def delete_movie(curs:cursor, name:str):
    pass

def update_col_name(curs:cursor, old_name:str, new_name:str):
    pass

def delete_collection(curse:cursor, name:str):
    pass

def rate_movie(curs:cursor, rating:int):
    pass

def watch_movie(curs:cursor, name:str):
    pass

def watch_collection(curs:cursor, name:str):
    pass

def follow(curs:cursor, user_email:str):
    pass

def search_users(curs:cursor, email:str):
    pass

def unfollow(curs:cursor, user_email:str):
    pass
