''' module to update vaps files in the database
'''
import datetime
import io
import json
import os
from functools import wraps
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from recordtype import recordtype
from decouple import config

DATA_FILES_VAPS = "D:\\OneDrive\\Work\\PDO\\vp_data\\1 VAPS files\\"
DATA_FILES_VP = "D:\\OneDrive\\Work\\PDO\\vp_data\\1 VP Report\\"
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

        progress_message = progress_message_generator(
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
    def get_vaps_data_by_date(cls, production_date):
        engine = DbUtils().get_engine()
        sql_string = (f'SELECT * FROM {cls.table_vaps} WHERE '
                      f'DATE(time_break) = \'{production_date.strftime("%Y-%m-%d")}\'')
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


class Vaps:

    vaps_base_folder = DATA_FILES_VAPS
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
                        if  vaps_record.line:
                            vaps_record.file_id = file_id
                            vaps_records.append(vaps_record)

                        next(progress_message)

                cls.vp_db.update_vaps(vaps_records)
                print()

    @classmethod
    def parse_vaps_line(cls, vaps_line):
        vaps_record = VapsTable(*[None]*22)

        try:
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

        except ValueError:
            vaps_record = VapsTable(*[None]*22)

        return vaps_record

class Vp:

    vp_base_folder = DATA_FILES_VP
    vp_db = VpDb()

    @classmethod
    def read_vp(cls):
        for foldername, _, filenames in os.walk(cls.vp_base_folder):
            for filename in filenames:
                if filename[-4:] not in ['.txt', '.TXT']:
                    continue

                vp_file = FilesVpTable(*[None]*3)

                abs_filename = os.path.abspath(os.path.join(foldername, filename))
                vp_file.file_name = abs_filename
                vp_file.file_date = (
                    datetime.datetime.fromtimestamp(os.stat(abs_filename).st_mtime))

                file_id = cls.vp_db.update_vp_file(vp_file)

                if file_id == -1:
                    continue

                progress_message = progress_message_generator(
                    f'reading vp from {vp_file.file_name}   ')

                vp_records = []
                with open(abs_filename, mode='rt') as vp:
                    for vp_line in vp.readlines():
                        if vp_line[0:9].strip() == 'Line':
                            continue

                        vp_record = cls.parse_vp_line(vp_line)
                        if vp_record.line:
                            vp_record.file_id = file_id
                            vp_records.append(vp_record)

                        next(progress_message)

                cls.vp_db.update_vp(vp_records)
                print()

    @classmethod
    def parse_vp_line(cls, vp_line):
        vp_record = VpTable(*[None]*20)

        try:
            # create time break date
            time_break = (datetime.datetime.strptime(datetime.datetime.strptime(
                vp_line[32:51], '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%y %H:%M:%S') +  \
                    '.' + vp_line[52:55] + '000', '%d-%m-%y %H:%M:%S.%f'))

            vp_record.line = int(vp_line[0:9])
            vp_record.station = int(vp_line[9:19])
            vp_record.vibrator = int(vp_line[19:29].strip()[4:5])
            vp_record.time_break = time_break
            vp_record.planned_easting = float(vp_line[64:79])
            vp_record.planned_northing = float(vp_line[79:94])
            vp_record.easting = float(vp_line[109:124])
            vp_record.northing = float(vp_line[124:139])
            vp_record.elevation = float(vp_line[139:154])
            vp_record.offset = float(vp_line[154:166])
            vp_record.peak_force = int(vp_line[166:178])
            vp_record.avg_force = int(vp_line[178:190])
            vp_record.peak_dist = int(vp_line[190:202])
            vp_record.avg_dist = int(vp_line[202:214])
            vp_record.peak_phase = int(vp_line[214:226])
            vp_record.avg_phase = int(vp_line[226:238])
            vp_record.qc_flag = vp_line[238:248].strip()

        except ValueError:
            vp_record = VpTable(*[None]*20)

        return vp_record


if __name__ == '__main__':
    vp_db = VpDb()
    vp_db.create_table_vaps_files()
    vp_db.create_table_vaps()
    vp_db.create_table_vp_files()
    vp_db.create_table_vp()

    vaps = Vaps()
    vaps.read_vaps()

    vp = Vp()
    vp.read_vp()
