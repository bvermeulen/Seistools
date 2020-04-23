''' module for vp database interaction
'''
#    postgis:
#    ALTER TABLE public.vaps_records ADD COLUMN geom geometry(Point, 3440);
#    UPDATE public.vaps_records SET geom =
#        ST_SetSRID(ST_MakePoint(easting, northing), 3440);
# find duplicates
#SELECT *
#FROM users
#WHERE employee_id IN (SELECT employee_id
#                      FROM users
#                      GROUP BY employee_id
#                      HAVING COUNT(employee_id) > 1);
from functools import wraps
import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from shapely.geometry import Point
import psycopg2
from decouple import config
import seis_utils
from seis_settings import (DATABASE, FLEETS, SWEEP_TIME, PAD_DOWN_TIME, DENSE_CRITERIUM,
                           EPSG_PSD93)


class DbUtils:
    '''  utility methods for database
    '''
    host = 'localhost'
    db_user = 'db_tester'
    db_user_pw = config('DB_PASSWORD')
    database = DATABASE

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

        sql_string = (
            f'CREATE TABLE {cls.table_vp_files} ('
            f'id SERIAL PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP);'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vp_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vp(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = (
            f'CREATE TABLE {cls.table_vp} ('
            f'id SERIAL PRIMARY KEY, '
            f'file_id INTEGER REFERENCES {cls.table_vp_files}(id) ON DELETE CASCADE, '
            f'vaps_id INTEGER REFERENCES {cls.table_vaps}(id) ON DELETE CASCADE, '
            f'line INT, '
            f'station INTEGER, '
            f'vibrator INTEGER, '
            f'time_break TIMESTAMP, '
            f'planned_easting DOUBLE PRECISION, '
            f'planned_northing DOUBLE PRECISION, '
            f'easting DOUBLE PRECISION, '
            f'northing DOUBLE PRECISION, '
            f'elevation REAL, '
            f'_offset REAL, '
            f'peak_force INTEGER, '
            f'avg_force INTEGER, '
            f'peak_dist INTEGER, '
            f'avg_dist INTEGER, '
            f'peak_phase INTEGER, '
            f'avg_phase INTEGER, '
            f'qc_flag VARCHAR(10), '
            f'distance REAL, '
            f'time REAL, '
            f'velocity REAL, '
            f'dense_flag BOOLEAN, '
            f'geom geometry(Point, {EPSG_PSD93}) );'
        )

        cursor.execute(sql_string)

        print(f'create table {cls.table_vp}')

    @classmethod
    @DbUtils.connect
    def create_table_vaps_files(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = (
            f'CREATE TABLE {cls.table_vaps_files} ('
            f'id SERIAL PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP);'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vaps_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vaps(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = (
            f'CREATE TABLE {cls.table_vaps} ('
            f'file_id INTEGER REFERENCES {cls.table_vaps_files}(id) ON DELETE CASCADE, '
            f'line INTEGER, '
            f'point INTEGER, '
            f'fleet_nr VARCHAR(2), '
            f'vibrator INTEGER, '
            f'drive INTEGER, '
            f'avg_phase INTEGER, '
            f'peak_phase INTEGER, '
            f'avg_dist INTEGER, '
            f'peak_dist INTEGER, '
            f'avg_force INTEGER, '
            f'peak_force INTEGER, '
            f'avg_stiffness INTEGER, '
            f'avg_viscosity INTEGER, '
            f'easting DOUBLE PRECISION, '
            f'northing DOUBLE PRECISION, '
            f'elevation REAL, '
            f'time_break TIMESTAMP, '
            f'hdop REAL, '
            f'tb_date VARCHAR(30), '
            f'positioning VARCHAR(75), '
            f'tb_date VARCHAR(30), '
            f'distance REAL, '
            f'time REAL, '
            f'velocity REAL, '
            f'dense_flag BOOLEAN);'
        )

        cursor.execute(sql_string)

        cursor.execute(
            f'ALTER TABLE {cls.table_vp} ADD COLUMN geom geometry(Point, {EPSG_PSD93});')

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
    def get_vaps_id(cls, vp_record, *args):
        ''' get vaps_id from the database and insert into vp_record
            arguments:
                vp_record: VpTable recordtype
            returns:
                VpTable recordtype
        '''
        cursor = DbUtils().get_cursor(args)
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

        return vp_record

    @classmethod
    @DbUtils.connect
    def update_vp(cls, vp_records, *args, link_vaps=False):
        cursor = DbUtils().get_cursor(args)

        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_vp}                   ')


        sql_vp_record = (
            f'INSERT INTO {cls.table_vp} ('
            f'file_id, vaps_id, line, station, vibrator, time_break, '
            f'planned_easting, planned_northing, easting, northing, elevation, _offset, '
            f'peak_force, avg_force, peak_dist, avg_dist, peak_phase, avg_phase, '
            f'qc_flag, geom) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            f'%s, %s, %s, %s, %s, %s, %s, %s, %s,  ST_SetSRID(%s::geometry, %s));'
        )

        for vp_record in vp_records:
            point = Point(vp_record.easting, vp_record.northing)

            if link_vaps:
                vp_record = cls.get_vaps_id(vp_record)

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
                point.wkb_hex, EPSG_PSD93
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
    @DbUtils.connect
    def update_vaps(cls, vaps_records, *args):
        cursor = DbUtils().get_cursor(args)

        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_vaps}                             ')


        sql_string = (
            f'INSERT INTO {cls.table_vaps} ('
            f'file_id, line, point, fleet_nr, vibrator, drive, '
            f'avg_phase, peak_phase, avg_dist, peak_dist, avg_force, peak_force, '
            f'avg_stiffness, avg_viscosity, easting, northing, elevation, '
            f'time_break, hdop, tb_date, positioning, geom) '
            f'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            f'%s, %s, %s, %s, %s, %s, ST_SetSRID(%s::geometry, %s));'
        )

        for vaps_record in vaps_records:
            point = Point(vaps_record.easting, vaps_record.northing)

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
                point.wkb_hex, EPSG_PSD93
                ))

            next(progress_message)

    @classmethod
    def get_vp_data_by_time(cls, start_time, end_time):
        ''' retrieve vp data by time interval
            arguments:
              start_time: datetime object
              end_time: datetime object
            returns:
              pandas dataframe with all database attributes
        '''
        assert end_time >= start_time, "end time must be greater equal than start time"
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
                f'{cls.table_vp}.time_break BETWEEN \'{start_time}\' AND \'{end_time}\' '
            f'ORDER BY {cls.table_vp}.time_break;'
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_data_by_date(cls, database_table, production_date):
        ''' retrieve vp data by date
            arguments:
              database_table: 'VAPS' or 'VP'
              production_date: datetime object
            returns:
              pandas dataframe with all database attributes
        '''
        if database_table == 'VAPS':
            table = cls.table_vaps

        else:
            table = cls.table_vp

        engine = DbUtils().get_engine()
        sql_string = (f'SELECT * FROM {table} WHERE '
                      f'DATE(time_break) = \'{production_date.strftime("%Y-%m-%d")}\'')
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_vp_data_by_line(cls, line):
        ''' retrieve vp data by line number
            arguments:
              line: integer
            returns:
              pandas dataframe with all database attributes
        '''
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
    def patch_add_distance_column(cls, database_table, start_date, end_date, *args):
        ''' patch to add column distance to vaps table
            arguments:
              database_table: 'VAPS' or 'VP'
              state_date: datetime.date object start date
              end_date: datetime.date object end date
        '''
        cursor = DbUtils().get_cursor(args)

        if database_table == 'VAPS':
            table = cls.table_vaps

        else:
            table = cls.table_vp

        sql_string = (
            f'UPDATE {table} '
            f'SET'
            f'    distance = %s, '
            f'    time = %s, '
            f'    velocity = %s, '
            f'    dense_flag = %s '
            f'WHERE id = %s;'
        )

        _date = start_date

        while _date <= end_date:
            progress_message = seis_utils.progress_message_generator(
                f'add dist, time, vel, dense_flag to {table} for '
                f'{_date.strftime("%d-%m-%Y")}                          ')

            vp_records_df = cls.get_data_by_date(database_table, _date)

            for vib in range(1, FLEETS):
                vib_df = vp_records_df[vp_records_df['vibrator'] == vib]

                vp_pts = [(id_xy[0], Point(id_xy[1], id_xy[2]), id_xy[3]) for id_xy in zip(  #pylint: disable=line-too-long
                    vib_df['id'].to_list(),
                    vib_df['easting'].to_list(),
                    vib_df['northing'].to_list(),
                    vib_df['time_break'].to_list(),
                )]

                dense_flag_1 = False

                for i in range(len(vp_pts) - 1):
                    index = vp_pts[i][0]
                    dx = vp_pts[i + 1][1].x - vp_pts[i][1].x
                    dy = vp_pts[i + 1][1].y - vp_pts[i][1].y
                    dist = np.sqrt(dx*dx + dy*dy)
                    time = max(0, (
                        vp_pts[i + 1][2] - vp_pts[i][2]).seconds -
                               SWEEP_TIME - PAD_DOWN_TIME)

                    try:
                        velocity = dist / time

                    except ZeroDivisionError:
                        velocity = 0

                    if dist < DENSE_CRITERIUM or dense_flag_1:
                        dense_flag = True

                    else:
                        dense_flag = False

                    cursor.execute(sql_string, (
                        dist,
                        time,
                        velocity,
                        dense_flag,
                        index,
                    ))

                    if dist < DENSE_CRITERIUM:
                        dense_flag_1 = True

                    else:
                        dense_flag_1 = False

                    next(progress_message)

                # handle data for last element if there is one
                if vp_pts:
                    index = vp_pts[-1][0]
                    cursor.execute(sql_string, (
                        np.nan,
                        np.nan,
                        np.nan,
                        dense_flag_1,
                        index,
                    ))

            _date += datetime.timedelta(days=+1)


