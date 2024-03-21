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


def createAccount(curs):
    # record time and date of account creation
    print ("Function to create a account")

def login(curs):
    print ("Function to login")

def listCollections(curs):
    print ("Function to print a users collection")

def searchMovie(curs):
    # Need the user to select by what parameter they are going to be searching by
    # Take in user input for that parameter and then write queries and return as such
    print ("Function to search for movies")


def getFriends(curs):
    # Write the querty to get and print friends
    print ("Function to get friends")
