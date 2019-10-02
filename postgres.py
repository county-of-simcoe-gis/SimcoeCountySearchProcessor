import psycopg2
import psycopg2.extras
from config import getConfig


def getConn(database='tabular'):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = getConfig(database)

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def query(conn, queryString):
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # execute a statement
        cur.execute(queryString)

        # display the PostgreSQL database server version
        #db_version = cur.fetchone()
        return cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        cur.close()


def queryOne(conn, queryString):
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # execute a statement
        cur.execute(queryString)

        # display the PostgreSQL database server version
        #db_version = cur.fetchone()
        return cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        cur.close()


def executeNonQuery(conn, insertString, values=None):
    try:
        cur = conn.cursor()

        # execute a statement
        if (values == None):
            cur.execute(insertString)
        else:
            cur.execute(insertString, values)
        conn.commit()
        return "OK"
    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR Caught: " + str(error))
        return "ERROR: " + str(error)
    finally:
        cur.close()
