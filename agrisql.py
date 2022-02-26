import pandas

from accessdb import query_db, getinfo
import pandas as pd


class PySQL:
    def __init__(self, dbconfig):
        self.DBname = dbconfig['database']
        # SQL connection properties in dictionary
        self.dbconfig = dbconfig
        # query and query arguments (change for different query calls)
        self.query = ''
        self.query_args = None
        self.query_flag = None
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
        if table_info['table_names']:
            for i_table in table_info['table_names']:
                i_table_info = {'database': self.DBname, 'table_name': i_table}
                table_obj = PySQLtable(self, i_table_info)
                self.tables.append(table_obj)

    def add_table(self, query, query_args=None):
        """add table corresponding to table object to selected DB schema using MySQL connector"""

        self._reset_query_flag()
        self.query = query
        if query_args is not None:
            self.query_args = query_args
        self.query_flag = query_db(self)

    def remove_table(self, table_name=None):
        """remove a table in given db object"""

        self._reset_query_flag()
        if table_name is not None:
            db_tables = [i_table.name for i_table in self.tables]
            if table_name in db_tables:
                self.query = ("DROP TABLE `{}`.`{}`".format(self.DBname, table_name))
                self.query_args = None
                if self.query_flag is None:
                    self.query_flag = query_db(self)

                if self.query_flag:
                    print("Table {} removed from DB {}".format(table_name, self.DBname))
                    # get new list of tables in db
                    self.tables = []
                    self._get_tables()
            else:
                print("Table `{}` is not present in DB `{}`".format(table_name, self.DBname))

    def _reset_query_flag(self):
        """reset query flag to None before running new queries if flag is not None"""

        if self.query_flag is not None:
            self.query_flag = None
            print('Query flag reset to None')
        else:
            print('Query flag is already None')

    @staticmethod
    def _read_info(file_name=None) -> pandas.DataFrame:
        """read client info from file to dataframe"""

        # read excel file with client data into pandas
        if file_name is not None:
            df = pd.read_excel(file_name, 'info', engine='openpyxl')
        else:
            df = None

        # fill nan values (for non NN columns in db) with appropriate replacement
        if df is not None:
            df['type'].fillna('none', inplace=True)

            # get first and last names from full name
            # df = df.assign(firstname=pd.Series(firstname))
            # df = df.assign(lastname=pd.Series(lastname))

            # convert cost to float
            df['cost'] = df['cost'].map(float)
        return df

    def add_entry(self, file_name=None, table_name=None):
        """load client info from dataframe to db"""

        # read data from file to pd.dataframe
        if file_name is not None:
            data = self._read_info(file_name)
        else:
            data = self._read_info()

        if table_name is not None:
            # directly add data to table.name = table_name
            db_table_name = [(idx, i_table.name) for idx, i_table in enumerate(self.tables) if i_table.name == table_name]
            if db_table_name:
                db_table_name = db_table_name[0][1]
                pos = db_table_name[0][0]
                print("Adding data to table {} in current DB {}".format(db_table_name, self.DBname))
                # add data to this table with table object
                self.tables[pos].add_data(data)
            else:
                print('Table {} is not present in current DB {}. Available tables are:'.format(table_name, self.DBname))
                for i_table in self.tables:
                    print(format(i_table.name))
        else:
            # find table to which data needs to be added - compare columns in data and tables
            db_columns = [i_table.column_names for i_table in self.tables]
            chosen_col = [[True if i_col in i_table else False for i_col in data.columns.values] for i_table in db_columns]
            chosen_table = [True for i_table in chosen_col if all(i_table)]
            tab_idx = [idx for idx, val in enumerate(chosen_table) if val][0]
            print('Chosen table for data entry: {}'.format(self.tables[tab_idx].name))
            self.tables[tab_idx].add_data(data, self)
            # if all(col_in_db_col):

    def last_item_id(self, table_obj, id_col):
        """get last id (biggest) from DB. Usually used to client id to new added entries"""

        # search db for latest clientid
        self._reset_query_flag()
        self.query = "SELECT %(id_column)s FROM {}.{}".format(self.DBname, table_obj.name)
        self.query_args = {'id_column': id_col}
        db_info = getinfo(self, id_only=True)

        if db_info is not None:
            if db_info['id']:
                large_id = max(db_info['id'])
            else:
                print('No previous existing ID. Initializing new ID from 1001.')
                large_id = 1000
        else:
            large_id = None
        return large_id

    def check_db(self, query, info: dict):         #, qtype=-1, get_address=False, get_password=False):
        """check if given entry is already present in DB based on given info (name/type/item id)
        and return all details of said item"""

        self._reset_query_flag()
        self.query = query
        self.query_args = info
        dbinfo = getinfo(self, items=True)
        return dbinfo


