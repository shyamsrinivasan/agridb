import mysql.connector
from mysql.connector import errorcode


def query_db(sqlobj, printflag=False):
    """connect to mysql db using connector and query, add to or
    update db using relevant queries passed as input"""

    flag = False
    if sqlobj.dbconfig is None:
        print('Empty database configuration information')
        return flag
    else:
        try:
            cnx = mysql.connector.connect(**sqlobj.dbconfig)
            cursor = cnx.cursor()
            if sqlobj.query_args is None:
                cursor.execute(sqlobj.query)
            else:
                cursor.execute(sqlobj.query, sqlobj.query_args)  # execute given query in mysql object

            # if printflag:
            #     # print statement only good for taxdb.clients
            #     for (first_name, last_name, client_id) in cursor:
            #         print("{} {} is a client with ID: {}".format(first_name, last_name, client_id))

            cnx.commit()
            flag = True

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("SQL Error: Username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("SQL Error: Database does not exist")
            elif err.errno == errorcode.ER_KEY_COLUMN_DOES_NOT_EXITS:
                print('SQL Error: Column specified in query does not exist')
            elif err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print('SQL Error: Table with name to be added already exists in DB')
            else:
                print(err)
            cnx.rollback()
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
    return flag


def getinfo(sqlobj, items=False, id_only=False, tables=False, columns=False):
    """get entries from db using given query. Fetch all relevant details from all tables in db"""

    result = None
    try:
        cnx = mysql.connector.connect(**sqlobj.dbconfig)
        cursor = cnx.cursor(dictionary=True)
        if sqlobj.query_args is None:
            cursor.execute(sqlobj.query)
        else:
            cursor.execute(sqlobj.query, sqlobj.query_args)  # execute given query in mysql object
        item_id, item_name, item_type, item_cost = [], [], [], []
        table_names, column_names, column_dtype, column_default, is_null = [], [], [], [], []
        for row in cursor:
            if tables:
                table_names.append(row['TABLE_NAME'])
            if columns:
                column_names.append(row['COLUMN_NAME'])
                column_dtype.append(row['DATA_TYPE'])
                column_default.append(row['COLUMN_DEFAULT'])
                is_null.append(row['IS_NULLABLE'])
            if id_only:
                item_id.append(row['id'])
            if items:
                item_id.append(row['id'])
                item_name.append(row['description'])
                item_type.append(row['type'])
                item_cost.append(row['cost'])
        result = {'table_names': table_names, 'column_names': column_names, 'column_dtype': column_dtype,
                  'is_null': is_null, 'default': column_default}
        if items:
            result = {'id': item_id, 'description': item_name, 'type': item_type, 'cost': item_cost}
        if id_only:
            result = {'id': item_id}
        cursor.close()
        cnx.close()
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
    return result



