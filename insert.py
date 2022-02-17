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


def add_table():
    """add table to existing db schema"""

    # define table properties (cols and other properties)
    table_property = table_def()
    # set query with ADD
    query = ("CREATE TABLE")
    # call func to db to make changes and commit
    # flag = query_db()
    return


def add_column():
    """add column to existing table in existing db"""
    return



