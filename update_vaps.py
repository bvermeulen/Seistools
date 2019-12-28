''' module to update vaps files in the database
'''
import datetime
import io
import json
import os
from functools import wraps
import numpy as np
import psycopg2
from recordtype import recordtype
from decouple import config


YEAR = '2019'

FilesVpTable = recordtype(
    'FilesVpTable',
    'id, '
    'file_name, '
    'file_date'
)

VpTable = recordtype(
    'VpTable',
    'id, '
    'file_id, '
    'vaps_id, '
    'line, '
    'station, '
    'vibrator, '
    'time_break, '
    'planned_easting, '
    'planned_northing, '
    'easting, '
    'northing, '
    'elevation, '
    'offset, '
    'peak_force, '
    'avg_force, '
    'peak_dist, '
    'avg_dist, '
    'peak_phase, '
    'avg_phase, '
    'qc_flag'
)

FilesVapsTable = recordtype(
    'FilesVapsTable',
    'id, '
    'file_name, '
    'file_date'
)

VapsTable = recordtype(
    'VapsTable',
    'id, '
    'file_id, '
    'line, '
    'point, '
    'fleet_nr, '
    'vibrator, '
    'drive, '
    'avg_phase, '
    'peak_phase, '
    'avg_dist, '
    'peak_dist, '
    'avg_force, '
    'peak_force, '
    'avg_stiffness, '
    'avg_viscosity, '
    'easting, '
    'northing, '
    'elevation, '
    'time_break, '
    'hdop, '
    'tb_date, '
    'positioning'
)

def progress_message_generator(message):
    loop_dash = ['\u2014', '\\', '|', '/']
    i = 1
    print_interval = 1
    while True:
        print(
            f'\r{loop_dash[int(i/print_interval) % 4]} {i} {message}', end='')
        i += 1
        yield


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
            planned_easting='planned_easting REAL',
            planned_northing='planned_northing REAL',
            easting='easting REAL',
            northing='northing REAL',
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
            easting='easting REAL',
            northing='northing REAL',
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
        file_id = cursor.fetchone()[0]

        return file_id

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
                vaps_record.peak_phase,
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


class Vaps:

    vaps_base_folder = ".\\"
    vp_db = VpDb()

    @classmethod
    def read_vaps(cls):
        for foldername, _, filenames in os.walk(cls.vaps_base_folder):
            for filename in filenames:
                if filename[-5:] not in ['.vaps', '.VAPS']:
                    continue

                vaps_file = FilesVapsTable(*[None]*3)

                abs_filename = os.path.abspath(os.path.join(foldername, filename))
                vaps_file.file_name = abs_filename
                vaps_file.file_date = (
                    datetime.datetime.fromtimestamp(os.stat(abs_filename).st_mtime))

                print(vaps_file)
                file_id = cls.vp_db.update_vaps_file(vaps_file)

                if file_id == -1:
                    continue

                progress_message = progress_message_generator(
                    f'reading vaps from {vaps_file.file_name}   ')

                vaps_records = []
                with open(abs_filename, mode='rt') as vaps:
                    for vaps_line in vaps.readlines():
                        if vaps_line[0] != 'A':
                            continue

                        vaps_record = cls.parse_vaps_line(vaps_line)
                        vaps_record.file_id = file_id
                        vaps_records.append(vaps_record)

                        next(progress_message)

                cls.vp_db.update_vaps(vaps_records)

    @classmethod
    def parse_vaps_line(cls, vaps_line):
        vaps_record = VapsTable(*[None]*22)

        # create time break date
        time_break = (datetime.datetime.strptime(datetime.datetime.strptime(
            YEAR + vaps_line[117:120], '%Y%j').strftime('%d-%m-%y') + ' ' +  \
                vaps_line[120:126] + '.' + vaps_line[144:147], '%d-%m-%y %H%M%S.%f'))

        vaps_record.line = int(float(vaps_line[1:17]))
        vaps_record.point = int(float(vaps_line[17:25]))
        vaps_record.fleet_nr = vaps_line[26:27]
        vaps_record.vibrator = int(vaps_line[27:29])
        vaps_record.drive = int(vaps_line[29:32])
        vaps_record.avg_phase = int(vaps_line[32:36])
        vaps_record.peak_phase = int(vaps_line[36:40])
        vaps_record.avg_dist = int(vaps_line[40:42])
        vaps_record.peak_dist = int(vaps_line[42:44])
        vaps_record.avg_force = int(vaps_line[44:46])
        vaps_record.peak_force = int(vaps_line[46:49])
        vaps_record.avg_stiffness = int(vaps_line[49:52])
        vaps_record.avg_viscosity = int(vaps_line[52:55])
        vaps_record.easting = float(vaps_line[55:64])
        vaps_record.northing = float(vaps_line[64:74])
        vaps_record.elevation = float(vaps_line[74:80])
        vaps_record.time_break = time_break
        vaps_record.hdop = float(vaps_line[126:130])
        vaps_record.tb_date = vaps_line[130:150]
        vaps_record.positioning = vaps_line[150:225]

        return vaps_record

if __name__ == '__main__':
    vp_db = VpDb()
    vp_db.create_table_vaps_files()
    vp_db.create_table_vaps()

    vaps = Vaps()
    vaps.read_vaps()
