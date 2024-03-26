import psycopg2
from sshtunnel import SSHTunnelForwarder
from creds import USERNAME, PASSWORD, DB_NAME
from application import main_loop
from psycopg2 import DatabaseError

try:
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=USERNAME,
                            ssh_password=PASSWORD,
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'database': DB_NAME,
            'user': USERNAME,
            'password': PASSWORD,
            'host': 'localhost',
            'port': server.local_bind_portr
        }


        conn = psycopg2.connect(**params)
        curs = conn.cursor()
        print(type(curs))
        print("Database connection established")

        # DB work here
        try: # Catches DB errors
            main_loop(curs, conn)
        except(Exception, DatabaseError) as error:
            print(error)

        conn.close()
except:
    print("Connection failed")
