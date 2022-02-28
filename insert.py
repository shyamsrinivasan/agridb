from agrisql import PySQL, PySQLNewTable


def create_single_new_table(obj: PySQL, table_name=None, table_property=None):
    """add one new table to existing db schema"""

    # create new table object
    create_table_flag = False
    new_obj = PySQLNewTable(dbname=obj.DBname, table_name=table_name)

    # define table properties (cols and other properties)
    new_obj = new_obj.set_table_properties(table_property)

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
        if icol <= ncols - 1:
            start += "`{}` {} {}".format(cols, new_obj.column_dtype[icol], new_obj.is_null[icol])
            if new_obj.default is not None:
                if new_obj.other_value is not None and (new_obj.other_value[icol] and not new_obj.default[icol]):
                    start += " {}, ".format(new_obj.other_value[icol])
                elif new_obj.default[icol]:
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
            if ip < npkey - 1:
                start += ", "
            elif ip == npkey - 1:
                start += ")"

    # add unique index
    if new_obj.unique_index is not None:
        start += ", UNIQUE INDEX "
        nuid = len(new_obj.unique_index)
        for ip, uind in enumerate(new_obj.unique_index):
            start += new_obj.unique_index_name[ip]
            start += " (`{}`".format(uind)
            if ip < nuid - 1:
                start += ", "
            elif ip == nuid - 1:
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


def create_new_table(obj: PySQL, table_name=None, table_property=None):
    """add table to existing db schema"""

    create_table_flag = False
    if table_name is not None and table_property is not None:
        if isinstance(table_name, list) and isinstance(table_property, list):
            create_table_flag = [False] * len(table_name)
            if len(table_name) == len(table_property):
                for idx, i_table in enumerate(table_name):
                    create_table_flag[idx] = create_single_new_table(obj, table_name=i_table,
                                                                     table_property=table_property[idx])
            else:
                print('Number of table names and number of table properties DOES NOT MATCH')
        else:
            create_table_flag = create_single_new_table(obj, table_name=table_name, table_property=table_property)

    return create_table_flag


def add_column():
    """add column to existing table in existing db"""
    return



