''' module for ivms database interaction using sqlite3
'''
from functools import wraps
import datetime
import sqlite3
import numpy as np
import pandas as pd
from shapely.geometry import Point
from sqlalchemy import create_engine
import seis_utils
from ivms_settings import DATABASE, IvmsDriver


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


class IvmsDb:
    table_driver = 'ivms_driver'

    @classmethod
    @DbUtils.connect
    def delete_table_driver(cls, cursor):
        sql_string = f'DROP TABLE {cls.table_driver};'
        cursor.execute(sql_string)
        print(f'delete table {cls.table_driver}')

    @classmethod
    @DbUtils.connect
    def create_table_driver(cls, cursor):
        sql_string = (
            f'CREATE TABLE {cls.table_driver} ('
            f'id INTEGER PRIMARY KEY, '
            f'contractor VARCHAR(15), '
            f'employee_no INTEGER, '
            f'ivms_id INTEGER UNIQUE, '
            f'name VARCHAR(50), '
            f'dob TIMESTAMP, '
            f'mobile VARCHAR(12), '
            f'hse_passport VARCHAR(6), '
            f'site_name VARCHAR(30), '
            f'ROP_license VARCHAR(10) UNIQUE, '
            f'date_issue_license TIMESTAMP, '
            f'date_expiry_license TIMESTAMP, '
            f'PDO_permit VARCHAR(10),'
            f'date_expiry_permit TIMESTAMP, '
            f'vehicle_light BOOLEAN, '
            f'vehicle_heavy BOOLEAN, '
            f'date_dd01 TIMESTAMP, '
            f'date_dd02 TIMESTAMP, '
            f'date_dd03 TIMESTAMP, '
            f'date_dd04 TIMESTAMP, '
            f'date_dd05 TIMESTAMP, '
            f'date_dd06 TIMESTAMP, '
            f'date_dd06_due TIMESTAMP, '
            f'date_assessment_day TIMESTAMP, '
            f'date_assessment_night TIMESTAMP, '
            f'date_assessment_rough TIMESTAMP, '
            f'assessment_comment TEXT, '
            f'training_comment TEXT'
            f');'
        )

        cursor.execute(sql_string)
        print(f'create table {cls.table_driver}')

    @classmethod
    @DbUtils.connect
    def update_driver_records(cls, driver_records, cursor):
        ''' method to update the driver records
        '''
        progress_message = seis_utils.progress_message_generator(
            f'update database for table: {cls.table_driver}                              '
        )
        for driver_record in driver_records:
            sql_string = (
                f'SELECT id FROM {cls.table_driver} '
                f'WHERE ivms_id = {driver_record.ivms_id}'
            )
            cursor.execute(sql_string)
            try:
                # id exists, update the record
                _ = cursor.fetchone()[0]
                sql_string = (
                    f'UPDATE {cls.table_driver} SET '
                    f'contractor = ?, '
                    f'employee_no = ?, '
                    f'ivms_id = ?, '
                    f'name = ?, '
                    f'dob = ?, '
                    f'mobile = ?, '
                    f'hse_passport = ?, '
                    f'site_name = ?, '
                    f'ROP_license = ?, '
                    f'date_issue_license = ?, '
                    f'date_expiry_license = ?, '
                    f'PDO_permit = ?, '
                    f'date_expiry_permit = ?, '
                    f'vehicle_light = ?, '
                    f'vehicle_heavy = ?, '
                    f'date_dd01 = ?, '
                    f'date_dd02 = ?, '
                    f'date_dd03 = ?, '
                    f'date_dd04 = ?, '
                    f'date_dd05 = ?, '
                    f'date_dd06 = ?, '
                    f'date_dd06_due = ?, '
                    f'date_assessment_day = ?, '
                    f'date_assessment_night = ?, '
                    f'date_assessment_rough = ?, '
                    f'assessment_comment = ?, '
                    f'training_comment = ? '
                    f'WHERE ivms_id = {driver_record.ivms_id}'
                )

            except TypeError:
                # no id was found, create a record
                sql_string = (
                    f'INSERT INTO {cls.table_driver} ('
                    f'contractor, employee_no, ivms_id, name, dob, mobile, hse_passport, '
                    f'site_name, ROP_license, date_issue_license, date_expiry_license, '
                    f'PDO_permit, date_expiry_permit, vehicle_light, vehicle_heavy, '
                    f'date_dd01, date_dd02, date_dd03, date_dd04, date_dd05, date_dd06, '
                    f'date_dd06_due, date_assessment_day, date_assessment_night, '
                    f'date_assessment_rough, assessment_comment, training_comment'
                    f') VALUES ({", ".join(["?"]*27)})'
                )

            cursor.execute(sql_string, (
                driver_record.contractor, driver_record.employee_no,
                driver_record.ivms_id, driver_record.name, driver_record.dob,
                driver_record.mobile, driver_record.hse_passport, driver_record.site_name,
                driver_record.ROP_license, driver_record.date_issue_license,
                driver_record.date_expiry_license, driver_record.PDO_permit,
                driver_record.date_expiry_permit, driver_record.vehicle_light,
                driver_record.vehicle_heavy, driver_record.date_dd01,
                driver_record.date_dd02, driver_record.date_dd03, driver_record.date_dd04,
                driver_record.date_dd05, driver_record.date_dd06, driver_record.date_dd06_due,
                driver_record.date_assessment_day, driver_record.date_assessment_night,
                driver_record.date_assessment_rough, driver_record.assessment_comment,
                driver_record.training_comment,
            ))
            next(progress_message)

    @classmethod
    def fetch_driver_records(cls):
        engine = DbUtils.get_db_engine()
        sql_string = (
            f'SELECT * FROM {cls.table_driver}'
            )
        driver_records_df = pd.read_sql_query(sql_string, con=engine)

        driver_records = []
        for _, row in driver_records_df.iterrows():
            driver_record = IvmsDriver()
            driver_record.contractor = row['contractor']
            driver_record.employee_no = row['employee_no']
            driver_record.ivms_id = row['ivms_id']
            driver_record.name = row['name']
            driver_record.dob = row['dob']
            driver_record.mobile = row['mobile']
            driver_record.hse_passport = row['hse_passport']
            driver_record.site_name = row['site_name']
            driver_record.ROP_license = row['ROP_license']
            driver_record.date_issue_license = row['date_issue_license']
            driver_record.date_expiry_license = row['date_expiry_license']
            driver_record.PDO_permit = row['PDO_permit']
            driver_record.date_expiry_permit = row['date_expiry_permit']
            driver_record.vehicle_light = row['vehicle_light']
            driver_record.vehicle_heavy = row['vehicle_heavy']
            driver_record.date_dd01 = row['date_dd01']
            driver_record.date_dd02 = row['date_dd02']
            driver_record.date_dd03 = row['date_dd03']
            driver_record.date_dd04 = row['date_dd04']
            driver_record.date_dd05 = row['date_dd05']
            driver_record.date_dd06 = row['date_dd06']
            driver_record.date_dd06_due = row['date_dd06_due']
            driver_record.date_assessment_day = row['date_assessment_day']
            driver_record.date_assessment_night = row['date_assessment_night']
            driver_record.date_assessment_rough = row['date_assessment_rough']
            driver_record.assessment_comment = row['assessment_comment']

            driver_records.append(driver_record)


        return driver_records