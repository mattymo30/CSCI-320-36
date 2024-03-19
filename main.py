# This is the main application file.
# Pushing out to github to have a starting point

import psycopg2
from sshtunnel import SSHTunnelForwarder
import creds

username = creds.username
password = creds.password
dbName = "p320_36"


try:
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'database': dbName,
            'user': username,
            'password': password,
            'host': 'localhost',
            'port': server.local_bind_port
        }


        conn = psycopg2.connect(**params)
        curs = conn.cursor()
        print("Database connection established")

        # DB work here....

        conn.close()
except:
    print("Connection failed")




