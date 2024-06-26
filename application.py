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
CLEAR_COMM = 'clear' # switch to cls if windows

# global variable to track login status
logged_in = False


def main_loop(cursor, conn):
    while 1:
        if CURR_USER: # Once logged in
            user_input = input(
                "Welcome to the movies database!\n"
                "c: to go to collections\n"
                "cc: create collection\n"
                "s: search movies\n"
                "rate: rate movie\n"
                "w: to watch a movie\n"
                "wc: to watch a collection\n"
                "u: Show user profile\n"
                "ss: Show hottest movies in town\n"
                "q: exit program\n"
                )
        else: # if not logged in
            user_input = input(
                "Welcome to the movies database!\n"
                "r: register new user\n"
                "l: login to database\n"
                "q: exit program\n"
            )
        system(CLEAR_COMM)

        if user_input == 'q':
            break
        elif user_input == 'l':
            login(cursor, conn)
        elif user_input == 'r':
            createAccount(cursor, conn)
        elif user_input == 'rate':
            rate_movie(cursor, conn)
        elif user_input == 'c':
            manageCollection(cursor, conn)
        elif user_input == 's':
            searchMovie(cursor)
        elif user_input == 'cc':
            createCollections(cursor, conn)
        elif user_input == 'u':
            user_profile(cursor, conn)
        elif user_input == 'w':
            watch_movie(cursor, conn)
        elif user_input == 'wc':
            watch_collection(cursor, conn)
        elif user_input == 'ss':
            statstics(cursor, conn)
        else:
            print("invalid command.")



def statstics(curs: cursor, conn):
    while 1:
        user_input = input("Type Any of the opitions\n"
                           "TM: Top movies in the past 90 Days\n"
                           "TF: Top movies among my followers\n"
                           "TR: Top 5 new releases of the month\n"
                           "R:  Recommended Movies for you\n")

        if user_input == "TM":
            curs.execute("SELECT m.movieID, m.title FROM WATCHES w JOIN MOVIE m ON w.movieID = m.movieID WHERE w.date_watched >= CURRENT_DATE - INTERVAL '90 days' GROUP BY m.movieID, m.title ORDER BY COUNT(w.movieID) DESC LIMIT 20;")
            results = curs.fetchall()
            print(tabulate(results, headers=['Movie Id', 'Movie Title']))
        elif user_input == "TF":
            curs.execute("SELECT m.movieID, m.title FROM friendrelation fr JOIN person u ON fr.friendID = u.userID JOIN WATCHES w ON u.userID = w.userID JOIN MOVIE m ON w.movieID = m.movieID WHERE fr.userID = %s GROUP BY m.movieID, m.title ORDER BY COUNT(w.movieid) DESC LIMIT 20;", (CURR_USER_ID, ))
            results = curs.fetchall()
            print(tabulate(results, headers=['Movie Id', 'Movie Title']))
        elif user_input == "TR":
            curs.execute("""SELECT m.movieID, m.title, ROUND(AVG(r.userRating), 2) AS avg_rating
                            FROM MOVIE m
                            JOIN RATES r ON m.movieID = r.movieID
                            JOIN RELEASED rd ON m.movieID = rd.movieID
                            WHERE EXTRACT(YEAR FROM rd.releaseDate) = EXTRACT(YEAR FROM CURRENT_DATE)
                            AND EXTRACT(MONTH FROM rd.releaseDate) = EXTRACT(MONTH FROM CURRENT_DATE)
                            GROUP BY m.movieID, m.title
                            ORDER BY avg_rating DESC
                            LIMIT 5;""")
            results = curs.fetchall()
            print(tabulate(results, headers=['Movie Id', 'Movie Title', 'Movie Rating']))
        elif user_input == "R":
            curs.execute("""WITH your_top_genres AS (
                            SELECT g.genreID, g.type, COUNT(*) AS genre_count
                            FROM person u
                            JOIN WATCHES w ON u.userID = w.userID
                            JOIN MOVIE m ON w.movieID = m.movieID
                            JOIN CATEGORIZE c ON m.movieID = c.movieID
                            JOIN GENRE g ON c.genreID = g.genreID
                            WHERE u.userid = %s
                            GROUP BY g.genreID, g.type
                            ORDER BY genre_count DESC
                            LIMIT 3
                        ),
                        friend_rated_movies AS (
                            SELECT w.movieID
                            FROM friendrelation fr
                            JOIN WATCHES w ON fr.friendID = w.userID
                            JOIN MOVIE m ON w.movieID = m.movieID
                            JOIN CATEGORIZE c ON m.movieID = c.movieID
                            JOIN your_top_genres yg ON c.genreID = yg.genreID
                            WHERE fr.userID = %s
                        )
                            SELECT m.movieID, m.title
                            FROM MOVIE m
                            JOIN CATEGORIZE c ON m.movieID = c.movieID
                            JOIN your_top_genres yg ON c.genreID = yg.genreID
                        WHERE m.movieID IN (
                            SELECT movieID FROM friend_rated_movies
                        )
                        GROUP BY m.movieID, m.title
                        ORDER BY COUNT(*) DESC
                    LIMIT 10;""", (CURR_USER_ID, CURR_USER_ID, ))
            results = curs.fetchall()
            print(tabulate(results, headers=['Movie Id', 'Movie Title']))
        elif user_input == "q":
            break


