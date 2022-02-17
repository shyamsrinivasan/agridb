from accessdb import query_db, getinfo


class PySQL:
    def __init__(self, dbconfig):
        self.DBname = dbconfig['database']
        # SQL connection properties in dictionary
        self.dbconfig = dbconfig
        # query and query arguments (change for different query calls)
        self.query = ''
        self.query_args = None
        # get info on all tables (table name, column names) in db
        self.tables = []
        self._get_tables()

    def _get_tables(self):
        """get all tables associated with DB using MySQl connector"""

        # get DB table info
        self.query = ("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE "
                      "TABLE_TYPE = 'BASE TABLE AND TABLE_SCHEMA = %(db_name)s")
        self.query_args = {'db_name': self.DBname}
        table_info = getinfo(self, tables=True)

        # create PySQltable objects for each table and create list of table objects
        # {'table_names': table_names, 'column_names': column_names}
        for i_table in table_info['table_names']:
            i_table_info = {'database': self.DBname, 'table_name': i_table}
            table_obj = PySQLtable(self, i_table_info)
            self.tables.append(table_obj)

    def add_table(self, info):
        """add table corresponding to table object to selected DB schema using MySQL connector"""

        # table_name, col_name, col_type, index, foreign_index
        # query = ("CREATE TABLE `table_name` ")
        self.query = ("CREATE TABLE `{}`.`table_name` (`column_name` int(11) NULL, `column_2` varchar(55) NOT NULL, "
                      "PRIMARY KEY (`column_name`), KEY `column_name` (`index_name`), "
                      "CONSTRAINT `constraint_name` FOREIGN KEY (`indexed_column_name`) "
                      "REFERENCES `table_name` (`column_in_foreign_table`) ON DELETE CASCADE".format(self.DBname))
        self.query_args = None
        query_db(self)


class PySQLtable:
    def __init__(self, db_obj, init):
        self.DBname = init['database']
        self.table_name = init['table_name']
        # get info on all columns in table
        self.column_names = None
        self.column_dtype = None
        self.is_null = None
        self.column_default = None
        self.columns = 0
        self._get_columns(db_obj)
        self.keys = init['key']
        self.foreign_key = init['foreign_key']

    def _get_columns(self, db_obj):
        """get all column names for listed tables in DB"""

        # get column names, column type, column nullablity and column default
        db_obj.query = ("SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_DEFAULT, IS_NULLABLE, COLUMN_KEY "
                        "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %(table_name)s")
        db_obj.query_args = {'table_name': self.table_name}
        column_info = getinfo(db_obj, columns=True)
        self.column_names = column_info['column_names']
        self.column_dtype = column_info['column_dtype']
        self.is_null = column_info['is_null']
        self.column_default = column_info['default']
        self.columns = len(self.column_names)

    def add_column(self, table_properties):
        """add column to specific table using ADD"""

        # add column to table object
        for i_col in table_properties:
            self.column_names.append(i_col['column_name'])
        # call mySQL connector to add new table to SQl db


class PySQlNewTable:
    def __init__(self):
        self.create_query = ''
        self.create_info = None
        self.DBname = ''

    def add_table(self):
        # add table referred by table object to self.DBname DB
        # call to accessdb function
        return



