import datetime
import pandas as pd
import seis_utils
from seis_database import DbUtils


class WeatherDb:
    '''  database method for weather data
    '''
    table_weather_files = 'weather_files'
    table_weather_data = 'weather_data'

    @classmethod
    @DbUtils.connect
    def delete_table_weather_files(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_weather_files};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_weather_files}')

    @classmethod
    @DbUtils.connect
    def delete_table_weather_data(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_weather_data};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_weather_data}')

    @classmethod
    @DbUtils.connect
    def create_table_weather_files(cls, cursor):
        sql_string = (
            f'CREATE TABLE {cls.table_weather_files} ('
            f'id INTEGER PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP);'
        )
        cursor.executescript(sql_string)
        print(f'create table {cls.table_weather_files}')

    @classmethod
    @DbUtils.connect
    def create_table_weather_data(cls, cursor):
        ''' data table for the weather information
        '''
        sql_string = (
            f'CREATE TABLE {cls.table_weather_data} ('
            f'id INTEGER PRIMARY KEY, '
            f'file_id INTEGER REFERENCES {cls.table_weather_files}(id) ON DELETE CASCADE, '
            f'date_time TIMESTAMP, '
            f'wind_speed REAL, '
            f'wind_gust REAL, '
            f'pulse_count INTEGER, '
            f'counter_value INTEGER, '
            f'input_voltage REAL, '
            f'temperature REAL);'
        )
        cursor.executescript(sql_string)
        print(f'create table {cls.table_weather_data}')


    @classmethod
    @DbUtils.connect
    def update_weather_file(cls, weather_file, cursor):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_weather_files} WHERE '
            f'file_name like \'%{weather_file.file_name}\' ;'
        )
        cursor.execute(sql_string)
        try:
            _ = cursor.fetchone()[0]
            return -1

        except TypeError:
            # no id was found so go on to create one
            pass

        sql_string = (
            f'INSERT INTO {cls.table_weather_files} ('
            f'file_name, file_date) '
            f'VALUES (?, ?) '
        )
        cursor.execute(sql_string, (weather_file.file_name, weather_file.file_date))
        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_weather_records(cls, weather_records, cursor):
        date_ = weather_records[0].date_time.strftime('%d-%b-%Y')
        progress_message = seis_utils.progress_message_generator(
            f'{date_} populate database for table: {cls.table_weather_data}                        ')

        sql_insert_string = (
            f'INSERT INTO {cls.table_weather_data} ('
            f'file_id, date_time, wind_speed, wind_gust, pulse_count, '
            f'counter_value, input_voltage, temperature) '
            f'VALUES ({", ".join(["?"]*8)}); '
        )

        for weather_record in weather_records:

            cursor.execute(sql_insert_string, (
                weather_record.file_id,
                weather_record.date_time,
                weather_record.wind_speed,
                weather_record.wind_gust,
                weather_record.pulse_count,
                weather_record.counter_value,
                weather_record.input_voltage,
                weather_record.temperature,
            ))
            next(progress_message)

    @classmethod
    @DbUtils.connect
    def delete_weather_file(cls, file_id, cursor):
        sql_string = (
            f'DELETE FROM {cls.table_weather_files} WHERE id={file_id};'
        )
        cursor.execute(sql_string)
        print(f'record {file_id} deleted from {cls.table_node_files}')

    @classmethod
    def get_weather_data_by_dates(
        cls, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        ''' retrieve node data by date
            arguments:
              start_date: datetime object
              end_date: datetime object
            returns:
              pandas dataframe with weather data
        '''
        engine = DbUtils().get_db_engine()
        sql_string = (
            f'SELECT * FROM {cls.table_weather_data} WHERE '
            f'DATE(date_time) BETWEEN '
            f'\'{start_date.strftime("%Y-%m-%d")}\' AND '
            f'\'{end_date.strftime("%Y-%m-%d")}\' '
            f'ORDER BY date_time;'
        )
        return pd.read_sql_query(sql_string, con=engine)
