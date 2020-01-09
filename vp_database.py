''' module for vp database interaction
'''
from functools import wraps
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from decouple import config
import vp_utils
from vp_settings import FilesVpTable, VpTable, FilesVapsTable, VapsTable


class DbUtils:
    '''  utility methods for database
    '''
    host = 'localhost'
    db_user = 'db_tester'
    db_user_pw = config('DB_PASSWORD')
    database = 'vp_database'

    @classmethod
    def connect(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            connect_string = f'host=\'{cls.host}\' dbname=\'{cls.database}\''\
                             f'user=\'{cls.db_user}\' password=\'{cls.db_user_pw}\''
            result = None
            try:
                connection = psycopg2.connect(connect_string)
                cursor = connection.cursor()
                result = func(*args, cursor, **kwargs)
                connection.commit()

            except psycopg2.Error as error:
                print(f'error while connect to PostgreSQL {cls.database}: '
                      f'{error}')

            finally:
                if connection:
                    cursor.close()
                    connection.close()

            return result

        return wrapper

    @classmethod
    def get_engine(cls):
        return create_engine(
            f'postgresql+psycopg2://{cls.db_user}:{cls.db_user_pw}'
            f'@{cls.host}/{cls.database}')

    @staticmethod
    def get_cursor(cursor):
        if cursor:
            return cursor[0]

        else:
            print('unable to connect to database')
            raise()

class VpDb:
    table_vp_files = 'vp_files'
    table_vp = 'vp_records'
    table_vaps_files = 'vaps_files'
    table_vaps = 'vaps_records'

    @classmethod
    @DbUtils.connect
    def delete_table_vp(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = f'DROP TABLE {cls.table_vp};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vp}')

    @classmethod
    @DbUtils.connect
    def delete_table_vp_files(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = f'DROP TABLE {cls.table_vp_files};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vp_files}')

    @classmethod
    @DbUtils.connect
    def delete_table_vaps(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = f'DROP TABLE {cls.table_vaps};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vaps}')

    @classmethod
    @DbUtils.connect
    def delete_table_vaps_files(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = f'DROP TABLE {cls.table_vaps_files};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vp_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vp_files(cls, *args):
        cursor = DbUtils().get_cursor(args)

        files_tbl = FilesVpTable(
            id='id SERIAL PRIMARY KEY',
            file_name='file_name VARCHAR(100)',
            file_date='file_date TIMESTAMP',
        )

        sql_string = (
            f'CREATE TABLE {cls.table_vp_files} '
            f'({files_tbl.id}, '
            f'{files_tbl.file_name}, '
            f'{files_tbl.file_date});'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vp_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vp(cls, *args):
        cursor = DbUtils().get_cursor(args)

        vp_tbl = VpTable(
            id='id SERIAL PRIMARY KEY',
            file_id=f'file_id INTEGER REFERENCES {cls.table_vp_files}(id) '
                    f'ON DELETE CASCADE',
            vaps_id=f'vaps_id INTEGER REFERENCES {cls.table_vaps}(id) '
                    f'ON DELETE CASCADE',
            line='line INT',
            station='station INTEGER',
            vibrator='vibrator INTEGER',
            time_break='time_break TIMESTAMP',
            planned_easting='planned_easting DOUBLE PRECISION',
            planned_northing='planned_northing DOUBLE PRECISION',
            easting='easting DOUBLE PRECISION',
            northing='northing DOUBLE PRECISION',
            elevation='elevation REAL',
            offset='_offset REAL',
            peak_force='peak_force INTEGER',
            avg_force='avg_force INTEGER',
            peak_dist='peak_dist INTEGER',
            avg_dist='avg_dist INTEGER',
            peak_phase='peak_phase INTEGER',
            avg_phase='avg_phase INTEGER',
            qc_flag='qc_flag VARCHAR(10)'
        )

        sql_string = (
            f'CREATE TABLE {cls.table_vp} '
            f'({vp_tbl.id}, '
            f'{vp_tbl.file_id}, '
            f'{vp_tbl.vaps_id}, '
            f'{vp_tbl.line}, '
            f'{vp_tbl.station}, '
            f'{vp_tbl.vibrator}, '
            f'{vp_tbl.time_break}, '
            f'{vp_tbl.planned_easting}, '
            f'{vp_tbl.planned_northing}, '
            f'{vp_tbl.easting}, '
            f'{vp_tbl.northing}, '
            f'{vp_tbl.elevation}, '
            f'{vp_tbl.offset}, '
            f'{vp_tbl.peak_force}, '
            f'{vp_tbl.avg_force}, '
            f'{vp_tbl.peak_dist}, '
            f'{vp_tbl.avg_dist}, '
            f'{vp_tbl.peak_phase}, '
            f'{vp_tbl.avg_phase}, '
            f'{vp_tbl.qc_flag});'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vp}')

    @classmethod
    @DbUtils.connect
    def create_table_vaps_files(cls, *args):
        cursor = DbUtils().get_cursor(args)

        files_tbl = FilesVapsTable(
            id='id SERIAL PRIMARY KEY',
            file_name='file_name VARCHAR(100)',
            file_date='file_date TIMESTAMP',
        )

        sql_string = (
            f'CREATE TABLE {cls.table_vaps_files} '
            f'({files_tbl.id}, '
            f'{files_tbl.file_name}, '
            f'{files_tbl.file_date});'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vaps_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vaps(cls, *args):
        cursor = DbUtils().get_cursor(args)

        vaps_tbl = VapsTable(
            id='id SERIAL PRIMARY KEY',
            file_id=f'file_id INTEGER REFERENCES {cls.table_vaps_files}(id)'
                    f'ON DELETE CASCADE',
            line='line INTEGER',
            point='point INTEGER',
            fleet_nr='fleet_nr VARCHAR(2)',
            vibrator='vibrator INTEGER',
            drive='drive INTEGER',
            avg_phase='avg_phase INTEGER',
            peak_phase='peak_phase INTEGER',
            avg_dist='avg_dist INTEGER',
            peak_dist='peak_dist INTEGER',
            avg_force='avg_force INTEGER',
            peak_force='peak_force INTEGER',
            avg_stiffness='avg_stiffness INTEGER',
            avg_viscosity='avg_viscosity INTEGER',
            easting='easting DOUBLE PRECISION',
            northing='northing DOUBLE PRECISION',
            elevation='elevation REAL',
            time_break='time_break TIMESTAMP',
            hdop='hdop REAL',
            tb_date='tb_date VARCHAR(30)',
            positioning='positioning VARCHAR(75)'
        )

        sql_string = (
            f'CREATE TABLE {cls.table_vaps} '
            f'({vaps_tbl.id}, '
            f'{vaps_tbl.file_id}, '
            f'{vaps_tbl.line}, '
            f'{vaps_tbl.point}, '
            f'{vaps_tbl.fleet_nr}, '
            f'{vaps_tbl.vibrator}, '
            f'{vaps_tbl.drive}, '
            f'{vaps_tbl.avg_phase}, '
            f'{vaps_tbl.peak_phase}, '
            f'{vaps_tbl.avg_dist}, '
            f'{vaps_tbl.peak_dist}, '
            f'{vaps_tbl.avg_force}, '
            f'{vaps_tbl.peak_force}, '
            f'{vaps_tbl.avg_stiffness}, '
            f'{vaps_tbl.avg_viscosity}, '
            f'{vaps_tbl.easting}, '
            f'{vaps_tbl.northing}, '
            f'{vaps_tbl.elevation}, '
            f'{vaps_tbl.time_break}, '
            f'{vaps_tbl.hdop}, '
            f'{vaps_tbl.tb_date}, '
            f'{vaps_tbl.positioning});'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vaps}')

    @classmethod
    @DbUtils.connect
    def update_vp_file(cls, vp_file, *args):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        cursor = DbUtils().get_cursor(args)

        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_vp_files} WHERE '
            f'file_name=\'{vp_file.file_name}\' AND '
            f'file_date=\'{vp_file.file_date}\';'
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
            f'INSERT INTO {cls.table_vp_files} ('
            f'file_name, file_date) '
            f'VALUES (%s, %s) '
            f'RETURNING id;'
        )

        cursor.execute(sql_string, (vp_file.file_name, vp_file.file_date))

        return cursor.fetchone()[0]

    @classmethod
    @DbUtils.connect
    def update_vp(cls, vp_records, *args):
        cursor = DbUtils().get_cursor(args)

        sql_vp_record = (
            f'INSERT INTO {cls.table_vp} ('
            f'file_id, vaps_id, line, station, vibrator, time_break, '
            f'planned_easting, planned_northing, easting, northing, elevation, _offset, '
            f'peak_force, avg_force, peak_dist, avg_dist, peak_phase, avg_phase, '
            f'qc_flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            f'%s, %s, %s, %s, %s, %s, %s, %s, %s);'
        )

        sql_string = (
            f'SELECT file_name FROM {cls.table_vp_files} WHERE '
            f'id={vp_records[0].file_id};'
        )
        cursor.execute(sql_string)
        try:
            file_name = cursor.fetchone()[0]
        except TypeError:
            file_name = ''

        progress_message = vp_utils.progress_message_generator(
            f'update database vp records for file: {file_name}   ')

        for vp_record in vp_records:
            # get vaps_id for the record
            sql_string = (
                f'SELECT id FROM {cls.table_vaps} WHERE '
                f'time_break=\'{vp_record.time_break}\' AND '
                f'vibrator={vp_record.vibrator};'
            )
            cursor.execute(sql_string)
            try:
                vp_record.vaps_id = cursor.fetchone()[0]

            except TypeError:
                pass

            cursor.execute(sql_vp_record, (
                vp_record.file_id,
                vp_record.vaps_id,
                vp_record.line,
                vp_record.station,
                vp_record.vibrator,
                vp_record.time_break,
                vp_record.planned_easting,
                vp_record.planned_northing,
                vp_record.easting,
                vp_record.northing,
                vp_record.elevation,
                vp_record.offset,
                vp_record.peak_force,
                vp_record.avg_force,
                vp_record.peak_dist,
                vp_record.avg_dist,
                vp_record.peak_phase,
                vp_record.avg_phase,
                vp_record.qc_flag,
                ))

            next(progress_message)

    @classmethod
    @DbUtils.connect
    def update_vaps_file(cls, vaps_file, *args):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        cursor = DbUtils().get_cursor(args)

        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_vaps_files} WHERE '
            f'file_name=\'{vaps_file.file_name}\' AND '
            f'file_date=\'{vaps_file.file_date}\';'
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
            f'INSERT INTO {cls.table_vaps_files} ('
            f'file_name, file_date) '
            f'VALUES (%s, %s) '
            f'RETURNING id;'
        )

        cursor.execute(sql_string, (vaps_file.file_name, vaps_file.file_date))

        return cursor.fetchone()[0]

    @classmethod
    def get_vp_data_by_date(cls, production_date):
        engine = DbUtils().get_engine()
        sql_string = (f'SELECT * FROM {cls.table_vaps} WHERE '
                      f'DATE(time_break) = \'{production_date.strftime("%Y-%m-%d")}\'')
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_vp_data_by_line(cls, line):
        engine = DbUtils().get_engine()
        sql_string = (
            f'SELECT '
                f'{cls.table_vp}.line, '  #pylint: disable=bad-continuation
                f'{cls.table_vp}.station, '
                f'{cls.table_vp}.easting, '
                f'{cls.table_vp}.northing, '
                f'{cls.table_vp}.elevation, '
                f'{cls.table_vp}.time_break, '
                f'{cls.table_vaps}.avg_phase, '
                f'{cls.table_vaps}.peak_phase, '
                f'{cls.table_vaps}.avg_dist, '
                f'{cls.table_vaps}.peak_dist, '
                f'{cls.table_vaps}.avg_force, '
                f'{cls.table_vaps}.peak_force, '
                f'{cls.table_vaps}.avg_stiffness, '
                f'{cls.table_vaps}.avg_viscosity '
            f'FROM {cls.table_vp}, {cls.table_vaps} '
            f'WHERE '
                f'{cls.table_vp}.vaps_id = {cls.table_vaps}.id AND '
                f'{cls.table_vp}.line = {line} '
            f'ORDER BY {cls.table_vp}.station;'
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    @DbUtils.connect
    def update_vaps(cls, vaps_records, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = (
            f'INSERT INTO {cls.table_vaps} ('
            f'file_id, line, point, fleet_nr, vibrator, drive, '
            f'avg_phase, peak_phase, avg_dist, peak_dist, avg_force, peak_force, '
            f'avg_stiffness, avg_viscosity, easting, northing, elevation, '
            f'time_break, hdop, tb_date, positioning) '
            f'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            f'%s, %s, %s, %s, %s, %s);'
        )

        for vaps_record in vaps_records:

            cursor.execute(sql_string, (
                vaps_record.file_id,
                vaps_record.line,
                vaps_record.point,
                vaps_record.fleet_nr,
                vaps_record.vibrator,
                vaps_record.drive,
                vaps_record.avg_phase,
                vaps_record.peak_phase,
                vaps_record.avg_dist,
                vaps_record.peak_dist,
                vaps_record.avg_force,
                vaps_record.peak_force,
                vaps_record.avg_stiffness,
                vaps_record.avg_viscosity,
                vaps_record.easting,
                vaps_record.northing,
                vaps_record.elevation,
                vaps_record.time_break,
                vaps_record.hdop,
                vaps_record.tb_date,
                vaps_record.positioning,
                ))
