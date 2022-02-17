from agrisql import PySQL, PySQLNewTable


def table_def(obj: PySQLNewTable):
    """define table properties for creating table in db"""

    table_property = None
    if obj.name:
        # add table to schema (unique id and foregin keys to be included)
        # table_name, col_name, col_type, index, foreign_index
        table_property = {'table_name': obj.name, 'column_names': ['itemid', 'name', 'type', 'cost', 'from_date', 'to_date'],
                          'column_dtype': ['TINYINT(8)', 'VARCHAR(45)', 'VARCHAR(15)', 'DECIMAL(10,2)', 'TIMESTAMP', 'TIMESTAMP'],
                          'column_is_null': ['NOT NULL', 'NULL', 'NULL', 'NULL', 'NOT NULL', 'NULL'],
                          'default_value': [],
                          'primary_key': ['itemid']}
        obj.set_table_properties(table_property)
    return obj


def add_table(obj: PySQL, table_name=None):
    """add table to existing db schema"""

    # create new table object
    new_table_obj = PySQLNewTable(dbname=obj.DBname, table_name=table_name)

    # define table properties (cols and other properties)
    new_table_obj = table_def(new_table_obj)
    # set query with ADD
    query = ("CREATE TABLE")
    # call func to db to make changes and commit
    # flag = query_db()
    return


def add_column():
    """add column to existing table in existing db"""
    return



