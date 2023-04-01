import pandas as pd
import dask.dataframe as dd


def prepare_env_data(file_name, sep='\t'):
    """read data from csv file and prepare for db upload"""

    # data = pd.read_csv(file_name, sep=sep, header=0)
    data = dd.read_csv(file_name, sep=sep, header=0)
    # parse df (remove NaN and drop repeated rows
    column_names = data.columns.values.tolist()
    filter_data = data[data[column_names[0]] != column_names[0]]  # remove rows with data similar to column headers
    filter_data = filter_data.dropna()  # get only valid data (NaN and other strings removed)
    data = change_column_name_env(filter_data)

    # combine date and time into one new column
    # get full time
    time_only = data['Hour'] + ':' + data['Minute']  # + ':' + data['Second']
    data = data.drop(['Second'], axis=1)

    # get full date
    date = data['Year'] + '-' + data['Month'] + '-' + data['Date']

    # get full date and time
    date_time = date + ' ' + time_only
    # # add new date_time column to data
    # filter_data = filter_data.assign(date_time=date_time)

    # drop rows which have column name as data
    # if row_index is not None:
    #     filter_data = filter_data.drop(labels=row_index, axis=0)

    # convert string to float64 values
    data[['Temperature', 'Humidity']] = data[['Temperature', 'Humidity']].astype('float64')
    if 'Heat Index' in data.columns:
        data = data.drop('Heat Index', axis=1)

    # pressure data
    if 'Pressure' in data.columns and 'Sea_Level_Pressure' in data.columns:
        data[['Pressure', 'Sea_Level_Pressure']] = data[['Pressure', 'Sea_Level_Pressure']].astype('float64')

    # soil moisture data
    if 'Soil_Moisture_Percentage' in data.columns and 'Soil_Moisture' in data.columns:
        data['Soil_Moisture_Percentage'] = data['Soil_Moisture_Percentage'].astype('float64')

    # data = data.assign(date_time=date_time)
    # data = data.assign(time_only=time_only)

    return data


def change_column_name_env(data):
    """change column names to remove trailing spaces"""

    column_names = data.columns.values.tolist()
    new_column_names = [i_name.strip() for i_name in column_names]

    column_name_dict = {i_key: i_value for i_key, i_value in zip(column_names, new_column_names)}
    df = data.rename(columns=column_name_dict)

    return df
