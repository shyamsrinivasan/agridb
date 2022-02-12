class PySQL:
    def __init__(self, dbconfig):
        self.DBname = dbconfig['database']
        # SQL connection properties in dictionary
        self.dbconfig = dbconfig
        # query and query arguments (change for different query calls)
        self.query = ''
        self.query_args = None
        # get info on all tables (table name, column names) in db
        self._get_tables()

    def _get_tables(self):
        """get all tables associated with DB using MySQl connector"""

        # get DB table info
        self.query = ("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE "
                      "TABLE_TYPE = 'BASE TABLE AND TABLE_SCHEMA = %(db_name)s")
        self.query_args = {'db_name': self.DBname}

        # create PySQltable objects for each table

    def _get_columns(self):
        """get all column names for listed tables in DB"""

        self.query = ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                      "WHERE TABLE_NAME = %(table_name)s")
        self.query_args = {'table_name': 'x'}


class PySQLtable:
    def __init__(self, init):
        self.DBname = init['database']
        self.table_name = init['table_name']
        self.column_names = init['column_names']
        self.columns = len(init['column_names'])
        self.column_dtype = init['column_dtype']
        self.keys = init['key']
        self.foreign_key = init['foreign_key']

    def add_table(self):
        """add table corresponding to table object to selected DB schema using MySQL connector"""

        # table_name, col_name, col_type, index, foreign_index

    def add_column(self, table_properties):
        """add column to specific table using ADD"""

        # add column to table object
        for i_col in table_properties:
            self.column_names.append(i_col['column_name'])
        # call mySQL connector to add new table to SQl db

