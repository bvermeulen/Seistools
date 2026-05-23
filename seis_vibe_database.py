import datetime
import numpy as np
import pandas as pd
from shapely.geometry import Point
import seis_utils
from seis_settings import (
    VIBRATORS,
    SWEEP_TIME,
    PAD_DOWN_TIME,
    DENSE_CRITERIUM,
    VpType,
    VapsTable,
    VpTable,
)
from seis_database import DbUtils


class VpDb:
    table_vp_files = "vp_files"
    table_vp = "vp_records"
    table_vaps_files = "vaps_files"
    table_vaps = "vaps_records"
    table_ep = "ep_records"
    srid_projection = DbUtils().get_geometry_projection()

    @classmethod
    @DbUtils.connect
    def delete_table_vp(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_vp};"
        cursor.execute(sql_string)
        print(f"delete table {cls.table_vp}")

    @classmethod
    @DbUtils.connect
    def delete_table_vp_files(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_vp_files};"
        cursor.execute(sql_string)
        print(f"delete table {cls.table_vp_files}")

    @classmethod
    @DbUtils.connect
    def delete_table_vaps(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_vaps};"
        cursor.execute(sql_string)

        sql_string = (
            f"delete from geometry_columns where f_table_name = '{cls.table_vaps}';"
        )
        cursor.execute(sql_string)
        print(f"delete table {cls.table_vaps}")

    @classmethod
    @DbUtils.connect
    def delete_table_vaps_files(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_vaps_files};"
        cursor.execute(sql_string)
        print(f"delete table {cls.table_vaps_files}")

    @classmethod
    @DbUtils.connect
    def delete_table_ep(cls, cursor):
        sql_string = f"DROP TABLE {cls.table_ep};"
        cursor.execute(sql_string)

        sql_string = (
            f"delete from geometry_columns where f_table_name = '{cls.table_ep}';"
        )
        cursor.execute(sql_string)
        print(f"delete table {cls.table_ep}")

    @classmethod
    @DbUtils.connect
    def create_table_vp_files(cls, cursor):
        sql_string = (
            f"CREATE TABLE {cls.table_vp_files} ("
            f"id INTEGER PRIMARY KEY, "
            f"file_name VARCHAR(100), "
            f"file_date TIMESTAMP);"
        )
        cursor.execute(sql_string)
        print(f"create table {cls.table_vp_files}")

    @classmethod
    @DbUtils.connect
    def create_table_vp(cls, cursor):

        # first create the table
        sql_string = (
            f"CREATE TABLE {cls.table_vp} ("
            f"id INTEGER PRIMARY KEY, "
            f"file_id INTEGER REFERENCES {cls.table_vp_files}(id) ON DELETE CASCADE, "
            f"vaps_id INTEGER REFERENCES {cls.table_vaps}(id) ON DELETE CASCADE, "
            f"line INT, "
            f"station INTEGER, "
            f"vibrator INTEGER, "
            f"time_break TIMESTAMP, "
            f"planned_easting DOUBLE PRECISION, "
            f"planned_northing DOUBLE PRECISION, "
            f"easting DOUBLE PRECISION, "
            f"northing DOUBLE PRECISION, "
            f"elevation REAL, "
            f"_offset REAL, "
            f"peak_force INTEGER, "
            f"avg_force INTEGER, "
            f"peak_dist INTEGER, "
            f"avg_dist INTEGER, "
            f"peak_phase INTEGER, "
            f"avg_phase INTEGER, "
            f"qc_flag VARCHAR(10), "
            f"distance REAL, "
            f"time REAL, "
            f"velocity REAL, "
            f"dense_flag BOOLEAN);"
        )
        cursor.executescript(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_vp}", '
            f'"geom", {cls.srid_projection}, "POINT", "XY");'
        )
        cursor.execute(sql_string)

        print(f"create table {cls.table_vp}")

    @classmethod
    @DbUtils.connect
    def create_table_vaps_files(cls, cursor):
        sql_string = (
            f"CREATE TABLE {cls.table_vaps_files} ("
            f"id INTEGER PRIMARY KEY, "
            f"file_name VARCHAR(100), "
            f"file_date TIMESTAMP);"
        )

        cursor.execute(sql_string)
        print(f"create table {cls.table_vaps_files}")

    @classmethod
    @DbUtils.connect
    def create_table_vaps(cls, cursor):

        sql_string = (
            f"CREATE TABLE {cls.table_vaps} ("
            f"id INTEGER PRIMARY KEY, "
            f"file_id INTEGER REFERENCES {cls.table_vaps_files}(id) ON DELETE CASCADE, "
            f"line INTEGER, "
            f"point INTEGER, "
            f"point_index INTEGER, "
            f"vibrator INTEGER, "
            f"fleet INTEGER, "
            f"drive INTEGER, "
            f"avg_phase INTEGER, "
            f"peak_phase INTEGER, "
            f"avg_dist INTEGER, "
            f"peak_dist INTEGER, "
            f"avg_force INTEGER, "
            f"peak_force INTEGER, "
            f"avg_stiffness INTEGER, "
            f"avg_viscosity INTEGER, "
            f"easting DOUBLE PRECISION, "
            f"northing DOUBLE PRECISION, "
            f"elevation REAL, "
            f"shot_nb INTEGER, "
            f"acq_nb INTEGER, "
            f"fleet_nb INTEGER, "
            f"vib_status INTEGER, "
            f"m1_warning VARCHAR(1), "
            f"m2_warning VARCHAR(1), "
            f"m3_warning VARCHAR(1), "
            f"p1_warning VARCHAR(1), "
            f"p2_warning VARCHAR(1), "
            f"p3_warning VARCHAR(1), "
            f"p4_warning VARCHAR(1), "
            f"p5_warning VARCHAR(1), "
            f"p6_warning VARCHAR(1), "
            f"force_overload VARCHAR(1), "
            f"pressure_overload VARCHAR(1), "
            f"mass_overload VARCHAR(1), "
            f"valve_overload VARCHAR(1), "
            f"excitation_overload VARCHAR(1), "
            f"stack_fold INTEGER, "
            f"compute_domain VARCHAR(1), "
            f"ve432 VARCHAR(4), "
            f"time_break TIMESTAMP, "
            f"hdop REAL, "
            f"tb_date VARCHAR(30), "
            f"distance REAL, "
            f"time REAL, "
            f"velocity REAL, "
            f"dense_flag BOOLEAN,  "
            f"gpgga VARCHAR(200) "
            f"); "
        )
        cursor.executescript(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_vaps}", '
            f'"geom", {cls.srid_projection}, "POINT", "XY");'
        )
        cursor.execute(sql_string)

        print(f"create table {cls.table_vaps}")

    @classmethod
    @DbUtils.connect
    def create_table_ep(cls, cursor):
        sql_string = (
            f"CREATE TABLE {cls.table_ep} ("
            f"id INTEGER PRIMARY KEY, "
            f"file_id INTEGER REFERENCES {cls.table_vaps_files}(id) ON DELETE CASCADE, "
            f"line INTEGER, "
            f"point INTEGER, "
            f"fleet INTEGER, "
            f"vib_count INTEGER, "
            f"vp_type VARCHAR(3), "
            f"avg_phase INTEGER, "
            f"peak_phase INTEGER, "
            f"avg_dist INTEGER, "
            f"peak_dist INTEGER, "
            f"avg_force INTEGER, "
            f"peak_force INTEGER, "
            f"avg_stiffness INTEGER, "
            f"avg_viscosity INTEGER, "
            f"easting DOUBLE PRECISION, "
            f"northing DOUBLE PRECISION, "
            f"elevation REAL, "
            f"drive INTEGER, "
            f"time_break TIMESTAMP, "
            f"tb_date VARCHAR(30), "
            f"vibs VARCHAR(20), "
            f"distance_fleet REAL, "
            f"time_fleet REAL, "
            f"velocity_fleet REAL, "
            f"dense_flag BOOLEAN "
            f"); "
        )
        cursor.execute(sql_string)

        # once table is created you can add the geomety column
        sql_string = (
            f'SELECT AddGeometryColumn("{cls.table_ep}", '
            f'"geom", {cls.srid_projection}, "POINT", "XY");'
        )
        cursor.execute(sql_string)
        print(f"create table {cls.table_ep}")

    @classmethod
    @DbUtils.connect
    def update_vp_file(cls, vp_file, cursor):
        """method to to check if file_name exists in the database, if it does not then
        add the filename to the data base
        returns:
        -1, if file is found
        n, new file_id number if no file is found
        """
        # check if file exists
        sql_string = (
            f"SELECT id FROM {cls.table_vp_files} WHERE "
            f"file_name like '%{vp_file.file_name}' ;"
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
            f"INSERT INTO {cls.table_vp_files} ("
            f"file_name, file_date) "
            f"VALUES (?, ?); "
        )
        cursor.execute(sql_string, (vp_file.file_name, vp_file.file_date))
        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_vp(cls, vp_records: VpTable, cursor: any, link_vaps=False) -> None:
        progress_message = seis_utils.progress_message_generator(
            f"populate database for table: {cls.table_vp}                   "
        )
        sql_vp_record = (
            f"INSERT INTO {cls.table_vp} ("
            f"file_id, vaps_id, line, station, vibrator, time_break, "
            f"planned_easting, planned_northing, easting, northing, elevation, _offset, "
            f"peak_force, avg_force, peak_dist, avg_dist, peak_phase, avg_phase, "
            f'qc_flag, geom) VALUES ({", ".join(["?"]*19)}, MakePoint(?, ?, ?));'
        )
        for vp_record in vp_records:
            point = Point(vp_record.easting, vp_record.northing)

            if link_vaps:
                vp_record = cls.get_vaps_id(vp_record)

            cursor.execute(
                sql_vp_record,
                (
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
                    point.x,
                    point.y,
                    cls.srid_projection,
                ),
            )
            next(progress_message)

    @classmethod
    @DbUtils.connect
    def update_vaps_file(cls, vaps_file, cursor):
        """method to to check if file_name exists in the database, if it does not then
        add the filename to the data base
        returns:
        -1, if file is found
        n, new file_id number if no file is found
        """
        # check if file exists
        sql_string = (
            f"SELECT id FROM {cls.table_vaps_files} WHERE "
            f"file_name like '%{vaps_file.file_name}' ;"
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
            f"INSERT INTO {cls.table_vaps_files} ("
            f"file_name, file_date) "
            f"VALUES (?, ?); "
        )
        cursor.execute(sql_string, (vaps_file.file_name, vaps_file.file_date))
        return cursor.lastrowid

    @classmethod
    @DbUtils.connect
    def update_vaps(cls, vaps_records: VapsTable, cursor: any) -> any:
        progress_message = seis_utils.progress_message_generator(
            f"populate database for table: {cls.table_vaps}                             "
        )
        sql_string = (
            f"INSERT INTO {cls.table_vaps} ("
            f"file_id, line, point, point_index, vibrator, fleet, drive, "
            f"avg_phase, peak_phase, avg_dist, peak_dist, avg_force, peak_force, "
            f"avg_stiffness, avg_viscosity, easting, northing, elevation, "
            f"shot_nb, acq_nb, fleet_nb, vib_status, "
            f"m1_warning, m2_warning, m3_warning, p1_warning, p2_warning, "
            f"p3_warning, p4_warning, p5_warning, p6_warning, force_overload, "
            f"pressure_overload, mass_overload, valve_overload, "
            f"excitation_overload, stack_fold, compute_domain, ve432, "
            f"time_break, hdop, tb_date, gpgga, geom) "
            f'VALUES ({", ".join(["?"]*43)}, MakePoint(?, ?, ?));'
        )
        for vaps_record in vaps_records:
            point = Point(vaps_record.easting, vaps_record.northing)
            cursor.execute(
                sql_string,
                (
                    vaps_record.file_id,
                    vaps_record.line,
                    vaps_record.point,
                    vaps_record.point_index,
                    vaps_record.vibrator,
                    vaps_record.fleet,
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
                    vaps_record.shot_nb,
                    vaps_record.acq_nb,
                    vaps_record.fleet_nb,
                    vaps_record.vib_status,
                    vaps_record.m1_warning,
                    vaps_record.m2_warning,
                    vaps_record.m3_warning,
                    vaps_record.p1_warning,
                    vaps_record.p2_warning,
                    vaps_record.p3_warning,
                    vaps_record.p4_warning,
                    vaps_record.p5_warning,
                    vaps_record.p6_warning,
                    vaps_record.force_overload,
                    vaps_record.pressure_overload,
                    vaps_record.mass_overload,
                    vaps_record.valve_overload,
                    vaps_record.excitation_overload,
                    vaps_record.stack_fold,
                    vaps_record.compute_domain,
                    vaps_record.ve432,
                    vaps_record.time_break.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    vaps_record.hdop,
                    vaps_record.tb_date,
                    vaps_record.gpgga,
                    point.x,
                    point.y,
                    cls.srid_projection,
                ),
            )
            next(progress_message)

    @classmethod
    @DbUtils.connect
    def update_ep_table_by_date(
        cls, database_table: str, prod_date: datetime.datetime, cursor: any
    ) -> None:
        progress_message = seis_utils.progress_message_generator(
            f"populate database for table: {cls.table_ep}                             "
        )

        def calc_avg(value_list: list[str]) -> float:
            val = np.mean([float(v) for v in value_list])
            return float(val)

        def convert_to_list(val_string: str) -> list[str]:
            return [v for v in val_string.split(",")]

        def elstrtolist_and_select(sweeps: list, attribute_txt: str) -> list:
            attribute_list = convert_to_list(attribute_txt)
            selected_attribute_list = []
            for sweep in sweeps:
                selected_attribute_list += attribute_list[sweep[0] : sweep[1] + 1]
            return selected_attribute_list

        def determine_vp_type(sweeps, drive):
            ep_type = "V_"
            if len(sweeps) == VpType.V1.value[0] and drive == VpType.V1.value[2]:
                ep_type = "V1"

            if len(sweeps) == VpType.V2.value[0] and drive == VpType.V2.value[2]:
                ep_type = "V2"

            if len(sweeps) == VpType.V3.value[0] and drive == VpType.V3.value[2]:
                ep_type = "V3"

            if len(sweeps) == VpType.V4.value[0] and drive == VpType.V4.value[2]:
                ep_type = "V4"

            return ep_type

        sql_string = (
            f"DELETE FROM {cls.table_ep} "
            f"WHERE DATE(time_break) = '{prod_date.strftime("%Y-%m-%d")}';"
        )
        cursor.execute(sql_string)

        sql_string = (
            f"INSERT INTO {cls.table_ep} ("
            f"file_id, line, point, fleet, vibs, vib_count, vp_type, "
            f"avg_phase, peak_phase, avg_dist, peak_dist, "
            f"avg_force, peak_force, avg_stiffness, avg_viscosity, "
            f"easting, northing, elevation, drive, "
            f"time_break, tb_date, geom) "
            f"VALUES ({",".join(["?"]*21)}, MakePoint(?, ?, ?));"
        )
        vp_df = cls.get_ep_data_by_date(database_table, prod_date)

        for _, vp in vp_df.iterrows():
            time_diff = convert_to_list(vp.time_diff)
            sweeps = seis_utils.determine_sweeps(time_diff)[: VpType.V1.value[0]]
            easting = calc_avg(elstrtolist_and_select(sweeps, vp.easting))
            northing = calc_avg(elstrtolist_and_select(sweeps, vp.northing))
            point = Point(easting, northing)
            time_break = datetime.datetime.strptime(
                elstrtolist_and_select(sweeps, vp.time_break)[-1],
                "%Y-%m-%d %H:%M:%S.%f",
            )
            drive = round(calc_avg(elstrtolist_and_select(sweeps, vp.drive)), 0)
            ep_type = determine_vp_type(sweeps, drive)
            cursor.execute(
                sql_string,
                (
                    vp.file_id,
                    vp.line,
                    vp.point,
                    vp.fleet,
                    ", ".join(elstrtolist_and_select(sweeps, vp.vibs)),
                    vp.vib_count,
                    ep_type,
                    round(calc_avg(elstrtolist_and_select(sweeps, vp.avg_phase)), 0),
                    round(calc_avg(elstrtolist_and_select(sweeps, vp.peak_phase)), 0),
                    round(calc_avg(elstrtolist_and_select(sweeps, vp.avg_dist)), 0),
                    round(calc_avg(elstrtolist_and_select(sweeps, vp.peak_dist)), 0),
                    round(calc_avg(elstrtolist_and_select(sweeps, vp.avg_force)), 0),
                    round(calc_avg(elstrtolist_and_select(sweeps, vp.peak_force)), 0),
                    round(
                        calc_avg(elstrtolist_and_select(sweeps, vp.avg_stiffness)), 0
                    ),
                    round(
                        calc_avg(elstrtolist_and_select(sweeps, vp.avg_viscosity)), 0
                    ),
                    easting,
                    northing,
                    calc_avg(elstrtolist_and_select(sweeps, vp.elevation)),
                    drive,
                    time_break,
                    elstrtolist_and_select(sweeps, vp.tb_date)[-1],
                    point.x,
                    point.y,
                    cls.srid_projection,
                ),
            )
            next(progress_message)

    @classmethod
    @DbUtils.connect
    def update_vp_distance(
        cls, database_table: str, prod_date: datetime.datetime, fleets: int, cursor: any
    ) -> None:
        """Add values for distance, time, velocity, denseflag to the database_table
        This can only be done after all vps have been added to the database
        as only then it be sorted by consecutive vp points by vibrator
        """
        distance = "distance"
        time = "time"
        velocity = "velocity"
        match database_table:
            case "VAPS":
                table = cls.table_vaps
                fleets = VIBRATORS
                fleet_or_vibe = "vibrator"

            case "VP":
                table = cls.table_vp
                fleets = VIBRATORS
                fleet_or_vibe = "vibrator"

            case "EP":
                table = cls.table_ep
                fleet_or_vibe = "fleet"
                distance = "distance_fleet"
                time = "time_fleet"
                velocity = "velocity_fleet"

        sql_string = (
            f"UPDATE {table} "
            f"SET"
            f"    {distance} = ?, "
            f"    {time} = ?, "
            f"    {velocity} = ?, "
            f"    dense_flag = ? "
            f"WHERE id = ?;"
        )
        progress_message = seis_utils.progress_message_generator(
            f"add dist, time, vel, dense_flag to {table} for "
            f'{prod_date.strftime("%d-%m-%Y")}                          '
        )
        vp_records_df = cls.get_vp_data_by_date(database_table, prod_date)

        for fleet in range(1, fleets + 1):
            vib_df = vp_records_df[vp_records_df[fleet_or_vibe] == fleet]
            vp_pts = [
                (val[0], Point(val[1], val[2]), val[3])
                for val in zip(
                    vib_df["id"].to_list(),
                    vib_df["easting"].to_list(),
                    vib_df["northing"].to_list(),
                    vib_df["time_break"].to_list(),
                )
            ]
            # use consecutive vp's
            dense_flag = False
            for vp_a, vp_b in zip(vp_pts, vp_pts[1:]):
                index = vp_a[0]
                dx = vp_b[1].x - vp_a[1].x
                dy = vp_b[1].y - vp_a[1].y
                dist = np.sqrt(dx * dx + dy * dy)
                try:
                    t2 = datetime.datetime.strptime(vp_b[2], "%Y-%m-%d %H:%M:%S.%f")

                except ValueError:
                    t2 = datetime.datetime.strptime(vp_b[2], "%Y-%m-%d %H:%M:%S")

                try:
                    t1 = datetime.datetime.strptime(vp_a[2], "%Y-%m-%d %H:%M:%S.%f")

                except ValueError:
                    t1 = datetime.datetime.strptime(vp_a[2], "%Y-%m-%d %H:%M:%S")

                time = max(0, ((t2 - t1).seconds - SWEEP_TIME - PAD_DOWN_TIME))

                velocity = dist / time if time > 0 else 0
                dense_flag = True if dist < DENSE_CRITERIUM else False

                cursor.execute(
                    sql_string,
                    (
                        dist,
                        time,
                        velocity,
                        dense_flag,
                        index,
                    ),
                )
                next(progress_message)

            # handle data for last element if there is one
            if vp_pts:
                index = vp_pts[-1][0]
                cursor.execute(
                    sql_string,
                    (
                        np.nan,
                        np.nan,
                        np.nan,
                        dense_flag,
                        index,
                    ),
                )

    @classmethod
    @DbUtils.connect
    def get_vaps_id(cls, vp_record: VpTable, cursor: any) -> VpTable:
        """get vaps_id from the database and insert into vp_record"""
        sql_string = (
            f"SELECT id FROM {cls.table_vaps} WHERE "
            f"time_break='{vp_record.time_break}' AND "
            f"vibrator={vp_record.vibrator};"
        )
        cursor.execute(sql_string)
        try:
            vp_record.vaps_id = cursor.fetchone()[0]

        except TypeError:
            pass

        return vp_record

    @classmethod
    def get_vp_data_by_time(
        cls,
        database_table: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> pd.DataFrame:
        """retrieve vp data by time interval"""
        assert end_time >= start_time, "end time must be greater equal than start time"
        table = cls.table_vaps if database_table == "VAPS" else cls.table_vp
        engine = DbUtils().get_db_engine()
        sql_string = (
            f"SELECT * FROM {table} WHERE "
            f"time_break BETWEEN '{start_time}' AND '{end_time}' "
            f"ORDER BY time_break;"
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_vp_data_by_date(
        cls, database_table, production_date: datetime.datetime
    ) -> pd.DataFrame:
        """retrieve vp data by date"""
        match database_table:
            case "VAPS":
                table = cls.table_vaps
            case "VP":
                table = cls.table_vp
            case "EP":
                table = cls.table_ep

        engine = DbUtils().get_db_engine()
        sql_string = (
            f"SELECT * FROM {table} WHERE "
            f'DATE(time_break) = \'{production_date.strftime("%Y-%m-%d")}\' '
            f"ORDER BY time_break;"
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_vp_data_by_line(cls, database_table: str, line: int) -> pd.DataFrame:
        """retrieve vp data by line number"""
        table = cls.table_vaps if database_table == "VAPS" else cls.table_vp
        engine = DbUtils().get_db_engine()
        sql_string = f"SELECT * FROM {table} WHERE " f"line = {line} ORDER BY station;"
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    def get_ep_data_by_date(
        cls, database_table: str, production_date: datetime.datetime
    ) -> pd.DataFrame:
        engine = DbUtils().get_db_engine()
        table = cls.table_vaps if database_table == "VAPS" else cls.table_vp

        """retrieve ep data of the fleet by date"""
        sql_string = (
            f"SELECT "
            f"file_id, "
            f"line, "
            f"point, "
            f"fleet, "
            f"group_concat(vibrator) vibs, "
            f"count(*) vib_count, "
            f"group_concat(avg_phase) avg_phase, "
            f"group_concat(peak_phase) peak_phase, "
            f"group_concat(avg_dist) avg_dist, "
            f"group_concat(peak_dist) peak_dist, "
            f"group_concat(avg_force) avg_force, "
            f"group_concat(peak_force) peak_force, "
            f"group_concat(avg_stiffness) avg_stiffness, "
            f"group_concat(avg_viscosity) avg_viscosity, "
            f"group_concat(easting) easting, "
            f"group_concat(northing) northing, "
            f"group_concat(elevation) elevation, "
            f"group_concat(drive) drive, "
            f"group_concat(time_break) time_break, "
            f"group_concat(tb_date) tb_date, "
            f"group_concat(time_diff) time_diff "
            f"FROM (SELECT "
            f"*, "
            f"(julianday(time_break) - julianday(lag(time_break) over (ORDER BY time_break)))* 86400 as time_diff "
            f"FROM {table} "
            f"ORDER BY time_break "
            f") "
            f"WHERE DATE(time_break) = '{production_date.strftime("%Y-%m-%d")}' "
            f"GROUP BY line, point "
            f"ORDER BY time_break; "
        )
        return pd.read_sql_query(sql_string, con=engine)

    @classmethod
    @DbUtils.connect
    def delete_last_file_id(cls, cursor: any) -> str | int:
        """deletes the last vaps file record, returns the name of the deleted file"""
        sql_string = (
            f"select file_name, id from {cls.table_vaps_files} "
            f"where id = (select max(id) from {cls.table_vaps_files})"
        )
        cursor.execute(sql_string)
        try:
            filename, id = cursor.fetchone()

        except TypeError:
            return -1

        sql_string = f"delete from {cls.table_vaps} " f"where file_id = {id}"
        cursor.execute(sql_string)

        sql_string = f"delete from {cls.table_ep} " f"where file_id = {id}"
        cursor.execute(sql_string)

        sql_string = f"delete from {cls.table_vaps_files} " f"where id = {id}"
        cursor.execute(sql_string)

        return filename
