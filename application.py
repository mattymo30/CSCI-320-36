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
import time

CURR_USER = None
CURR_USER_ID = None

# global variable to track login status
logged_in = False


def main_loop(cursor, conn):
    while 1:
        if CURR_USER: # Once logged in
            user_input = input(
                "Welcome to the movies database!\n"
                "r: register new user\n"
                "l: login to database\n"
                "c: to go to collections\n"
                "q: exit program\n"
                "cc: create collection\n"
                "s: search movies\n"
                "w: to watch a movie\n"
                "wc: to watch a collection\n"
                "f: follow another user\n"
                "u: unfollow a user\n"
                "q: exit program\n"
                )
        else: # if not logged in
            user_input = input(
                "Welcome to the movies database!\n"
                "r: register new user\n"
                "l: login to database\n"
                "q: exit program\n"
            )
            
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
        elif user_input == 'f':
            follow(cursor, conn)
        elif user_input == 'u':
            unfollow(cursor, conn)
        else:
            print("invalid command.")


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


def watch_movie(curs: cursor, conn):
    # ask for name
    while 1:
        system('clear')
        movieSearch = input("Type the name of the movie you want to watch or press q ")
        if movieSearch == "q":
            break
        else:
            curs.execute("SELECT movieID, title FROM MOVIE WHERE LOWER(title) LIKE LOWER(%s)", (movieSearch, ))
            results = curs.fetchall()
            print(tabulate(results, headers=['Movie Id', 'Movie Title']))
            movieToPlay = input("Type the id the movie you wish to play ")
            curs.execute("INSERT INTO watches (userid, movieid, date_watched) VALUES (%s, %s, NOW()::timestamp);", (CURR_USER_ID, movieToPlay))
            conn.commit()
            print("Watching Movie")
            time.sleep(1.5)


"""-------------------Friends---------------------"""

def search_users(curs:cursor, email:str):
    # Gets potential friend info
    curs.execute("select username,userid from person where email = (%s);",(email,))
    result = curs.fetchall()
    if result == []: # Not in DB
        print("User not found.")
        return None
    username = result[0][0]
    userid = result[0][1]
    
    # Confirms follow
    answer = input(f"\nEnter y if you want to follow '{username}'.\nEnter n to cancel.\n")
    if answer == "y":
        return userid
    elif answer == "n":
        return None
    else:
        print("Invalid response. Try again.")
        return None
    

def follow(curs:cursor, conn):
    email = ""

    while(True):
        # Prompt user for email
        email = input("\nFollow Users (press q to exit).\nSearch for a user by their email: ")
        if email == "q": # Break case
            break

        # Search email
        friendid = search_users(curs, email)
        if not friendid: # Problem with search
            break

        curs.execute("select count(*) from friendrelation")
        relationshipid = curs.fetchall()[0][0] + 1 # total relationships

        # Make them friends
        curs.execute(
            """
            INSERT INTO friendrelation (relationshipid, userid, friendid)
            VALUES (%s, %s, %s)
            """,
            (relationshipid,CURR_USER_ID,friendid)
        )
        conn.commit()
        print("Friend added!")

def getFriends(curs:cursor):
    curs.execute(
        """
        select p.username, f.relationshipid
        from person p
        inner join friendrelation f
        on p.userid = f.friendid and f.userid = %s;
        """,
        (CURR_USER_ID,)
    )
    # list of (username, relationshipid) tuples
    freinds = curs.fetchall()

    print("\nAll Friends:")
    for i in range(len(freinds)):
        print(f"{i+1}. {freinds[i][0]}")
    return freinds

def unfollow(curs:cursor):
    while(True):
        # Display friends of user
        all_friends:dict = getFriends(curs)
        username = input("\nUnfollow Users (press q to exit).\nEnter the username you want to remove: ")
        if username == "q": # Break case
            break

        # Deletes friend
        for friend in all_friends:
            if friend[0] == username:
                curs.execute(
                    """
                    DELETE FROM friendrelation WHERE relationshipid = (%s);
                    """,
                    (friend[1],)
                )
                print(f"Successfully unfollowed {username}")
            else:
                print("Invalid username entered.")

"""----------------Authentication------------------"""


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
        INSERT INTO person (userid, username, password, email, fname, lname, dob)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            int(total_users + 1),
            username,
            password,
            email,
            fname,
            lname,
            dob
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
        CURR_USER = username
        cursor.execute("SELECT userID FROM person WHERE username = %s", (CURR_USER,))
        CURR_USER_ID = cursor.fetchone()[0]
        print(f"Login successful.\n Welcome {CURR_USER}")

        login_date = date.today()
        t = time.localtime()
        login_time = time.strftime("%H:%M:%S", t)
        cursor.execute("""select count(*) from login""")
        relationshipid = cursor.fetchall()[0][0] + 1
        cursor.execute("""
            INSERT INTO login (loginid, userid, date_logged_in, time_logged_in)
            VALUES (%s, %s, %s, %s)
            """,
            (
                relationshipid,
                CURR_USER_ID,
                login_date,
                login_time
            )
        )
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