class RcvDb:
    table_files = 'rcv_files'
    table_points = 'rcv_points'
    table_attributes = 'rcv_attributes'

    @classmethod
    @DbUtils.connect
    def delete_table_records(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = f'DROP TABLE {cls.table_attributes} CASCADE;'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_attributes}')

        sql_string = f'DROP TABLE {cls.table_points} CASCADE;'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_points}')

    @classmethod
    @DbUtils.connect
    def delete_table_files(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = f'DROP TABLE {cls.table_files} CASCADE;'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_files}')

    @classmethod
    @DbUtils.connect
    def create_table_files(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = (
            f'CREATE TABLE {cls.table_files} ('
            f'id SERIAL PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP);'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_files}')

    @classmethod
    @DbUtils.connect
    def create_table_records(cls, *args):
        cursor = DbUtils().get_cursor(args)

        sql_string = (
            f'CREATE TABLE {cls.table_points} ('
            f'line INT NOT NULL, '
            f'station INT NOT NULL, '
            f'easting DOUBLE PRECISION, '
            f'northing DOUBLE PRECISION, '
            f'elevation REAL, '
            f'geom geometry(Point, {EPSG_PSD93}) UNIQUE, '
            f'PRIMARY KEY (line, station) '
            f');'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_points}')

        sql_string = (
            f'CREATE TABLE {cls.table_attributes} ('
            f'id SERIAL PRIMARY KEY, '
            f'id_file INT REFERENCES {cls.table_files}(id) ON DELETE CASCADE, '
            f'fdu_sn INT, '
            f'sensor_type INTEGER, '
            f'resistance REAL, '
            f'tilt REAL, '
            f'noise REAL, '
            f'leakage REAL, '
            f'time_update TIMESTAMP, '
            f'geom geometry REFERENCES {cls.table_points}(geom) ON DELETE CASCADE '
            f');'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_attributes}')

    @classmethod
    @DbUtils.connect
    def update_rcv_file(cls, rcv_file, *args):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        cursor = DbUtils().get_cursor(args)

        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_files} WHERE '
            f'file_name=\'{rcv_file.file_name}\' AND '
            f'file_date=\'{rcv_file.file_date}\';'
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
            f'INSERT INTO {cls.table_files} ('
            f'file_name, file_date) '
            f'VALUES (%s, %s) '
            f'RETURNING id;'
        )

        cursor.execute(sql_string, (rcv_file.file_name, rcv_file.file_date))
        return cursor.fetchone()[0]

    @classmethod
    def create_point_record(cls, cursor, rcv_record):
        point = Point(rcv_record.easting, rcv_record.northing)

        sql_string = (
            f'SELECT geom FROM {cls.table_points} WHERE '
            f'line = {rcv_record.line} AND '
            f'station = {rcv_record.station} '
            f';'
        )
        cursor.execute(sql_string)

        try:
            geom = cursor.fetchone()[0]

        except TypeError:
            sql_string = (
                f'INSERT INTO {cls.table_points} ('
                f'line, station, easting, northing, elevation, geom) '
                f'VALUES (%s, %s, %s, %s, %s, ST_SetSRID(%s::geometry, %s)) '
                f'RETURNING geom;'
            )

            cursor.execute(sql_string, (
                rcv_record.line,
                rcv_record.station,
                rcv_record.easting,
                rcv_record.northing,
                rcv_record.elevation,
                point.wkb_hex, EPSG_PSD93
            ))

            geom = cursor.fetchone()[0]

        return geom

    @classmethod
    def create_attr_record(cls, cursor, rcv_record):
        sql_string = (
            f'INSERT INTO {cls.table_attributes} ('
            f'id_file, fdu_sn, sensor_type, resistance, tilt, '
            f'noise, leakage, time_update, geom) '
            f'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) '
            f';'
        )

        cursor.execute(sql_string, (
            rcv_record.id_file,
            rcv_record.fdu_sn,
            rcv_record.sensor_type,
            rcv_record.resistance,
            rcv_record.tilt,
            rcv_record.noise,
            rcv_record.leakage,
            rcv_record.time_update,
            rcv_record.geom
        ))

    @classmethod
    @DbUtils.connect
    def update_rcv(cls, rcv_records, *args):
        cursor = DbUtils().get_cursor(args)

        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_points}                           ')

        for rcv_record in rcv_records:

            rcv_record.geom = cls.create_point_record(cursor, rcv_record)
            cls.create_attr_record(cursor, rcv_record)

            next(progress_message)
