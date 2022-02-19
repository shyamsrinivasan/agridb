from agrisql import PySQL, PySQLNewTable


def table_def(obj: PySQLNewTable):
    """define table properties for creating table in db"""

    table_property = None
    if obj.name:
        # add table to schema (unique id and foregin keys to be included)
        # table_name, col_name, col_type, index, foreign_index
        table_property = {'table_name': obj.name, 'column_names': ['itemid', 'name', 'type', 'cost', 'from_date', 'to_date'],
                          'column_dtype': ['TINYINT(8)', 'VARCHAR(30)', 'VARCHAR(15)', 'DECIMAL(10,2)', 'TIMESTAMP', 'TIMESTAMP'],
                          'column_is_null': ['NOT NULL', 'NULL', 'NULL', 'NULL', 'NOT NULL', 'NULL'],
                          'default_value': ['', '', '', '', '', ''],
                          'primary_key': ['itemid']}
        obj.set_table_properties(table_property)
    return obj


def add_table(obj: PySQL, table_name=None):
    """add table to existing db schema"""

    # create new table object
    new_obj = PySQLNewTable(dbname=obj.DBname, table_name=table_name)

    # define table properties (cols and other properties)
    new_obj = table_def(new_obj)
    # set query with ADD
    # query = ("CREATE TABLE `{}`.`table_name` (`column_name` int(11) NULL, `column_2` varchar(55) NOT NULL, "
    #          "PRIMARY KEY (`column_name`), KEY `column_name` (`index_name`), "
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
            start += "`%{}s`".format(pkey)
            if ip < npkey-1:
                start += ", "
            elif ip == npkey-1:
                start += ")"
    # add foreign key constraint
    # end CREATE TABLE block
    start += ") "

    # call func to db to make changes and commit
    # flag = query_db()
    return


def add_column():
    """add column to existing table in existing db"""
    return



