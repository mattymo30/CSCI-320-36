# This is the main application file.
# Pushing out to github to have a starting point

import psycopg2
from sshtunnel import SSHTunnelForwarder
import bcrypt # bcrypt hash used with mockaroo passwords
from psycopg2.extensions import cursor


def main_loop(cursor):
    while 1:
        user_input = input("Press q to quit")
        if user_input == 'q':
            break
        else:
            cursor.execute("SELECT * FROM genre")
            results = cursor.fetchall()
            print(results)


# Adds movie to collection
def add_movie(curs: cursor):
    pass


# Deletes movie from collection
def delete_movie(curs: cursor):
    # Ask for name
    pass


def update_col_name(curs: cursor):
    # Ask for old name and and new name
    pass


def delete_collection(curse: cursor):
    # ask for name
    pass


def rate_movie(curs: cursor):
    # ask for rating out of 5
    pass


def watch_movie(curs: cursor):
    # ask for name
    pass


def watch_collection(curs: cursor):
    # ask for name
    pass


def follow(curs: cursor):
    # ask for user email to follow
    pass


def search_users(curs: cursor):
    # Ask for user email
    pass


def unfollow(curs: cursor):
    # ask for user email
    pass


def createAccount(cursor):
    username = input("Type the new account's username: ")
    # check if username already exists
    cursor.execute("SELECT count(*) FROM person WHERE username = ?", (username,))
    results = cursor.fetchall()
    if results > 0:
        print("username already exists!")
    else:
        password = input("Type in the new account's password: ")
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(bytes, salt)
        email = input("Enter your email address: ")
        fname = input("Enter your first name: ")
        lname = input("Enter your last name: ")
        dob = input("Enter your date of birth (YYYY-MM-DD): ")


    # record time and date of account creation
    print("Function to create a account")


def login(curs):
    # use bcrypt.checkpw to check passwords?
    print("Function to login")


def listCollections(curs):
    print("Function to print a users collection")


def createCollections(curs):
    print("Function to create collection")


def manageCollection(curs):
    print("A function to manage collections")


def searchMovie(curs):
    # Need the user to select by what parameter they are going to be searching by
    # Take in user input for that parameter and then write queries and return as such
    print("Function to search for movies")


def getFriends(curs):
    # Write the querty to get and print friends
    print("Function to get friends")
