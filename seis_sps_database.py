import datetime
import numpy as np
import pandas as pd
from shapely.geometry import Point
import seis_utils
from seis_settings import EPSG_PSD93
from seis_database import DbUtils


class SpsDb:
    table_sps_files = 'sps_files'
    table_sps = 'sps_records'

    @classmethod
    def create_database(cls):
        DbUtils().create_database()

    @classmethod
    @DbUtils.connect
    def delete_table_sps(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_sps};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_sps}')

    @classmethod
    @DbUtils.connect
    def delete_table_sps_files(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_sps_files};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_sps_files}')

    @classmethod
    @DbUtils.connect
    def create_table_sps_files(cls, cursor):
        sql_string = (
            f'CREATE TABLE {cls.table_sps_files} ('
            f'id INTEGER PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP, '
            f'block_name VARCHAR(10));'
        )
        cursor.execute(sql_string)
        print(f'create table {cls.table_sps_files}')

    @classmethod
    @DbUtils.connect
    def create_table_sps(cls, cursor):
        # create the table according to SPS format
        sql_string = (
            f'CREATE TABLE {cls.table_sps} ('
            f'id INTEGER PRIMARY KEY, '
            f'file_id INTEGER REFERENCES {cls.table_sps_files}(id) ON DELETE CASCADE, '
            f'sps_type VARCHAR(1), '
            f'line INTEGER, '
            f'point INTEGER, '
            f'point_index INTEGER, '
            f'source_type VARCHAR(5),'
            f'easting DOUBLE PRECISION, '
            f'northing DOUBLE PRECISION, '
            f'elevation REAL, '
            f'dpg_filename VARCHAR(30), '
            f'time_break TIMESTAMP, '
            f'vibrator);'
        )
        cursor.executescript(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_sps}", '
            f'"geom", {EPSG_PSD93}, "POINT", "XY");'
        )
        cursor.execute(sql_string)

        print(f'create table {cls.table_sps}')

    @classmethod
    @DbUtils.connect
    def update_sps_file(cls, sps_file, cursor):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_sps_files} WHERE '
            f'file_name like \'%{sps_file.file_name}\' ;'
        )
        cursor.execute(sql_string)
        try:
            # check if id exists
            _ = cursor.fetchone()[0]
            return -1

        except TypeError:
            # no id was found so go on to create one
            pass

        sql_string = (
            f'INSERT INTO {cls.table_sps_files} ('
            f'file_name, file_date, block_name) '
            f'VALUES (?, ?, ?); '
        )
        cursor.execute(sql_string, (
            sps_file.file_name, sps_file.file_date, sps_file.block_name)
        )
        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_sps(cls, sps_records, cursor):
        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_sps}                   ')

        sql_vp_record = (
            f'INSERT INTO {cls.table_sps} ('
            f'file_id, sps_type, line, point, point_index, source_type, '
            f'easting, northing, elevation, dpg_filename, time_break, '
            f'vibrator, geom) '
            f'VALUES ({", ".join(["?"]*12)}, MakePoint(?, ?, ?));'
        )

        for sps_record in sps_records:
            point = Point(sps_record.easting, sps_record.northing)

            cursor.execute(sql_vp_record, (
                sps_record.file_id,
                sps_record.sps_type,
                sps_record.line,
                sps_record.point,
                sps_record.point_index,
                sps_record.source_type,
                sps_record.easting,
                sps_record.northing,
                sps_record.elevation,
                sps_record.dpg_filename,
                sps_record.time_break,
                sps_record.vibrator,
                point.x, point.y, EPSG_PSD93
                )
            )
            next(progress_message)

    @classmethod
    def get_sps_data_by_time(cls, start_time, end_time):
        ''' retrieve vp data by time interval
            arguments:
              start_time: datetime object
              end_time: datetime object
            returns:
              pandas dataframe with all database attributes
        '''
        assert end_time >= start_time, "end time must be greater equal than start time"

        engine = DbUtils().get_db_engine()
        sql_string = (
            f'SELECT * FROM {cls.table_sps} WHERE '
            f'time_break BETWEEN \'{start_time}\' AND \'{end_time}\' '
            f'ORDER BY time_break;'
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_sps_data_by_date(cls, production_date):
        ''' retrieve vp data by date
            arguments:
              database_table: 'VAPS' or 'VP'
              production_date: datetime object
            returns:
              pandas dataframe with vp attributes for production_date
        '''
        engine = DbUtils().get_db_engine()
        sql_string = (f'SELECT * FROM {cls.table_sps} WHERE '
                      f'DATE(time_break) = \'{production_date.strftime("%Y-%m-%d")}\';')
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_vp_data_by_line(cls, line):
        ''' retrieve vp data by line number
            arguments:
              line: integer
            returns:
              pandas dataframe with all database attributes
        '''
        engine = DbUtils().get_db_engine()
        sql_string = (
            f'SELECT * FROM {cls.table_sps} WHERE '
            f'line = {line} ORDER BY station;'
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    @DbUtils.connect
    def get_all_line_points(cls, block_name, cursor):
        ''' get all line, point of the table_sps in a pandas df
        '''
        sql_string = (
            f'CREATE VIEW line_points (line, point) '
            f'AS SELECT line, point FROM {cls.table_sps} as r '
            f'INNER JOIN {cls.table_sps_files} as f ON f.id = r.file_id '
            f'WHERE f.block_name = \"{block_name}\";'
        )
        cursor.execute(sql_string)

        engine = DbUtils().get_db_engine()
        sql_string = (
            f'SELECT line, point FROM line_points '
            f'ORDER BY line, point'
        )
        sps_df = pd.read_sql_query(sql_string, con=engine)
        lines = np.array(sps_df['line'].to_list()) * 10_000
        points = np.array(sps_df['point'].to_list())
        linepoints = np.add(lines, points)

        sql_string = (
            f'DROP VIEW IF EXISTS line_points;'
        )
        cursor.execute(sql_string)

        return linepoints