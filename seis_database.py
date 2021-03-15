''' module for seistools database interaction using sqlite3
'''
from functools import wraps
import datetime
import sqlite3
import numpy as np
import pandas as pd
from shapely.geometry import Point
from sqlalchemy import create_engine
import seis_utils
from seis_settings import (
    DATABASE, INIT_DB, FLEETS, SWEEP_TIME, PAD_DOWN_TIME, DENSE_CRITERIUM, EPSG_PSD93
)


class DbUtils:
    '''  utility methods for database
    '''
    database = DATABASE

    @classmethod
    def connect(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            try:
                connection = sqlite3.connect(cls.database)
                connection.enable_load_extension(True)
                connection.execute('SELECT load_extension("mod_spatialite")')
                if INIT_DB:
                    connection.execute('SELECT InitSpatialMetaData(1);')
                cursor = connection.cursor()
                result = func(*args, cursor, **kwargs)
                connection.commit()

            except sqlite3.Error as error:
                print(f'error while connect to sqlite {cls.database}: '
                      f'{error}')

            finally:
                if connection:
                    cursor.close()
                    connection.close()

            return result

        return wrapper

    @classmethod
    def get_db_engine(cls):
        return create_engine(f'sqlite:///{cls.database}')


class VpDb:
    table_vp_files = 'vp_files'
    table_vp = 'vp_records'
    table_vaps_files = 'vaps_files'
    table_vaps = 'vaps_records'

    @classmethod
    @DbUtils.connect
    def delete_table_vp(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_vp};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vp}')

    @classmethod
    @DbUtils.connect
    def delete_table_vp_files(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_vp_files};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vp_files}')

    @classmethod
    @DbUtils.connect
    def delete_table_vaps(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_vaps};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vaps}')

    @classmethod
    @DbUtils.connect
    def delete_table_vaps_files(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_vaps_files};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_vaps_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vp_files(cls, cursor):
        sql_string = (
            f'CREATE TABLE {cls.table_vp_files} ('
            f'id INTEGER PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP);'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vp_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vp(cls, cursor):
        # first create the table
        sql_string = (
            f'CREATE TABLE {cls.table_vp} ('
            f'id INTEGER PRIMARY KEY, '
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
            f'dense_flag BOOLEAN);'
        )
        cursor.executescript(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_vp}", '
            f'"geom", {EPSG_PSD93}, "POINT", "XY");'
        )
        cursor.execute(sql_string)

        print(f'create table {cls.table_vp}')

    @classmethod
    @DbUtils.connect
    def create_table_vaps_files(cls, cursor):
        sql_string = (
            f'CREATE TABLE {cls.table_vaps_files} ('
            f'id INTEGER PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP);'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_vaps_files}')

    @classmethod
    @DbUtils.connect
    def create_table_vaps(cls, cursor):
        sql_string = (
            f'CREATE TABLE {cls.table_vaps} ('
            f'id INTEGER PRIMARY KEY, '
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
            f'distance REAL, '
            f'time REAL, '
            f'velocity REAL, '
            f'dense_flag BOOLEAN); '
        )
        cursor.executescript(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_vaps}", '
            f'"geom", {EPSG_PSD93}, "POINT", "XY");'
        )
        cursor.execute(sql_string)

        print(f'create table {cls.table_vaps}')

    @classmethod
    @DbUtils.connect
    def update_vp_file(cls, vp_file, cursor):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_vp_files} WHERE '
            f'file_name=\'{vp_file.file_name}\' ;'
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
            f'VALUES (?, ?); '
        )
        cursor.execute(sql_string, (vp_file.file_name, vp_file.file_date))

        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_vp(cls, vp_records, cursor, link_vaps=False):
        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_vp}                   ')


        sql_vp_record = (
            f'INSERT INTO {cls.table_vp} ('
            f'file_id, vaps_id, line, station, vibrator, time_break, '
            f'planned_easting, planned_northing, easting, northing, elevation, _offset, '
            f'peak_force, avg_force, peak_dist, avg_dist, peak_phase, avg_phase, '
            f'qc_flag, geom) VALUES ({", ".join(["?"*19])}, MakePoint(?, ?, ?));'
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
                point.x, point.y, EPSG_PSD93
                ))

            next(progress_message)

    @classmethod
    @DbUtils.connect
    def update_vaps_file(cls, vaps_file, cursor):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_vaps_files} WHERE '
            f'file_name=\'{vaps_file.file_name}\' ;'
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
            f'VALUES (?, ?); '
        )

        cursor.execute(sql_string, (vaps_file.file_name, vaps_file.file_date))

        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_vaps(cls, vaps_records, cursor):
        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_vaps}                             ')

        sql_string = (
            f'INSERT INTO {cls.table_vaps} ('
            f'file_id, line, point, fleet_nr, vibrator, drive, '
            f'avg_phase, peak_phase, avg_dist, peak_dist, avg_force, peak_force, '
            f'avg_stiffness, avg_viscosity, easting, northing, elevation, '
            f'time_break, hdop, tb_date, positioning, geom) '
            f'VALUES ({", ".join(["?"]*21)}, MakePoint(?, ?, ?));'
        )

        for vaps_record in vaps_records:
            point = Point(vaps_record.easting, vaps_record.northing)

            cursor.execute(sql_string, (
                vaps_record.file_id,
                vaps_record.line,
                vaps_record.station,
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
                point.x, point.y, EPSG_PSD93
                ))

            next(progress_message)
    @classmethod

    @DbUtils.connect
    def update_vp_distance(cls, database_table, prod_date, cursor):
        ''' Add values for distance, time, velocity, denseflag to the database_table
            This can only be done after all vps have been added to the database
            as only then it be sorted by consecutive vp points by vibrator
            arguments:
                database_table: either 'VAPS' or 'VP'
                state_date: datetime.date object start date
                end_date: datetime.date object end date
        '''
        if database_table == 'VAPS':
            table = cls.table_vaps

        else:
            table = cls.table_vp

        sql_string = (
            f'UPDATE {table} '
            f'SET'
            f'    distance = ?, '
            f'    time = ?, '
            f'    velocity = ?, '
            f'    dense_flag = ? '
            f'WHERE id = ?;'
        )

        progress_message = seis_utils.progress_message_generator(
            f'add dist, time, vel, dense_flag to {table} for '
            f'{prod_date.strftime("%d-%m-%Y")}                          ')

        vp_records_df = cls.get_vp_data_by_date(database_table, prod_date)

        for vib in range(1, FLEETS):
            vib_df = vp_records_df[vp_records_df['vibrator'] == vib]
            vp_pts = [
                (val[0], Point(val[1], val[2]), val[3]) for val in zip(
                    vib_df['id'].to_list(),
                    vib_df['easting'].to_list(),
                    vib_df['northing'].to_list(),
                    vib_df['time_break'].to_list(),
                )
            ]

            # use consecutive vp's
            for vp_a, vp_b in zip(vp_pts, vp_pts[1:]):
                index = vp_a[0]
                dx = vp_b[1].x - vp_a[1].x
                dy = vp_b[1].y - vp_a[1].y
                dist = np.sqrt(dx*dx + dy*dy)
                try:
                    t2 = datetime.datetime.strptime(
                        vp_b[2], '%Y-%m-%d %H:%M:%S.%f')

                except ValueError:
                    t2 = datetime.datetime.strptime(
                        vp_b[2], '%Y-%m-%d %H:%M:%S')

                try:
                    t1 = datetime.datetime.strptime(
                        vp_a[2], '%Y-%m-%d %H:%M:%S.%f')

                except ValueError:
                    t1 = datetime.datetime.strptime(
                        vp_a[2], '%Y-%m-%d %H:%M:%S')

                time = max(0, ((t2 - t1).seconds - SWEEP_TIME - PAD_DOWN_TIME))

                velocity = dist / time if time > 0 else 0
                dense_flag = True if dist < DENSE_CRITERIUM else False

                cursor.execute(sql_string, (
                    dist,
                    time,
                    velocity,
                    dense_flag,
                    index,
                ))

                next(progress_message)

            # handle data for last element if there is one
            if vp_pts:
                index = vp_pts[-1][0]
                cursor.execute(sql_string, (
                    np.nan,
                    np.nan,
                    np.nan,
                    dense_flag,
                    index,
                ))

    @classmethod
    @DbUtils.connect
    def get_vaps_id(cls, vp_record, cursor):
        ''' get vaps_id from the database and insert into vp_record
            arguments:
                vp_record: VpTable recordtype
            returns:
                VpTable recordtype
        '''
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
    def get_vp_data_by_time(cls, database_table, start_time, end_time):
        ''' retrieve vp data by time interval
            arguments:
              start_time: datetime object
              end_time: datetime object
            returns:
              pandas dataframe with all database attributes
        '''
        assert end_time >= start_time, "end time must be greater equal than start time"
        if database_table == 'VAPS':
            table = cls.table_vaps

        else:
            table = cls.table_vp

        engine = DbUtils().get_db_engine()
        sql_string = (
            f'SELECT * FROM {table} WHERE '
            f'time_break BETWEEN \'{start_time}\' AND \'{end_time}\' '
            f'ORDER BY time_break;'
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_vp_data_by_date(cls, database_table, production_date):
        ''' retrieve vp data by date
            arguments:
              database_table: 'VAPS' or 'VP'
              production_date: datetime object
            returns:
              pandas dataframe with vp attributes for production_date
        '''
        if database_table == 'VAPS':
            table = cls.table_vaps

        else:
            table = cls.table_vp

        engine = DbUtils().get_db_engine()
        sql_string = (f'SELECT * FROM {table} WHERE '
                      f'DATE(time_break) = \'{production_date.strftime("%Y-%m-%d")}\';')
        vp_df = pd.read_sql_query(sql_string, con=engine)
        return vp_df

    @classmethod
    def get_vp_data_by_line(cls, database_table, line):
        ''' retrieve vp data by line number
            arguments:
              line: integer
            returns:
              pandas dataframe with all database attributes
        '''
        if database_table == 'VAPS':
            table = cls.table_vaps

        else:
            table = cls.table_vp

        engine = DbUtils().get_db_engine()
        sql_string = (
            f'SELECT * FROM {table} WHERE '
            f'line = {line} ORDER BY station;'
        )
        return pd.read_sql_query(sql_string, con=engine)


class RcvDb:
    table_rcvr_points = 'rcvr_points'
    table_node_files = 'node_files'
    table_node_attributes = 'node_attributes'

    @classmethod
    @DbUtils.connect
    def delete_table_rcvr_points(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_rcvr_points};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_rcvr_points}')

    @classmethod
    @DbUtils.connect
    def delete_table_node_attributes(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_node_attributes};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_node_attributes}')

    @classmethod
    @DbUtils.connect
    def delete_table_node_files(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_node_files};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_node_files}')

    @classmethod
    @DbUtils.connect
    def create_table_rcvr_points(cls, cursor):
        ''' create table with receiver positions
        '''
        sql_string = (
            f'CREATE TABLE {cls.table_rcvr_points} ('
            f'id INTEGER PRIMARY KEY, '
            f'line INTEGER NOT NULL, '
            f'rcvr_index INTEGER NOT NULL, '
            f'station INTEGER NOT NULL, '
            f'easting DOUBLE PRECISION, '
            f'northing DOUBLE PRECISION, '
            f'elevation REAL, '
            f'UNIQUE (line, station, rcvr_index) '
            f');'
        )
        cursor.executescript(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_rcvr_points}", '
            f'"geom", {EPSG_PSD93}, "POINT", "XY");'
        )
        cursor.execute(sql_string)
        print(f'create table {cls.table_rcvr_points}')

    @classmethod
    @DbUtils.connect
    def create_table_node_files(cls, cursor):
        sql_string = (
            f'CREATE TABLE {cls.table_node_files} ('
            f'id INTEGER PRIMARY KEY, '
            f'file_name VARCHAR(100), '
            f'file_date TIMESTAMP);'
        )
        cursor.executescript(sql_string)
        print(f'create table {cls.table_node_files}')

    @classmethod
    @DbUtils.connect
    def create_table_node_attributes(cls, cursor):
        ''' attributes table for the Inova Quantum nodes
            based on the IX1 analog test report (Feb-2021)
        '''
        sql_string = (
            f'CREATE TABLE {cls.table_node_attributes} ('
            f'id INTEGER PRIMARY KEY, '
            f'id_file INTEGER REFERENCES {cls.table_node_files}(id) ON DELETE CASCADE, '
            f'id_point INTEGER REFERENCES {cls.table_rcvr_points}(id), '
            f'qtm_sn VARCHAR(8), '
            f'battery REAL, '
            f'ch INTEGER, '
            f'type VARCHAR(15), '
            f'noise REAL, '
            f'frequency REAL, '
            f'damping REAL, '
            f'sensitivity REAL, '
            f'resistance REAL, '
            f'leakage REAL, '
            f'thd REAL, '
            f'crossfeed REAL, '
            f'power REAL, '
            f'cmr REAL, '
            f'tilt REAL, '
            f'acqrate REAL, '
            f'time_stamp TIMESTAMP);'
        )
        cursor.executescript(sql_string)
        print(f'create table {cls.table_node_attributes}')

    @classmethod
    @DbUtils.connect
    def update_rcvr_point_records(cls, rcv_records, cursor):
        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_rcvr_points}                      ')

        sql_select_string = (
            f'SELECT id FROM {cls.table_rcvr_points} WHERE '
            f'line = ? AND '
            f'station = ? AND '
            f'rcvr_index = ?;'
        )
        sql_insert_string = (
            f'INSERT INTO {cls.table_rcvr_points} ('
            f'line, station, rcvr_index, easting, northing, elevation, geom) '
            f'VALUES ({", ".join(["?"]*6)}, MakePoint(?, ?, ?)); '
        )

        for rcv_record in rcv_records:
            cursor.execute(sql_select_string, (
                rcv_record.line,
                rcv_record.station,
                rcv_record.rcvr_index
            ))
            try:
                _ = cursor.fetchone()[0]

            except TypeError:
                point = Point(rcv_record.easting, rcv_record.northing)
                cursor.execute(sql_insert_string, (
                    rcv_record.line,
                    rcv_record.station,
                    rcv_record.rcvr_index,
                    rcv_record.easting,
                    rcv_record.northing,
                    rcv_record.elevation,
                    point.x, point.y, EPSG_PSD93
                ))

                next(progress_message)

    @classmethod
    @DbUtils.connect
    def update_node_file(cls, node_file, cursor):
        ''' method to to check if file_name exists in the database, if it does not then
            add the filename to the data base
            returns:
            -1, if file is found
            n, new file_id number if no file is found
        '''
        # check if file exists
        sql_string = (
            f'SELECT id FROM {cls.table_node_files} WHERE '
            f'file_name=\'{node_file.file_name}\' ;'
        )
        cursor.execute(sql_string)
        try:
            _ = cursor.fetchone()[0]
            return -1

        except TypeError:
            # no id was found so go on to create one
            pass

        sql_string = (
            f'INSERT INTO {cls.table_node_files} ('
            f'file_name, file_date) '
            f'VALUES (?, ?) '
        )
        cursor.execute(sql_string, (node_file.file_name, node_file.file_date))
        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_node_attributes_records(cls, node_records, cursor):
        progress_message = seis_utils.progress_message_generator(
            f'populate database for table: {cls.table_node_attributes}                  ')

        # get the receiver ids and check all nodes have an rcvr_id
        sql_get_rcvr_id_string = (
            f'SELECT id FROM {cls.table_rcvr_points} WHERE '
            f'line = ? AND '
            f'station = ? AND '
            f'rcvr_index = ?;'
        )

        rcvr_ids = []
        for node_record in node_records:
            cursor.execute(sql_get_rcvr_id_string, (
                node_record.line,
                node_record.station,
                node_record.rcvr_index
            ))
            try:
                rcvr_ids.append(cursor.fetchone()[0])

            except TypeError:
                return (
                    'check node file, not all records have a receiver point '
                    'in the database'
                )

        sql_insert_string = (
            f'INSERT INTO {cls.table_node_attributes} ('
            f'id_file, id_point, qtm_sn, battery, ch, type, noise, frequency, damping, '
            f'sensitivity, resistance, leakage, thd, crossfeed, power, cmr, '
            f'tilt, acqrate, time_stamp) '
            f'VALUES ({", ".join(["?"]*19)}) '
            f';'
        )
        for rcvr_id, node_record in zip(rcvr_ids, node_records):
            cursor.execute(sql_insert_string, (
                node_record.id_file,
                rcvr_id,
                node_record.qtm_sn,
                node_record.battery,
                node_record.ch,
                node_record.type,
                node_record.noise,
                node_record.frequency,
                node_record.damping,
                node_record.sensitivity,
                node_record.resistance,
                node_record.leakage,
                node_record.thd,
                node_record.crossfeed,
                node_record.power,
                node_record.cmr,
                node_record.tilt,
                node_record.acqrate,
                node_record.time_stamp,
            ))

            next(progress_message)

    @classmethod
    @DbUtils.connect
    def delete_node_file(cls, file_id, cursor):
        sql_string = (
            f'DELETE FROM {cls.table_node_files} WHERE id={file_id};'
        )
        cursor.execute(sql_string)
        print(f'record {file_id} deleted from {cls.table_node_files}')

    @classmethod
    def get_node_data_by_date(cls, production_date):
        ''' retrieve node data by date
            arguments:
              production_date: datetime object
            returns:
              pandas dataframe with node attributes for production date
        '''
        engine = DbUtils().get_db_engine()
        sql_string = (f'SELECT * FROM {cls.table_node_attributes} WHERE '
                      f'DATE(time_stamp) = \'{production_date.strftime("%Y-%m-%d")}\';')
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_node_data_by_node(cls, qtm_sn: str) -> pd.DataFrame:
        ''' retrieve node data by quantum node serial number
            arguments:
              qtm_sn: serial number of quantum node (str)
            returns:
              pandas dataframe with node attributes for qtm_sn
        '''
        engine = DbUtils().get_db_engine()
        sql_string = (f'SELECT * FROM {cls.table_node_attributes} WHERE '
                      f'qtm_sn = {qtm_sn};')
        return pd.read_sql_query(sql_string, con=engine)
