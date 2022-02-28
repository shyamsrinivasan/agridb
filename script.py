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
    # file_name = os.path.join(os.getcwd(), 'sampleinfo.xlsx')
    # db.add_entry(file_name=file_name)   #, table_name='items')

    # drop table from db
    db.remove_table(table_name=['items', 'employee'])

    # define new table properties
    item_table = {'table_name': 'items', 'column_names': ['id', 'description', 'type', 'cost', 'from_date',
                                                          'to_date', 'serial_number'],
                  'column_dtype': ['INT', 'VARCHAR(30)', 'VARCHAR(15)', 'DECIMAL(10,2)', 'TIMESTAMP',
                                   'TIMESTAMP', 'INT'],
                  'column_is_null': ['NOT NULL', 'NULL', 'NULL', 'NULL', 'NOT NULL', 'NULL', 'NOT NULL'],
                  'default_value': ['', '', '', '', 'CURRENT_TIMESTAMP', '', ''],
                  'other_value': ['', '', '', '', '', '', 'AUTO_INCREMENT'],
                  'primary_key': ['serial_number'], 'unique_index_name': ['serial_num_idx'],
                  'unique_index': ['serial_number'], 'key': ['id', 'description', 'cost'],
                  'key_name': ['itemid_idx', 'name_idx', 'cost_idx']}
    # 'constraint': ['cons_name_1'],
    # 'foreign_key': ['column_name_in_current_table'],
    # 'ref_table': ['foreign_table'],
    # 'ref_column': ['foreign_table_column'],
    # 'on_delete': ['cascade']}
    employee_table = {'table_name': 'employee', 'column_names': ['id', 'name', 'gender', 'serial_number'],
                      'column_dtype': ['INT', 'VARCHAR(20)', 'VARCHAR(10)', 'INT'],
                      'column_is_null': ['NOT NULL', 'NOT NULL', 'NULL', 'NOT NULL'],
                      'default_value': ['', '', '', ''],
                      'other_value': ['', '', '', 'AUTO_INCREMENT'], 'primary_key': ['serial_number'],
                      'unique_index_name': ['serial_num_emp_idx'], 'unique_index': ['serial_number'],
                      'key': ['id', 'name'], 'key_name': ['empid_idx', 'empname_idx']}
    table_property = [item_table, employee_table]

    # add table to schema
    flag = create_new_table(db, table_name=['items', 'employee'], table_property=table_property)

    # update data in table
    # col_name, values
    # db.update_entry()
    # add addtional columns to existing tables
    # col_name, col_type, index, foreign_index
    # db.add_column()