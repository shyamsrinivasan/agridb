import os.path


if __name__ == '__main__':
    dbconfig = {'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'database': 'agridb',
                'raise_on_warnings': True}

    # add table to schema (unique id and foregin keys to be included)
    # table_name, col_name, col_type, index, foreign_index
    # add data to table
    # col_name, values
    # update data in table
    # col_name, values
    # add addtional columns to existing tables
    # col_name, col_type, index, foreign_index