import datetime
import pandas as pd
from shapely.geometry import Point
import seis_utils
from seis_settings import EPSG_PSD93
from seis_database import DbUtils


class QuantumDb:
    """database method for Inova Quantum nodes"""

    table_rcvr_points = "rcvr_points"
    table_node_files = "node_quantum_files"
    table_node_attributes = "node_quantum_attributes"
    table_receivers = "rcvr_points"

    @classmethod
    @DbUtils.connect
    def delete_table_rcvr_points(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_rcvr_points};"
        cursor.execute(sql_string)
        print(f"delete table {cls.table_rcvr_points}")

    @classmethod
    @DbUtils.connect
    def delete_table_node_attributes(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_node_attributes};"
        cursor.execute(sql_string)
        print(f"delete table {cls.table_node_attributes}")

    @classmethod
    @DbUtils.connect
    def delete_table_node_files(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_node_files};"
        cursor.execute(sql_string)
        print(f"delete table {cls.table_node_files}")

    @classmethod
    @DbUtils.connect
    def create_table_rcvr_points(cls, cursor):
        """create table with receiver positions"""
        sql_string = (
            f"CREATE TABLE {cls.table_rcvr_points} ("
            f"id INTEGER PRIMARY KEY, "
            f"line INTEGER NOT NULL, "
            f"rcvr_index INTEGER NOT NULL, "
            f"station INTEGER NOT NULL, "
            f"easting DOUBLE PRECISION, "
            f"northing DOUBLE PRECISION, "
            f"elevation REAL, "
            f"UNIQUE (line, station, rcvr_index) "
            f");"
        )
        cursor.executescript(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_rcvr_points}", '
            f'"geom", {EPSG_PSD93}, "POINT", "XY");'
        )
        cursor.execute(sql_string)
        print(f"create table {cls.table_rcvr_points}")

    @classmethod
    @DbUtils.connect
    def create_table_node_files(cls, cursor):
        sql_string = (
            f"CREATE TABLE {cls.table_node_files} ("
            f"id INTEGER PRIMARY KEY, "
            f"file_name VARCHAR(100), "
            f"file_date TIMESTAMP);"
        )
        cursor.executescript(sql_string)
        print(f"create table {cls.table_node_files}")

    @classmethod
    @DbUtils.connect
    def create_table_node_attributes(cls, cursor):
        """attributes table for the Inova Quantum nodes based on BITS report"""
        sql_string = (
            f"CREATE TABLE {cls.table_node_attributes} ("
            f"id INTEGER PRIMARY KEY, "
            f"id_file INTEGER REFERENCES {cls.table_node_files}(id) ON DELETE CASCADE, "
            f"id_point INTEGER REFERENCES {cls.table_rcvr_points}(id), "
            f"qtm_sn VARCHAR(10), "
            f"software VARCHAR(20), "
            f"geoph_model VARCHAR(10), "
            f"test_time TIMESTAMP, "
            f"temp REAL, "
            f"bits_type VARCHAR(15), "
            f"tilt REAL, "
            f"config_id INTEGER, "
            f"resistance REAL, "
            f"noise REAL, "
            f"thd REAL, "
            f"polarity VARCHAR(15), "
            f"frequency REAL, "
            f"damping REAL, "
            f"sensitivity REAL, "
            f"dyn_range REAL, "
            f"ein REAL, "
            f"gain REAL, "
            f"offset REAL, "
            f"gps_time INTEGER, "
            f"ext_geophone BOOLEAN);"
        )
        cursor.executescript(sql_string)
        print(f"create table {cls.table_node_attributes}")

    @classmethod
    @DbUtils.connect
    def update_rcvr_point_records(cls, rcv_records, cursor):
        progress_message = seis_utils.progress_message_generator(
            f"populate database for table: {cls.table_rcvr_points}                      "
        )

        sql_select_string = (
            f"SELECT id FROM {cls.table_rcvr_points} WHERE "
            f"line = ? AND "
            f"station = ? AND "
            f"rcvr_index = ?;"
        )
        sql_insert_string = (
            f"INSERT INTO {cls.table_rcvr_points} ("
            f"line, station, rcvr_index, easting, northing, elevation, geom) "
            f'VALUES ({", ".join(["?"]*6)}, MakePoint(?, ?, ?)); '
        )

        for rcv_record in rcv_records:
            cursor.execute(
                sql_select_string,
                (rcv_record.line, rcv_record.station, rcv_record.rcvr_index),
            )
            try:
                _ = cursor.fetchone()[0]

            except TypeError:
                point = Point(rcv_record.easting, rcv_record.northing)
                cursor.execute(
                    sql_insert_string,
                    (
                        rcv_record.line,
                        rcv_record.station,
                        rcv_record.rcvr_index,
                        rcv_record.easting,
                        rcv_record.northing,
                        rcv_record.elevation,
                        point.x,
                        point.y,
                        EPSG_PSD93,
                    ),
                )

                next(progress_message)

    @classmethod
    @DbUtils.connect
    def update_node_file(cls, node_file, cursor):
        """method to to check if file_name exists in the database, if it does not then
        add the filename to the data base
        returns:
        -1, if file is found
        n, new file_id number if no file is found
        """
        # check if file exists
        sql_string = (
            f"SELECT id FROM {cls.table_node_files} WHERE "
            f"file_name like '%{node_file.file_name}' ;"
        )
        cursor.execute(sql_string)
        try:
            _ = cursor.fetchone()[0]
            return -1

        except TypeError:
            # no id was found so go on to create one
            pass

        sql_string = (
            f"INSERT INTO {cls.table_node_files} ("
            f"file_name, file_date) "
            f"VALUES (?, ?) "
        )
        cursor.execute(sql_string, (node_file.file_name, node_file.file_date))
        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_node_attributes_records(cls, node_records, cursor):
        progress_message = seis_utils.progress_message_generator(
            f"populate database for table: {cls.table_node_attributes}                  "
        )

        # get the receiver ids and check all nodes have an rcvr_id
        sql_get_rcvr_id_string = (
            f"SELECT id FROM {cls.table_rcvr_points} WHERE "
            f"line = ? AND "
            f"station = ? AND "
            f"rcvr_index = ?;"
        )
        rcvr_ids = []
        for node_record in node_records:
            cursor.execute(
                sql_get_rcvr_id_string,
                (node_record.line, node_record.station, node_record.rcvr_index),
            )
            try:
                rcvr_ids.append(cursor.fetchone()[0])

            except TypeError:
                return (
                    f"({node_record.line}, {node_record.station}) is not a receiver point "
                    f"in the database"
                )

        sql_insert_string = (
            f"INSERT INTO {cls.table_node_attributes} ("
            f"id_file, id_point, qtm_sn, software, geoph_model, test_time, temp, "
            f"bits_type, tilt, config_id, resistance, noise, thd, polarity, "
            f"frequency, damping, sensitivity, dyn_range, ein, gain, offset, "
            f"gps_time, ext_geophone) "
            f'VALUES ({", ".join(["?"]*23)}); '
        )
        for rcvr_id, node_record in zip(rcvr_ids, node_records):
            cursor.execute(
                sql_insert_string,
                (
                    node_record.id_file,
                    rcvr_id,
                    node_record.qtm_sn,
                    node_record.software,
                    node_record.geoph_model,
                    node_record.test_time,
                    node_record.temp,
                    node_record.bits_type,
                    node_record.tilt,
                    node_record.config_id,
                    node_record.resistance,
                    node_record.noise,
                    node_record.thd,
                    node_record.polarity,
                    node_record.frequency,
                    node_record.damping,
                    node_record.sensitivity,
                    node_record.dyn_range,
                    node_record.ein,
                    node_record.gain,
                    node_record.offset,
                    node_record.gps_time,
                    node_record.ext_geophone,
                ),
            )

            next(progress_message)

    @classmethod
    @DbUtils.connect
    def delete_node_file(cls, file_id, cursor):
        sql_string = f"DELETE FROM {cls.table_node_files} WHERE id={file_id};"
        cursor.execute(sql_string)
        print(f"record {file_id} deleted from {cls.table_node_files}")

    @classmethod
    def get_node_data_by_date(cls, production_date: datetime) -> pd.DataFrame:
        """retrieve node data by date
        arguments:
          production_date: datetime object
        returns:
          pandas dataframe with node attributes for production date
        """
        engine = DbUtils().get_db_engine()
        sql_string = (
            f"SELECT node.* FROM {cls.table_node_attributes} AS node "
            f"INNER JOIN {cls.table_receivers} AS rcv ON rcv.id = node.id_point "
            f'WHERE DATE(node.test_time) = \'{production_date.strftime("%Y-%m-%d")}\' '
            f"ORDER BY rcv.line ASC, rcv.station ASC;"
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_node_data_by_node(cls, qtm_sn: str) -> pd.DataFrame:
        """retrieve node data by quantum node serial number
        arguments:
          qtm_sn: serial number of quantum node (str)
        returns:
          pandas dataframe with node attributes for qtm_sn
        """
        engine = DbUtils().get_db_engine()
        sql_string = (
            f"SELECT * FROM {cls.table_node_attributes} WHERE " f"qtm_sn = {qtm_sn};"
        )
        return pd.read_sql_query(sql_string, con=engine)
