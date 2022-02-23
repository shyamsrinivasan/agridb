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
                      "TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = %(db_name)s")
        self.query_args = {'db_name': self.DBname}
        table_info = getinfo(self, tables=True)

        # create PySQltable objects for each table and create list of table objects
        # {'table_names': table_names, 'column_names': column_names}
        if table_info['table_names']:
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


class PySQLNewTable:
    def __init__(self, dbname=None, table_name=None):
        self.create_query = ''
        self.create_info = None
        if dbname is not None:
            self.DBname = dbname
        else:
            self.DBname = ''
        if table_name is not None:
            self.name = table_name
        else:
            self.name = ''
        self.properties = None
        self.column_names = None
        self.column_dtype = None
        self.is_null = None
        self.default = None
        self.primary_key = None
        self.unique_index = None
        self.unique_index_name = None
        self.key = None
        self.key_name = None
        self.constraint = None
        self.foreign_key = None
        self.ref_table = None
        self.ref_column = None
        self.on_delete = None

    def set_table_properties(self, info):
        """set table properties for creating new table based on given info"""
        self.properties = info
        self.column_names = info['column_names']
        self.column_dtype = info['column_dtype']
        self.is_null = info['column_is_null']
        if info.get('default_value') is not None:
            self.default = info['default_value']
        # primary key details
        if info.get('primary_key') is not None:
            self.primary_key = info['primary_key']
        # unique index details
        if info.get('unique_index') is not None:
            self.unique_index = info['unique_index']
        if info.get('unique_index_name') is not None:
            self.unique_index_name = info['unique_index_name']
        # index details
        if info.get('key') is not None:
            self.key = info['key']
        if info.get('key_name') is not None:
            self.key_name = info['key_name']

        # foreign key details
        fkey_flag = False
        if info.get('constraint') is None or info.get('foreign_key') is None or info.get('ref_table') is None or \
                info.get('ref_column') is None:
            print('Missing details to specify foreign key constraints.\nForeign constraints will not be added')
            fkey_flag = True
        else:
            # foreign keys
            if info.get('foreign_key') is not None:
                if len(info['foreign_key']) == len(info['constraint']):
                    self.foreign_key = info['foreign_key']
                else:
                    print('Number of foreign keys is NOT SAME as number of given constraint names')
                    fkey_flag = True
            else:
                print('Foreign key NOT GIVEN for foreign key constraints')
                fkey_flag = True
            # reference tables
            if info.get('ref_table') is not None:
                if len(info['ref_table']) == len(info['constraint']):
                    self.ref_table = info['ref_table']
                else:
                    print('Number of reference table names is NOT SAME as number of given constraint names')
                    fkey_flag = True
            else:
                print('Reference table NOT GIVEN for foreign key constraints')
                fkey_flag = True
            # reference columns
            if info.get('ref_column') is not None:
                if len(info['ref_column']) == len(info['constraint']):
                    self.ref_column = info['ref_column']
                else:
                    print('Number of reference columns is NOT SAME as number of given constraint names')
                    fkey_flag = True
            else:
                print('Reference column NOT GIVEN for foreign key constraints')
                fkey_flag = True
            # constraint names
            if not fkey_flag:
                self.constraint = info['constraint']
        # on delete condition
        if info.get('on_delete') is not None:
            self.on_delete = info['on_delete']

    def add_table(self):
        # add table referred by table object to self.DBname DB
        # call to accessdb function
        return



