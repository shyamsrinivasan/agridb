import os.path
from agrisql import PySQL
from insert import add_table


def table_def(table_name=None):
    """define table properties for creating table in db"""

    if table_name is None:
        table_name = 'new_table'

    # add table to schema (unique id and foregin keys to be included)
    # table_name, col_name, col_type, index, foreign_index
    table_property = {'table_name': 'items', 'column_names': ['itemid', 'name', 'type', 'cost', 'from_date',
                                                                'to_date'],
                      'column_dtype': ['TINYINT(8)', 'VARCHAR(45)', 'VARCHAR(15)', 'DECIMAL(10,2)', 'TIMESTAMP',
                                       'TIMESTAMP'],
                      'column_is_null': ['NOT NULL', 'NULL', 'NULL', 'NULL', 'NOT NULL', 'NULL'],
                      'default_value': [],
                      'primary_key': ['itemid']}
    return table_property


if __name__ == '__main__':
    dbconfig = {'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'database': 'agridb',
                'raise_on_warnings': True}
    # create table object for further use with all config details
    db = PySQL(dbconfig)

    # add table to schema
    table_properties = table_def('items')
    db.add_table(table_properties)
    # add data to table
    # col_name, values
    # db.add_entry()
    # update data in table
    # col_name, values
    # db.update_entry()
    # add addtional columns to existing tables
    # col_name, col_type, index, foreign_index
    # db.add_column()