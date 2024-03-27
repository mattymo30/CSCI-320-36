# This is the main application file.
# Pushing out to github to have a starting point
from sshtunnel import SSHTunnelForwarder
import bcrypt # bcrypt hash used with mockaroo passwords
from psycopg2.extensions import cursor
from datetime import date
import sys
from os import system
from tabulate import tabulate


CURR_USER = None
CURR_USER_ID = None


def main_loop(cursor, conn):
    while 1:
        user_input = input("Welcome to the movies database!\n"
                           "r: register new user\n"
                           "l: login to database\n"
                           "c: to go to collections\n"
                           "q: exit program\n")
        if user_input == 'q':
            break
        elif user_input == 'l':
            system('clear')
            login(cursor)
        elif user_input == 'r':
            system('clear')
            createAccount(cursor, conn)
        elif user_input == 'c':
            system('clear')
            manageCollection(cursor, conn)
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

# Helper function for login/signup
# Returns a hashed password
def hash_pass(password:str):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(bytes, salt)
    password = password.decode() # Changes from byte string to regular string
    return password

def createAccount(cursor:cursor, conn):
    """
    Register a user to the database
    :param cursor: cursor to connect to the database and tables
    """
    # check if username already exists
    # mfindon0 is expected to have 1
    username = input("Type the new account's username: ")
    cursor.execute("SELECT count(*) FROM person WHERE username = (%s);",(username,))
    results = cursor.fetchall()

    if results[0][0] > 0:
        print("username already exists!")
        return 
    
    # password hashing
    password = hash_pass(input("Type in the new account's password: "))
    
    # Other info
    email = input("Enter your email address: ")
    fname = input("Enter your first name: ")
    lname = input("Enter your last name: ")
    # TODO check if user inputted date in correct format?
    dob = input("Enter your date of birth (YYYY-MM-DD): ") 
    
    # record time and date of account creation
    creation_date = date.today()

    # Gets total users for primary key
    # Works because users can't be deleted
    cursor.execute("SELECT count(*) FROM person")
    total_users = cursor.fetchall()[0][0]
    
    cursor.execute("""
        INSERT INTO person (userid, username, password, email, fname, lname, dob, creation_date, last_access)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
        """, 
        (
            int(total_users+1),
            username,
            password,
            email,
            fname,
            lname,
            dob,
            creation_date
        )
    )
    conn.commit()

    print("Account has been created!")


def login(cursor:cursor):


    global CURR_USER
    global CURR_USER_ID

    """
    Attempt to log in a user to the database
    :param cursor: cursor to connect to the database and tables
    """
    # TODO Find a way to hold CUR_USER
    # if CUR_USER != "":
    #     print(f"You are already logged into an account: {CUR_USER}")
    #     return

    if CURR_USER != None:
        print(f"You are already logged into an account: {CURR_USER}")
        return

    # User enters credentials
    username = input("Enter your username: ")
    entered_pass = input("Enter your password: ").encode('utf-8')

    # Gets password from DB
    cursor.execute("SELECT password FROM person WHERE username = %s",(username,))
    result = cursor.fetchone()

    # if the username did exist
    if not result:
        print("Username not found. Please try again.")
        return
    
    actual_pass = result[0].encode('utf-8')
    if bcrypt.checkpw(entered_pass, actual_pass):
        print("Login successful")
        # TODO Find a way to hold CUR_USER
        CURR_USER = username
        cursor.execute("SELECT userID FROM person WHERE username = %s", (CURR_USER,))
        # CURR_USER_ID = cursor.fetchone()[0]
        CURR_USER_ID = 2152
        # print(CURR_USER_ID)

    else:
        print("Incorrect password. Please try again.")



def createCollections(curs):
    print("Function to create collection")

def display_menu(menu):
    for k, function in menu.items():
        print(str(k) + ": Collection Name " + str(function[1]) + " | Number of Movies in Collection " + str(function[2]) + " | Total Run time in Minutes:seconds " + str(function[3]))


def editCollection(collectionID: int, curs: cursor, conn):
    while True:
        system('clear')
        curs.execute("SELECT m.movieID, m.title, m.mpaa, m.length FROM CONTAINS c JOIN MOVIE m ON c.movieID = m.movieID WHERE c.collectionID = %s;", (collectionID, ))
        results = curs.fetchall()
        # printing out all the movies in the collection
        print(tabulate(results, headers=['Movie id', 'Movie Name', 'Movie Rating', 'Movie Runtime in seconds']))
        print(collectionID)
        selection = input('Type DW to Delete whole collection, Type CN to change collection name, Type D to delete a movie from collection, Type A to add a movie to the collection, q to exit')
        if selection == 'q':
            break
        elif selection == 'CN':
            new_name = input('Type the new name of your collection')
            curs.execute("UPDATE COLLECTION SET name = %s WHERE collectionID = %s", (new_name, collectionID, ))
            conn.commit()
        elif selection == 'D':
            movieToDelete = input ("Type the id of the movie you want to delete")
            curs.execute("DELETE FROM CONTAINS WHERE movieID = %s AND collectionID= %s", (movieToDelete, collectionID, ))
            conn.commit()
    

def manageCollection(curs: cursor, conn):
    system('clear')
    curs.execute("SELECT c.collectionID, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, TO_CHAR(INTERVAL '1 minute' * SUM(m.length), 'HH24:MI') AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID JOIN CONTAINS cm ON c.collectionID = cm.collectionID JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC, num_movies, total_length;", (CURR_USER_ID,))
    results = list(curs.fetchall())
    print(results)
    menu_items = dict(enumerate(results, start=1))
    print(menu_items)
    while True:
        display_menu(menu_items)
        selection = input("Select a number or press q to return to main menu")
        if selection == 'q':
            system('clear')
            break
        elif selection.isnumeric() and int(selection) in menu_items:
            editCollection(menu_items[int(selection)][0], curs, conn)
            system('clear')
            curs.execute("SELECT c.collectionID, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, TO_CHAR(INTERVAL '1 minute' * SUM(m.length), 'HH24:MI') AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID JOIN CONTAINS cm ON c.collectionID = cm.collectionID JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC, num_movies, total_length;", (CURR_USER_ID,))
            results = list(curs.fetchall())
            print(results)
            menu_items = dict(enumerate(results, start=1))
            print(menu_items)
        else:
            print ("Please select a valid number")



    # print("A function to manage collections")


def searchMovie(curs):
    # Need the user to select by what parameter they are going to be searching by
    # Take in user input for that parameter and then write queries and return as such
    print("Function to search for movies")


def getFriends(curs):
    # Write the querty to get and print friends
    print("Function to get friends")
