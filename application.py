# This is the main application file.
# Pushing out to github to have a starting point
from sshtunnel import SSHTunnelForwarder
import bcrypt # bcrypt hash used with mockaroo passwords
from psycopg2.extensions import cursor
from datetime import date


def main_loop(cursor, conn):
    while 1:
        user_input = input("Welcome to the movies database!\n"
                           "r: register new user\n"
                           "l: login to database\n"
                           "q: exit program\n")
        if user_input == 'q':
            break
        elif user_input == 'l':
            login(cursor)
        elif user_input == 'r':
            createAccount(cursor, conn)
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
    else:
        # password hashing
        password = input("Type in the new account's password: ")
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(bytes, salt)
        password = password.decode() # Changes from byte string to regular string
        
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


def login(cursor):
    """
    Attempt to log in a user to the database
    :param cursor: cursor to connect to the database and tables
    """

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # try to fetch the username in the person table
    cursor.execute("SELECT password FROM person WHERE username = ?",
                   (username,))
    result = cursor.fetchone()
    # if the username did exist
    if result:
        # now check the password
        hashed_p = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_p):
            print("Login successful")
            # TODO should the function return the user id?
        else:
            print("Incorrect password. Please try again.")

    else:
        print("Username not found. Please try again.")


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
