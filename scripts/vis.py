import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
 
    return None

def get_gdax(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM lake_rate WHERE platform = 'gdax'")
 
    return cur.fetchall()


def get_gdax_asks(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM lake_askprice WHERE platform = 'gdax'")
 
    return cur.fetchall()


def get_bitcoin_de_asks(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM lake_askprice WHERE platform = 'bitcoin.de'")
 
    return cur.fetchall()