def record_collection_watch(collectionID: int, curs: cursor, conn):
    print(collectionID)
    curs.execute("SELECT m.movieID, m.title, m.mpaa, m.length FROM CONTAINS c JOIN MOVIE m ON c.movieID = m.movieID WHERE c.collectionID = %s;", (collectionID, ))
    results = curs.fetchall()
    print(results)
    for x in range(len(results)):
        print(results[x][0])
        curs.execute("INSERT INTO watches (userid, movieid, date_watched) VALUES (%s, %s, NOW()::timestamp);", (CURR_USER_ID, results[x][0]))
        conn.commit()
    print("Watching all movies collection")
    time.sleep(1.5)


def watch_collection(curs: cursor, conn):
    # ask for name
    curs.execute("SELECT c.collectionid, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, CONCAT(FLOOR(SUM(m.length) / 3600), ':', CASE WHEN FLOOR((SUM(m.length) %% 3600) / 60) < 10 THEN CONCAT('0', FLOOR((SUM(m.length) %% 3600) / 60)) ELSE CAST(FLOOR((SUM(m.length) %% 3600) / 60) AS VARCHAR) END ) AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID LEFT JOIN CONTAINS cm ON c.collectionID = cm.collectionID LEFT JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC;", (CURR_USER_ID,))
    # curs.execute('SELECT c.collectionid, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, CONCAT(FLOOR(SUM(m.length) / 3600), ':', CASE WHEN FLOOR((SUM(m.length) % 3600) / 60) < 10 THEN CONCAT('0', FLOOR((SUM(m.length) % 3600) / 60)) ELSE CAST(FLOOR((SUM(m.length) % 3600) / 60) AS VARCHAR) END ) AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID LEFT JOIN CONTAINS cm ON c.collectionID = cm.collectionID LEFT JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC;', ((CURR_USER_ID,))
    print ("Executed the cursor")
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
            record_collection_watch(menu_items[int(selection)][0], curs, conn)
            curs.execute("SELECT c.collectionid, c.name AS collection_name, COUNT(cm.movieID) AS num_movies, CONCAT(FLOOR(SUM(m.length) / 3600), ':', CASE WHEN FLOOR((SUM(m.length) %% 3600) / 60) < 10 THEN CONCAT('0', FLOOR((SUM(m.length) %% 3600) / 60)) ELSE CAST(FLOOR((SUM(m.length) %% 3600) / 60) AS VARCHAR) END ) AS total_length FROM COLLECTION c JOIN USER_OWNS_COLLECTION uoc ON c.collectionID = uoc.collectionID LEFT JOIN CONTAINS cm ON c.collectionID = cm.collectionID LEFT JOIN MOVIE m ON cm.movieID = m.movieID WHERE uoc.userID = %s GROUP BY c.collectionID, c.name ORDER BY c.name ASC;", (CURR_USER_ID,))
            results = list(curs.fetchall())
            print(results)
            menu_items = dict(enumerate(results, start=1))
            print(menu_items)

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
    while True:
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

        # Sorting loop
        while True:
            # Sorting the result
            sort_option = input("Sort results by (name/studio/genre/release date): ").lower()
            if sort_option == "name":
                sort_clause = " ORDER BY m.title"
            elif sort_option == "studio":
                sort_clause = " ORDER BY p.fname, p.lname"
            elif sort_option == "genre":
                sort_clause = " ORDER BY cat.genreid"
            elif sort_option == "release date":
                sort_clause = " ORDER BY r.releasedate"
            else:
                print("Invalid sort option.")
                return
            
            # Prompt for sorting order
            sort_order = input("Sort in (ascending/descending) order: ").lower()
            if sort_order == "ascending":
                sort_clause += " ASC"
            elif sort_order == "descending":
                sort_clause += " DESC"
            else:
                print("Invalid sort order.")
                return

            # Execute the constructed query
            curs.execute(sql_query + sort_clause)
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

            # Ask the user if they want to sort again
            sort_again = input("Do you want to sort the results again? (yes/no): ").lower()
            if sort_again != "yes":
                break  # Exit the sorting loop if the user doesn't want to sort again

        # Ask the user if they want to search again
        search_again = input("Do you want to search again? (yes/no): ").lower()
        if search_again != "yes":
            break  # Exit the search loop if the user doesn't want to search again




def getFriends(curs):
    # Write the querty to get and print friends
    print("Function to get friends")
