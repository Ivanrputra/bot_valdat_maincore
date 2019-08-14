import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from mysql.connector import Error


def connect():

    try :
        global connection
        connection = mysql.connector.connect(host='10.112.82.94',
                                             database='valdat_test',
                                             user='ikrom',
                                             password='akuadmindb')

        # connection = mysql.connector.connect(host='localhost',
        #                                      database='db_bot',
        #                                      user='root',
        #                                      password='')

        if connection.is_connected():
               db_Info = connection.get_server_info()
               print("Connected to MySQL database... MySQL Server version on ",db_Info)
               cursor = connection.cursor()
               cursor.execute("select database();")
               record = cursor.fetchone()
               print ("Your connected to - ", record)
    except Error as e :
        print ("Error while connecting to MySQL", e)

def query(sql):
    try:
        global connection
        cursor = connection.cursor()
        cursor.execute(sql)
        # connection.commit()
        print("Query Berhasil di Eksekusi")


    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed inserting record into python_users table {}".format(error))
    return cursor

def comit():
    global connection
    connection.commit()