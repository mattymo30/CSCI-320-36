# This is the main application file.
# Pushing out to github to have a starting point
from datetime import datetime
import time

from sshtunnel import SSHTunnelForwarder
import bcrypt  # bcrypt hash used with mockaroo passwords
from psycopg2.extensions import cursor
from datetime import date
import sys
from os import system
from tabulate import tabulate

CURR_USER = None
CURR_USER_ID = None

# global variable to track login status
logged_in = False


def main_loop(cursor, conn):
    while 1:
        user_input = input("Welcome to the movies database!\n"
                           "r: register new user\n"
                           "l: login to database\n"
                           "c: to go to collections\n"
                           "q: exit program\n"
                           "cc: create collection\n"
                           "s: search movies\n"
                           "q: exit program\n")
        if user_input == 'q':
            break
        elif user_input == 'l':
            system('clear')
            login(cursor, conn)
        elif user_input == 'r':
            system('clear')
            createAccount(cursor, conn)
        elif user_input == 'c':
            system('clear')
            manageCollection(cursor, conn)
            system('clear')
        elif user_input == 's':
            searchMovie(cursor)
        elif user_input == 'cc':
            createCollections(cursor, conn)

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
def hash_pass(password: str):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(bytes, salt)
    password = password.decode()  # Changes from byte string to regular string
    return password