def rate_movie(curs: cursor, conn):
    """
    Ask the user to find a movie and rate it from a scale of 1-5
    :param conn: connection to database
    :param curs: cursor to connect to the database and tables
    """
    if CURR_USER is None:
        print("You aren't logged in!")
        return
    movieToRate = input("Type the name of the movie you want to rate: ")
    curs.execute("SELECT movieID FROM MOVIE where LOWER(title) LIKE LOWER(%s)", (movieToRate,))
    results = curs.fetchall()
    movie_id = results[0]
    while True:
        rating = int(input("Rate the movie from 1-5 stars: "))
        if rating < 1 or rating > 5:
            print("Rating must be between 1-5!")
        else:
            curs.execute("""INSERT INTO rates(userid, movieid, userrating)
            VALUES (%s, %s, %s)
            """,
                         (
                             CURR_USER_ID,
                             movie_id,
                             rating
                         )
                         )
            conn.commit()
            break


def watch_movie(curs: cursor, conn):
    # ask for name
    while 1:
        system(CLEAR_COMM)
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
        relationshipid = curs.fetchall()[0][0] + 2 # total relationships

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

def unfollow(curs:cursor, conn):
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
                conn.commit()
                return
        print("Invalid username entered.")

def get_top_10(curs):
    """
    Get a user's top 10 movies based on highest rating, most plays. or a
    combination of both
    :param curs: cursor to connect to the database and tables
    """
    # Get search parameters from the user
    while True:
        top_10_option = input("Get Top 10 From (ratings, plays, both): ").lower()
        if top_10_option in ['ratings','plays','both']:
            break
        print("Invalid Choice!")
    # user wants top 10 by ratings
    if top_10_option == 'ratings':
        curs.execute("""
            SELECT m.title, AVG(r.userrating) AS avg_rating
            FROM rates r
            JOIN movie m ON r.movieid = m.movieid
            WHERE r.userid = (%s)
            GROUP BY m.title
            ORDER BY avg_rating DESC
            LIMIT 10;
        """, (CURR_USER_ID,))
    elif top_10_option == 'plays':
        curs.execute("""
            SELECT m.title, COUNT(*) AS play_count
            FROM watches w
            JOIN movie m ON w.movieid = m.movieid
            WHERE w.userid = (%s)
            GROUP BY m.title
            ORDER BY play_count DESC
            LIMIT 10;
        """, (CURR_USER_ID,))
    else:
        curs.execute("""
            SELECT m.title, AVG(r.userrating) * COUNT(w.movieid) AS score
            FROM rates AS r
            JOIN watches AS w ON r.movieid = w.movieid
            JOIN movie AS m ON r.movieid = m.movieid
            WHERE r.userid = (%s)
            GROUP BY m.title
            ORDER BY score DESC
            LIMIT 10;
        """, (CURR_USER_ID,))

    results = curs.fetchall()

    # Print the results
    if results:
        print(f"Top 10 Movie Results based on {top_10_option}")
        for row in results:
            print(f"\t{row[0]}: {round(row[1], 1)}")
    else:
        print("No movies found! You need to rate or watch more movies!")

def user_profile(curs:cursor, conn):
    curs.execute( # Display number of following
        """
        select count(*) from friendrelation where userid = (%s);
        """,
        (CURR_USER_ID,)
    )
    following = curs.fetchall()[0][0]

    curs.execute( # Display the number of followers
        """
        select count(*) from friendrelation where friendid = (%s);
        """,
        (CURR_USER_ID,)
    )
    followers = curs.fetchall()[0][0]

    curs.execute( # Display number of collections the user has
        """
        select count(*) from user_owns_collection where userid = (%s);
        """,
        (CURR_USER_ID,)
    )
    coll_tot = curs.fetchall()[0][0]

    print(f"User: {CURR_USER}\n Collections: {coll_tot}\t Followers: {followers}\t Following: {following}\n")

    while(True):
        mode = input(
            "\n\nf: follow another user\n"
            "u: unfollow a user\n"
            "tt: Top ten\n\n"
        )

        if mode == 'f':
            follow(curs, conn)
        elif mode == 'u':
            unfollow(curs, conn)
        elif mode == 'tt':
            get_top_10(curs)
        elif mode == "q":
            return

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
        INSERT INTO account_creation (userid, date_created, time_created)
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
    menu_items = dict(enumerate(results, start=1))
    print(menu_items)
    while True:
        system(CLEAR_COMM)
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
        system(CLEAR_COMM)
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
        system(CLEAR_COMM)
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
                break

            # Ask the user if they want to sort again
            sort_again = input("Do you want to sort the results again? (yes/no): ").lower()
            if sort_again != "yes":
                break  # Exit the sorting loop if the user doesn't want to sort again

        # Ask the user if they want to search again
        search_again = input("Do you want to search again? (yes/no): ").lower()
        if search_again != "yes":
            break  # Exit the search loop if the user doesn't want to search again