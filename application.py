# This is the main application file.
# Pushing out to github to have a starting point

import psycopg2
from sshtunnel import SSHTunnelForwarder
# from connect import curs


def main_loop(cursor):
    while 1:
        user_input = input ("Press q to quit")
        if user_input == 'q':
            break
        else:
            cursor.execute("SELECT * FROM genre")
            results = cursor.fetchall()
            print (results)



