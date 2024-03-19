import psycopg2
from sshtunnel import SSHTunnelForwarder
from creds import USERNAME, PASSWORD, DB_NAME
from main import main_loop

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
            'port': server.local_bind_port
        }


        conn = psycopg2.connect(**params)
        curs = conn.cursor()
        print("Database connection established")

        # DB work here
        main_loop(curs)
        # print (curs)
        # print(curs.execute("SELECT * FROM genre"))


        conn.close()
except:
    print("Connection failed")
