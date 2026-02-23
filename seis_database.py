""" module for seistools database interaction using sqlite3
"""
from functools import wraps
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from seis_settings import (
    DATABASE,
    EPSG_PROJECT,
)


class DbUtils:
    """utility methods for database"""

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
                print(f"Error while connect to sqlite {cls.database}: {error}")

            finally:
                if connection:
                    cursor.close()
                    connection.close()

            return result

        return wrapper

    @classmethod
    def get_db_engine(cls):
        return create_engine(f"sqlite:///{cls.database}")

    @classmethod
    def create_database(cls):
        connection = None
        try:
            connection = sqlite3.connect(cls.database)
            connection.enable_load_extension(True)
            connection.execute('SELECT load_extension("mod_spatialite")')
            connection.execute("SELECT InitSpatialMetaData(1);")
            cursor = connection.cursor()
            cls.set_geometry_projection(cursor)
            connection.commit()

        except sqlite3.Error as error:
            print(f"error while connect to sqlite {cls.database}: " f"{error}")

        finally:
            if connection:
                connection.close()

    @classmethod
    def db_table_to_df(cls, db_table: str) -> pd.DataFrame:
        db_engine = cls.get_db_engine()
        return pd.read_sql_query(f"select * from {db_table}", con=db_engine)


    @classmethod
    def set_geometry_projection(cls, cursor) -> int:
        # create a custom project with srid 900001 if necessary
        if isinstance(EPSG_PROJECT, str):
            srid_projection = 900001
            sql_string = (
                f"INSERT INTO spatial_ref_sys "
                f"(srid, auth_name, auth_srid, proj4text) "
                f"VALUES ("
                f"{srid_projection}, "
                f"'OMV_GNAS_2D', "
                f"{srid_projection}, "
                f"'{EPSG_PROJECT}' "
                f") "
                f"ON CONFLICT DO NOTHING;"
            )
            cursor.execute(sql_string)
 
    @staticmethod
    def get_geometry_projection():
        if isinstance(EPSG_PROJECT, str):
            srid_projection = 900001
    
        else:
            srid_projection = int(EPSG_PROJECT)

        return srid_projection 