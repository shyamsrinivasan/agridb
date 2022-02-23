from agrisql import PySQL, PySQLNewTable


def table_def(obj: PySQLNewTable):
    """define table properties for creating table in db"""

    table_property = None
    if obj.name:
        # add table to schema (unique id and foregin keys to be included)
        # table_name, col_name, col_type, index, foreign_index
        table_property = {'table_name': obj.name, 'column_names': ['itemid', 'name', 'type', 'cost', 'from_date',
                                                                   'to_date', 'serial_number'],
                          'column_dtype': ['TINYINT', 'VARCHAR(30)', 'VARCHAR(15)', 'DECIMAL(10,2)', 'TIMESTAMP',
                                           'TIMESTAMP', 'TINYINT(8)'],
                          'column_is_null': ['NOT NULL', 'NULL', 'NULL', 'NULL', 'NOT NULL', 'NULL', 'NOT NULL'],
                          'default_value': ['', '', '', '', 'CURRENT_TIMESTAMP', '', ''],
                          'primary_key': ['serial_number'], 'unique_index_name': ['serial_num_idx'],
                          'unique_index': ['serial_number'], 'key': ['itemid', 'name', 'cost'],
                          'key_name': ['itemid_idx', 'name_idx', 'cost_idx']}
                          # 'constraint': ['cons_name_1'],
                          # 'foreign_key': ['column_name_in_current_table'],
                          # 'ref_table': ['foreign_table'],
                          # 'ref_column': ['foreign_table_column'],
                          # 'on_delete': ['cascade']}
        obj.set_table_properties(table_property)
    return obj


def create_new_table(obj: PySQL, table_name=None):
    """add table to existing db schema"""

    # create new table object
    create_table_flag = False
    new_obj = PySQLNewTable(dbname=obj.DBname, table_name=table_name)

    # define table properties (cols and other properties)
    new_obj = table_def(new_obj)
    # set query with ADD
    # query = ("CREATE TABLE `{}`.`table_name` (`column_name` int(11) NULL, `column_2` varchar(55) NOT NULL, "
    #          "PRIMARY KEY (`column_name`), KEY `column_name` (`index_name`), "
    #          "UNIQUE INDEX `index_name` (`column_name`),
    #          "CONSTRAINT `constraint_name` FOREIGN KEY (`indexed_column_name`) "
    #          "REFERENCES `table_name` (`column_in_foreign_table`) ON DELETE CASCADE".format(self.DBname))
    # build query statement CREATE TABLE
    start = ("CREATE TABLE `{}`.`{}` (".format(new_obj.DBname, new_obj.name))
    ncols = len(new_obj.column_names)
    # add each column
    for icol, cols in enumerate(new_obj.column_names):
        if icol <= ncols-1:
            start += "`{}` {} {}".format(cols, new_obj.column_dtype[icol], new_obj.is_null[icol])
            if new_obj.default is not None:
                if new_obj.default[icol]:
                    start += " DEFAULT {}, ".format(new_obj.default[icol])
                else:
                    start += ", "
            else:
                start += ", "

    # add primary key
    if new_obj.primary_key is not None:
        start += "PRIMARY KEY ("
        npkey = len(new_obj.primary_key)
        for ip, pkey in enumerate(new_obj.primary_key):
            start += "`{}`".format(pkey)
            if ip < npkey-1:
                start += ", "
            elif ip == npkey-1:
                start += ")"

    # add unique index
    if new_obj.unique_index is not None:
        start += ", UNIQUE INDEX "
        nuid = len(new_obj.unique_index)
        for ip, uind in enumerate(new_obj.unique_index):
            start += new_obj.unique_index_name[ip]
            start += " (`{}`".format(uind)
            if ip < nuid-1:
                start += ", "
            elif ip == nuid-1:
                start += ")"

    # other key/index (additional keys for use with foreign key constraints)
    if new_obj.key is not None:
        # nkey = len(new_obj.key)
        for ip, ind in enumerate(new_obj.key):
            start += ", KEY "
            start += '`{}`'.format(new_obj.key_name[ip])
            start += " (`{}`)".format(ind)
            # if ip < nkey-1:
            #     start += ", "
            # elif ip == nkey-1:
            #     start += ")"

    # add foreign key constraint
    #          "CONSTRAINT `constraint_name` FOREIGN KEY (`indexed_column_name`) "
    #          "REFERENCES `table_name` (`column_in_foreign_table`) ON DELETE CASCADE".format(self.DBname))
    if new_obj.foreign_key is not None and new_obj.constraint is not None:
        ncons = len(new_obj.foreign_key)
        for ifk, frnkey in enumerate(new_obj.foreign_key):
            start += ", CONSTRAINT `{}` FOREIGN KEY (`{}`) REFERENCES `{}` (`{}`)".format(new_obj.constraint[ifk],
                                                                                          frnkey,
                                                                                          new_obj.ref_table[ifk],
                                                                                          new_obj.ref_column[ifk])
            if new_obj.on_delete is not None:
                start += " ON DELETE {}".format(new_obj.on_delete[ifk])
    # end CREATE TABLE block
    start += ") "

    # call func to db to make changes and commit
    new_obj.add_table(obj, start)
    if new_obj.add_flag:
        print('Table with name {} created in database {}'.format(new_obj.name, obj.DBname))
        create_table_flag = True
    else:
        print('Could not create table {} in database {}'.format(new_obj.name, obj.DBname))

    return create_table_flag


def add_column():
    """add column to existing table in existing db"""
    return



