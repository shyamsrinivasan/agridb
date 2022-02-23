import os.path
from agrisql import PySQL
from insert import create_new_table


if __name__ == '__main__':
    dbconfig = {'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'database': 'agridb',
                'raise_on_warnings': True}
    # create table object for further use with all config details
    db = PySQL(dbconfig)

    # add table to schema
    flag = create_new_table(db, table_name='items')

    # add data to table
    # col_name, values
    # db.add_entry()
    # update data in table
    # col_name, values
    # db.update_entry()
    # add addtional columns to existing tables
    # col_name, col_type, index, foreign_index
    # db.add_column()