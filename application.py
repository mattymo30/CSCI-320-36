# This is the main application file.
# Pushing out to github to have a starting point
from sshtunnel import SSHTunnelForwarder
import bcrypt # bcrypt hash used with mockaroo passwords
from psycopg2.extensions import cursor
from datetime import date

#global variable to track login status
logged_in = False

def main_loop(cursor, conn):
    while 1:
        user_input = input("Welcome to the movies database!\n"
                           "r: register new user\n"
                           "l: login to database\n"
                           "q: exit program\n"
                           "c: create collection test\n"
                           "s: search movies\n"
                           "f: follow another user\n"
                           "u: unfollow a user\n"
                           "q: exit program\n")
        if user_input == 'q':
            break
        elif user_input == 'l':
            login(cursor)
        elif user_input == 'r':
            createAccount(cursor, conn)
        elif user_input == 'c':
            createCollections(cursor, conn)
        elif user_input == 's':
            searchMovie(cursor)
        elif user_input == 'f':
            follow(cursor, conn)
        elif user_input == 'u':
            unfollow(cursor, conn)
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
    userid = 4179 # TODO Update this when login is fixed

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
            (relationshipid,userid,friendid)
        )
        conn.commit()
        print("Friend added!")

def getFriends(curs:cursor):
    userid = 4179 # TODO Update this when login is fixed
    curs.execute(
        """
        select p.username, f.relationshipid
        from person p
        inner join friendrelation f
        on p.userid = f.friendid and f.userid = %s;
        """,
        (userid,)
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
            else:
                print("Invalid username entered.")

"""----------------Authentication------------------"""

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
    """
    Attempt to log in a user to the database
    :param cursor: cursor to connect to the database and tables
    """
    # TODO Find a way to hold CUR_USER
    # if CUR_USER != "":
    #     print(f"You are already logged into an account: {CUR_USER}")
    #     return

    # User enters credentials
    username = input("Enter your username: ")
    entered_pass = input("Enter your password: ").encode('utf-8')

    # Gets password from DB
    cursor.execute("SELECT password FROM person WHERE username = %s",(username,))
    result = cursor.fetchone()

    # if the username did exist
    if not result:
        print("Username not found. Please try again.")
    
    actual_pass = result[0].encode('utf-8')
    if bcrypt.checkpw(entered_pass, actual_pass):
        print("Login successful")
        # TODO Find a way to hold CUR_USER
        # CUR_USER = username
    else:
        print("Incorrect password. Please try again.")


def listCollections(curs):
    print("Function to print a users collection")


def createCollections(cursor:cursor, conn):
    collectionname = input("Name this collection: ")
    cursor.execute("SELECT MAX(collectionid) FROM collection")
    max_id = cursor.fetchone()[0] + 1
    cursor.execute("INSERT INTO collection (collectionid, name) VALUES (%s, %s)", (max_id, collectionname))
    conn.commit()

    print('Collection created.')


def manageCollection(curs):
    print("A function to manage collections")


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