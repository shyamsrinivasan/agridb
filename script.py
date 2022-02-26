import os.path
from agrisql import PySQL
from insert import create_new_table


if __name__ == '__main__':
    dbconfig = {'user': 'root',
                'password': 'root',
                'host': '127.0.0.1',
                'database': 'agridb',
                'raise_on_warnings': True}
    # create table object for further use with all config details
    db = PySQL(dbconfig)

    # add data to table - read data from excel file and write to mysql db
    # col_name, values
    # db.add_entry()
    # file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    # db
    # data = read_info(file_name)
    # loadclientinfo(data, dbconfig)

    # drop table from db
    db.remove_table(table_name='items')

    # define new table properties
    table_property = {'table_name': 'items', 'column_names': ['id', 'name', 'type', 'cost', 'from_date',
                                                              'to_date', 'serial_number'],
                      'column_dtype': ['TINYINT', 'VARCHAR(30)', 'VARCHAR(15)', 'DECIMAL(10,2)', 'TIMESTAMP',
                                       'TIMESTAMP', 'TINYINT'],
                      'column_is_null': ['NOT NULL', 'NULL', 'NULL', 'NULL', 'NOT NULL', 'NULL', 'NOT NULL'],
                      'default_value': ['', '', '', '', 'CURRENT_TIMESTAMP', '', ''],
                      'other_value': ['', '', '', '', '', '', 'AUTO_INCREMENT'],
                      'primary_key': ['serial_number'], 'unique_index_name': ['serial_num_idx'],
                      'unique_index': ['serial_number'], 'key': ['itemid', 'name', 'cost'],
                      'key_name': ['itemid_idx', 'name_idx', 'cost_idx']}
    # 'constraint': ['cons_name_1'],
    # 'foreign_key': ['column_name_in_current_table'],
    # 'ref_table': ['foreign_table'],
    # 'ref_column': ['foreign_table_column'],
    # 'on_delete': ['cascade']}

    # add table to schema
    flag = create_new_table(db, table_name='items', table_property=table_property)


    # update data in table
    # col_name, values
    # db.update_entry()
    # add addtional columns to existing tables
    # col_name, col_type, index, foreign_index
    # db.add_column()