class PySQLtable:
    def __init__(self, db_obj, init):
        self.DBname = init['database']
        self.name = init['table_name']
        # get info on all columns in table
        self.column_names = None
        self.column_dtype = None
        self.is_null = None
        self.column_default = None
        self.columns = 0
        self._get_columns(db_obj)
        if init.get('key') is not None:
            self.keys = init['key']
        else:
            self.keys = None
        if init.get('foreign_key') is not None:
            self.foreign_key = init['foreign_key']
        else:
            self.foreign_key = None

    def _get_columns(self, db_obj):
        """get all column names for listed tables in DB"""

        # get column names, column type, column nullablity and column default
        db_obj.query = ("SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_DEFAULT, IS_NULLABLE, COLUMN_KEY "
                        "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %(table_name)s")
        db_obj.query_args = {'table_name': self.name}
        column_info = getinfo(db_obj, columns=True)
        self.column_names = column_info['column_names']
        self.column_dtype = column_info['column_dtype']
        self.is_null = column_info['is_null']
        self.column_default = column_info['default']
        self.columns = len(self.column_names)

    def _assign_id(self, db_obj: PySQL, data: object):
        """assign client ids to new clients from client info file"""

        # search db for latest clientid
        large_id = db_obj.last_item_id(self, id_col='id')

        # add client ids to new clients
        if large_id is not None:
            nrows = data.shape[0]
            large_id += 1
            new_ids = [large_id + irow for irow in range(0, nrows)]
            data = data.assign(id=pd.Series(new_ids))
        else:
            print('Could not access database to get existing IDs: Assign IDs manually \n')
        return data

    @staticmethod
    def _list2dict(info_dict: dict) -> list:
        """convert dictionary of list to list of dictionaries for info obtained from db"""

        new_list, new_dict = [], {}
        nvals = max([len(info_dict[key]) for key, _ in info_dict.items() if info_dict[key]])  # size of new final list

        for ival in range(0, nvals):
            for key, _ in info_dict.items():
                if info_dict[key]:
                    new_dict[key] = info_dict[key][ival]
                else:
                    new_dict[key] = ''
            new_list.append(new_dict)
        return new_list

    def _check_table(self, info: dict, db_obj: PySQL):
        """check table in db for existing entry"""

        db_info = None
        if self.name == 'items':
            query = ("SELECT description, type FROM {}.{} "
                     "WHERE description = %(description)s OR type = %(type)s OR "
                     "id = %(id)s".format(self.DBname, self.name))
            db_info = db_obj.check_db(query, info)
        else:
            print("Table {} is not present in DB {}".format(self.name, self.DBname))

        return db_info

    def add_data(self, data, db_obj=None):
        """load client info from dataframe to db"""

        # assign client id to new clients
        data = self._assign_id(db_obj, data)

        data_list = data.to_dict('records')
        # loadclientinfo(data, dbconfig)
        for idx, i_entry in enumerate(data_list):
            # check if new entry in db (same name/pan)
            db_info = self._check_table(i_entry, db_obj)
            info_list = self._list2dict(db_info)
        #     name_check, _, _, _ = compare_info(i_client, info_list[0])
        #     if name_check:  # if present, only update existing entry (address) or return error
        #         print("Client {} is present in DB with ID {}. "
        #               "Proceeding to update existing entry".format(i_client['name'], info_list[0]['clientid']))
        #         # change client id to one obtained from db
        #         i_client['clientid'] = info_list[0]['clientid']
        #
        #         # get existing client info (pan,address) using client info from db
        #         db_info = check_db(dbconfig, i_client, qtype=1, get_address=True)
        #         info_list = list2dict(db_info)
        #         # check if same address in DB
        #         _, _, _, add_check = compare_info(i_client, info_list[0], check_address=True)
        #         if not add_check:
        #             update1entry(dbconfig, info_list[0], i_client)  # update DB if address is not same
        #         else:
        #             print("{} with ID {} has same address in DB. "
        #                   "No changes made".format(i_client['name'], i_client['clientid']))
        #     else:  # else add new entry
        #         loadsingleclientinfo(dbconfig, i_client)
        # return

    def add_column(self, table_properties):
        """add column to specific table using ADD"""

        # add column to table object
        for i_col in table_properties:
            self.column_names.append(i_col['column_name'])
        # call mySQL connector to add new table to SQl db


class PySQLNewTable:
    def __init__(self, dbname=None, table_name=None):
        self.create_query = None
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
        self.other_value = None
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

        self.add_flag = None

    def set_table_properties(self, info):
        """set table properties for creating new table based on given info"""

        self.properties = info
        if info is None:
            print('No properties provided for new table. No new table can be created.')
            return self

        if info.get('column_names') is not None:
            self.column_names = info['column_names']
        if info.get('column_dtype') is not None:
            self.column_dtype = info['column_dtype']
        if info.get('column_is_null') is not None:
            self.is_null = info['column_is_null']
        if info.get('default_value') is not None:
            self.default = info['default_value']
        if info.get('other_value') is not None:
            self.other_value = info['other_value']
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

        return self

    def add_table(self, db_obj: PySQL, query, query_args=None):
        """add table referred by table object to db_obj.DBname DB by calling to accessdb function"""

        if query and query_args is None:
            self.create_query = query
            db_obj.add_table(self.create_query)
        elif query_args is not None:
            self.create_info = query_args
            db_obj.add_table(self.create_query, self.create_info)
        self.add_flag = db_obj.query_flag
        return



