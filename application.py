# This is the main application file.
# Pushing out to github to have a starting point
import time

import psycopg2
from sshtunnel import SSHTunnelForwarder
import bcrypt # bcrypt hash used with mockaroo passwords
from psycopg2.extensions import cursor
from datetime import date


def main_loop(cursor):
    while 1:
        user_input = input("Welcome to the movies database!\n"
                           "r: register new user\n"
                           "l: login to database\n"
                           "s: search movies\n"
                           "q: exit program\n")
        if user_input == 'q':
            break
        elif user_input == 'l':
            login(cursor)
        elif user_input == 'r':
            createAccount(cursor)
        elif user_input == 's':
            searchMovie(cursor)
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
    """
    Register a user to the database
    :param cursor: cursor to connect to the database and tables
    """
    username = input("Type the new account's username: ")
    # check if username already exists
    cursor.execute("SELECT count(*) FROM person WHERE username = ?", (username,))
    results = cursor.fetchall()
    if results[0] > 0:
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
        # TODO check if user inputted date in correct format?
        # record time and date of account creation
        creation_date = date.today()
        last_access = date.today()
        # TODO how are we storing time of last access or is this unused?
        time_created = time.localtime()

        cursor.execute(
            "INSERT INTO person (username, password, email, fname, lname, dob, "
            "creation_date, last_access) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, password, email, fname, lname,
             dob, creation_date, last_access)
        )

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
    # Get search parameters from the user
    search_option = input("Search movies by (name/release date/cast members/studio/genre): ").lower()
    search_query = input("Enter your search query: ")

    # Construct the SQL query based on user input
    sql_query = """
                SELECT m.title, m.cast_members, m.director, m.length, m.mpaa, r.release_date
                FROM movie m
                LEFT JOIN released r ON m.movieid = r.movieid
                LEFT JOIN produces p ON m.movieid = p.movieid
                LEFT JOIN categorize c ON m.movieid = c.movieid
                WHERE """
    
    #search by name
    if search_option == "name":
        sql_query += f"LOWER(m.title) LIKE LOWER('%{search_query}%')"
    #search by release date
    elif search_option == "release date":
        sql_query += f"r.release_date = '{search_query}'"
    #search by cast members
    elif search_option == "cast members":
        sql_query += f"LOWER(m.cast_members) LIKE LOWER('%{search_query}%')"
    #search by studio
    elif search_option == "studio":
        sql_query += f"LOWER(p.contributorid) LIKE LOWER('%{search_query}%')"
    #search by genre
    elif search_option == "genre":
        sql_query += f"c.genreid = (SELECT genreid FROM genre WHERE LOWER(genre_name) = LOWER('{search_query}'))"
    else:
        print("Invalid search option.")
        return

    # Sorting the result
    sort_option = input("Sort results by (name/release date): ").lower()
    if sort_option == "name":
        sql_query += " ORDER BY m.title ASC"
    elif sort_option == "release date":
        sql_query += " ORDER BY r.release_date ASC"
    else:
        print("Invalid sort option.")
        return

    # Execute the constructed query
    cursor.execute(sql_query)
    results = cursor.fetchall()

    # Print the results
    if results:
        print("Search Results:")
        for result in results:
            print("Title:", result[0])
            print("Cast Members:", result[1])
            print("Director:", result[2])
            print("Length:", result[3])
            print("MPAA Rating:", result[4])
            print("Release Date:", result[5])
            print()
    else:
        print("No matching movies found.")


def getFriends(curs):
    # Write the querty to get and print friends
    print("Function to get friends")
