import datetime
import pandas as pd
import seis_utils
from seis_database import DbUtils


class NuseisDb:
    '''  database method for GTI NuSeis nodes
    '''
    table_rcvr_points = 'rcvr_points'
    table_node_files = 'nuseis_files'
    table_node_attributes = 'nuseis_attributes'

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
        ''' attributes table for the Inova Quantum nodes based on BITS report
        '''
        sql_string = (
            f'CREATE TABLE {cls.table_node_attributes} ('
            f'id INTEGER PRIMARY KEY, '
            f'id_file INTEGER REFERENCES {cls.table_node_files}(id) ON DELETE CASCADE, '
            f'id_point INTEGER REFERENCES {cls.table_rcvr_points}(id), '
            f'nuseis_sn INTEGER, '
            f'tilt REAL, '
            f'noise REAL, '
            f'resistance REAL, '
            f'impedance REAL, '
            f'thd REAL, '
            f'test_time TIME_STAMP);'
        )
        cursor.executescript(sql_string)
        print(f'create table {cls.table_node_attributes}')

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
            f'file_name like \'%{node_file.file_name}\' ;'
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
                    f'({node_record.line}, {node_record.station}) is not a receiver '
                    f'point in the database'
                )

        sql_insert_string = (
            f'INSERT INTO {cls.table_node_attributes} ('
            f'id_file, id_point, nuseis_sn, tilt, noise, resistance, '
            f'impedance, thd, test_time) '
            f'VALUES ({", ".join(["?"]*9)}); '
        )
        for rcvr_id, node_record in zip(rcvr_ids, node_records):
            cursor.execute(sql_insert_string, (
                node_record.id_file,
                rcvr_id,
                node_record.nuseis_sn,
                node_record.tilt,
                node_record.noise,
                node_record.resistance,
                node_record.impedance,
                node_record.thd,
                node_record.test_time,
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
    def get_node_data_by_date(cls, production_date: datetime) -> pd.DataFrame:
        ''' retrieve node data by date
            arguments:
              production_date: datetime object
            returns:
              pandas dataframe with node attributes for production date
        '''
        engine = DbUtils().get_db_engine()
        sql_string = (f'SELECT * FROM {cls.table_node_attributes} WHERE '
                      f'DATE(test_time) = \'{production_date.strftime("%Y-%m-%d")}\';')
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