def createAccount(cursor: cursor, conn):
    """
    Register a user to the database
    :param cursor: cursor to connect to the database and tables
    """
    # check if username already exists
    # mfindon0 is expected to have 1
    username = input("Type the new account's username: ")
    cursor.execute("SELECT count(*) FROM person WHERE username = (%s);", (username,))
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

    # Loop until user inputs correct DOB format
    while True:
        dob_i = input("Enter your date of birth (YYYY-MM-DD): ")
        try:
            dob = datetime.strptime(dob_i, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Incorrect date format. Please enter the date in YYYY-MM-DD format.")

    # record time and date of account creation
    creation_date = date.today()
    t = time.localtime()
    creation_time = time.strftime("%H:%M:%S", t)

    # Gets total users for primary key
    # Works because users can't be deleted
    cursor.execute("SELECT count(*) FROM person")
    total_users = cursor.fetchall()[0][0]

    cursor.execute("""
        INSERT INTO person (userid, username, password, email, fname, lname, dob, creation_date, last_access)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
        """,
                   (
                       int(total_users + 1),
                       username,
                       password,
                       email,
                       fname,
                       lname,
                       dob,
                       creation_date
                   )
                   )

    cursor.execute("""
        INSERT INTO account_creation (userid, creation_date, time_created)
        VALUES (%s, %s, %s)
        """,
                   (
                       int(total_users + 1),
                       creation_date,
                       creation_time
                   ))

    conn.commit()

    print("Account has been created!")


def login(cursor: cursor, conn):
    """
    Attempt to log in a user to the database
    :param cursor: cursor to connect to the database and tables
    """

    global CURR_USER
    global CURR_USER_ID

    if CURR_USER is not None:
        print(f"You are already logged into an account: {CURR_USER}")
        return

    # User enters credentials
    username = input("Enter your username: ")
    entered_pass = input("Enter your password: ").encode('utf-8')

    # Gets password from DB
    cursor.execute("SELECT password, userid FROM person WHERE username = %s",
                   (username,))
    result = cursor.fetchone()

    # if the username did exist
    if not result:
        print("Username not found. Please try again.")
        return

    actual_pass, userid = result[0].encode('utf-8'), result[1]
    if bcrypt.checkpw(entered_pass, actual_pass):
        print("Login successful")
        CURR_USER = username
        CURR_USER_ID = userid
        print(CURR_USER_ID)

        login_date = date.today()
        t = time.localtime()
        login_time = time.strftime("%H:%M:%S", t)
        cursor.execute("""
        INSERT INTO login (userid, date_logged_in, time_logged_in)
        VALUES (%s, %s, %s)
        """,
                       (
                           int(userid),
                           login_date,
                           login_time
                       ))

        conn.commit()

    else:
        print("Incorrect password. Please try again.")


def createCollections(cursor: cursor, conn):
    collectionname = input("Name this collection: ")
    cursor.execute("SELECT MAX(collectionid) FROM collection")
    max_id = cursor.fetchone()[0] + 1
    cursor.execute("INSERT INTO collection (collectionid, name) VALUES (%s, %s)", (max_id, collectionname))
    conn.commit()
    cursor.execute("INSERT INTO user_owns_collection (collectionID, userID) VALUES (%s, %s)", (max_id, CURR_USER_ID))
    conn.commit()

    print('Collection created.')


def display_menu(menu):
    print("In this function")
    for k, function in menu.items():
        print(str(k) + ": Collection Name " + str(function[1]) + " | Number of Movies in Collection " + str(
            function[2]) + " | Total Run time in Hours:minutes " + str(function[3]))


def editCollection(collectionID: int, curs: cursor, conn):
    while True:
        system('clear')
        curs.execute(
            "SELECT m.movieID, m.title, m.mpaa, m.length FROM CONTAINS c JOIN MOVIE m ON c.movieID = m.movieID WHERE c.collectionID = %s;",
            (collectionID,))
        results = curs.fetchall()
        # printing out all the movies in the collection
        print(tabulate(results, headers=['Movie id', 'Movie Name', 'Movie Rating', 'Movie Runtime in seconds']))
        selection = input(
            'Type DW to Delete whole collection, Type CN to change collection name, Type D to delete a movie from collection, Type A to add a movie to the collection, q to exit')
        if selection == 'q':
            break
        elif selection == 'CN':
            new_name = input('Type the new name of your collection')
            curs.execute("UPDATE COLLECTION SET name = %s WHERE collectionID = %s", (new_name, collectionID,))
            conn.commit()
        elif selection == 'D':
            movieToDelete = input("Type the id of the movie you want to delete")
            curs.execute("DELETE FROM CONTAINS WHERE movieID = %s AND collectionID= %s", (movieToDelete, collectionID,))
            conn.commit()
        elif selection == 'A':
            movieToAdd = input("Type the name of the movie you want to add")
            curs.execute("SELECT movieID, title FROM MOVIE WHERE LOWER(title) LIKE LOWER(%s)", (movieToAdd,))
            results = curs.fetchall()
            print(tabulate(results, headers=['Movie Id', 'Movie Title']))
            movieIdToAdd = input("Type the id of the movie you want to add")
            curs.execute("INSERT INTO CONTAINS (collectionID, movieID) VALUES (%s, %s)", ((collectionID, movieIdToAdd)))
            conn.commit()
        elif selection == "DW":
            curs.execute("DELETE FROM CONTAINS WHERE collectionID = %s", (collectionID,))
            curs.execute("DELETE FROM USER_OWNS_COLLECTION WHERE collectionID = %s", (collectionID,))
            curs.execute("DELETE FROM COLLECTION WHERE collectionID = %s", (collectionID,))
            conn.commit()


def manageCollection(curs: cursor, conn):
    print("IN this statement")
    curs.execute(
        "SELECT c.collectionid, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, CONCAT(FLOOR(SUM(m.length) / 3600), ':', CASE WHEN FLOOR((SUM(m.length) %% 3600) / 60) < 10 THEN CONCAT('0', FLOOR((SUM(m.length) %% 3600) / 60)) ELSE CAST(FLOOR((SUM(m.length) %% 3600) / 60) AS VARCHAR) END ) AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID LEFT JOIN CONTAINS cm ON c.collectionID = cm.collectionID LEFT JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC;",
        (CURR_USER_ID,))
    # curs.execute('SELECT c.collectionid, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, CONCAT(FLOOR(SUM(m.length) / 3600), ':', CASE WHEN FLOOR((SUM(m.length) % 3600) / 60) < 10 THEN CONCAT('0', FLOOR((SUM(m.length) % 3600) / 60)) ELSE CAST(FLOOR((SUM(m.length) % 3600) / 60) AS VARCHAR) END ) AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID LEFT JOIN CONTAINS cm ON c.collectionID = cm.collectionID LEFT JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC;', ((CURR_USER_ID,))
    print("Executed the cursor")
    results = list(curs.fetchall())
    print(results)
    menu_items = dict(enumerate(results, start=1))
    print(menu_items)
    while True:
        system("clear")
        display_menu(menu_items)
        selection = input("Select a number or press q to return to main menu")
        if selection == 'q':
            break
        elif selection.isnumeric() and int(selection) in menu_items:
            editCollection(menu_items[int(selection)][0], curs, conn)
            curs.execute(
                "SELECT c.collectionid, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, CONCAT(FLOOR(SUM(m.length) / 3600), ':', CASE WHEN FLOOR((SUM(m.length) %% 3600) / 60) < 10 THEN CONCAT('0', FLOOR((SUM(m.length) %% 3600) / 60)) ELSE CAST(FLOOR((SUM(m.length) %% 3600) / 60) AS VARCHAR) END ) AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID LEFT JOIN CONTAINS cm ON c.collectionID = cm.collectionID LEFT JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC;",
                (CURR_USER_ID,))
            results = list(curs.fetchall())
            print(results)
            menu_items = dict(enumerate(results, start=1))
            print(menu_items)
        else:
            print("Please select a valid number")

    # print("A function to manage collections")


def searchMovie(curs):
    # Get search parameters from the user
    search_option = input("Search movies by (name/release date/cast members/studio/genre): ").lower()
    search_query = input("Enter your search query: ")

    # Construct the SQL query based on user input
    sql_query = """
            SELECT m.title, c.fname AS cast_fname, c.lname AS cast_lname, d.fname AS director_fname, d.lname AS director_lname, m.length, m.mpaa, r.releasedate
            FROM movie m
            LEFT JOIN released r ON m.movieid = r.movieid
            LEFT JOIN categorize cat ON m.movieid = cat.movieid
            LEFT JOIN acts_in ai ON m.movieid = ai.movieid
            LEFT JOIN contributor c ON ai.contributorid = c.contributorid
            LEFT JOIN directs dr ON m.movieid = dr.movieid
            LEFT JOIN contributor d ON dr.contributorid = d.contributorid
            LEFT JOIN produces pr ON m.movieid = pr.movieid
            LEFT JOIN contributor p ON pr.contributorid = p.contributorid
            WHERE """

    # Search by name
    if search_option == "name":
        sql_query += f"LOWER(m.title) LIKE LOWER('%{search_query}%')"
    # Search by release date
    elif search_option == "release date":
        sql_query += f"r.releasedate = '{search_query}'"
    # Search by cast members
    elif search_option == "cast members":
        # Allow searching by either first name or last name
        sql_query += f"LOWER(c.fname) LIKE LOWER('%{search_query}%') OR LOWER(c.lname) LIKE LOWER('%{search_query}%')"
    # Search by studio
    elif search_option == "studio":
        sql_query += f"LOWER(p.lname) IS NULL AND LOWER(p.fname) LIKE LOWER('%{search_query}%')"
    # Search by genre
    elif search_option == "genre":
        sql_query += f"cat.genreid = (SELECT genreid FROM genre WHERE LOWER(type) = LOWER('{search_query}'))"
    else:
        print("Invalid search option.")
        return

    # Sorting the result
    sort_option = input("Sort results by (name/release date): ").lower()
    if sort_option == "name":
        sql_query += " ORDER BY m.title ASC"
    elif sort_option == "release date":
        sql_query += " ORDER BY r.releasedate ASC"
    else:
        print("Invalid sort option.")
        return

    # Execute the constructed query
    curs.execute(sql_query)
    results = curs.fetchall()

    # Print the results
    if results:
        print("Search Results:")
        prev_title = None
        unique_cast_members = set()
        for result in results:
            title = result[0]
            cast_member = f"{result[1]} {result[2]}"
            director = f"{result[3]} {result[4]}"
            length = result[5]
            mpaa_rating = result[6]
            release_date = result[7]

            # Check if a new movie title is encountered
            if prev_title != title:
                # Print cast members and movie details if it's not the first movie
                if prev_title is not None:
                    print("Cast Members:", ", ".join(unique_cast_members))
                    print("Director:", director)
                    print("Length:", length)
                    print("MPAA Rating:", mpaa_rating)
                    print("Release Date:", release_date)
                    print()  # Print an additional line after each movie
                    unique_cast_members.clear()  # Reset unique cast members set for the new movie

                print("Title:", title)
                unique_cast_members.add(cast_member)  # Add the first cast member encountered for the new movie

            else:
                unique_cast_members.add(cast_member)  # Add cast members for the current movie

            prev_title = title

        # Print the last movie's details
        print("Cast Members:", ", ".join(unique_cast_members))
        print("Director:", director)
        print("Length:", length)
        print("MPAA Rating:", mpaa_rating)
        print("Release Date:", release_date)
        print()  # Print an additional line after the loop
    else:
        print("No matching movies found.")


def getFriends(curs):
    # Write the querty to get and print friends
    print("Function to get friends")
