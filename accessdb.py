import mysql.connector
from mysql.connector import errorcode


def querydb(dbconfig=None, query='', query_args=None, printflag=False):
    """connect to mysql db using connector and query, add to or
    update db using relevant queries passed as input"""

    flag = False
    if dbconfig is None:
        print('Empty database configuration information')
        return flag
    else:
        try:
            cnx = mysql.connector.connect(**dbconfig)
            cursor = cnx.cursor()
            if query_args is None:
                cursor.execute(query)
            else:
                cursor.execute(query, query_args)  # execute given query in mysql object

            if printflag:
                # print statement only good for taxdb.clients
                for (first_name, last_name, client_id) in cursor:
                    print("{} {} is a client with ID: {}".format(first_name, last_name, client_id))

            cnx.commit()
            flag = True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            cnx.rollback()
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
    return flag