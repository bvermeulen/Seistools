''' module for seistools database interaction using sqlite3
'''
from functools import wraps
import sqlite3
from sqlalchemy import create_engine
from seis_settings import DATABASE


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


    @classmethod
    def create_database(cls):
        connection = None
        try:
            connection = sqlite3.connect(cls.database)
            connection.enable_load_extension(True)
            connection.execute('SELECT load_extension("mod_spatialite")')
            connection.execute('SELECT InitSpatialMetaData(1);')

        except sqlite3.Error as error:
            print(f'error while connect to sqlite {cls.database}: '
                  f'{error}')

        finally:
            if connection:
                connection.close()


