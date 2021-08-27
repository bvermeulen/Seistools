''' Read noise test for GTI nodes and store to database
'''
from datetime import datetime, timedelta
from vp_update import PROGRESS_SKIPS
import pandas as pd
import seis_utils
from seis_nuseis_database import NuseisDb
from seis_settings import DATA_FILES_NUSEIS, FilesNodeTable, NuseisTable


PROGRESS_SKIPS = 200
node_db = NuseisDb()

class Rcv:

    @classmethod
    def read_nodes(cls):
        for filename in DATA_FILES_NUSEIS.glob('*.*'):

            if not filename.is_file() or filename.suffix.lower() != '.csv':
                continue

            node_file = FilesNodeTable(*[None]*2)

            node_file.file_name = filename.name
            node_file.file_date = (
                datetime.fromtimestamp(filename.stat().st_mtime).strftime(
                    '%Y-%m-%d %H:%M:%S')
            )

            id_file = node_db.update_node_file(node_file)
            if id_file == -1:
                continue

            try:
                nuseis_df = pd.read_csv(filename)

            except PermissionError:
                node_db.delete_node_file(id_file)
                nuseis_df = pd.DataFrame()

            nuseis_df = nuseis_df.drop_duplicates(
                subset=['Serial_Number'], keep='last')
            node_records = []

            progress_bar = seis_utils.set_progress_bar(
                nuseis_df.shape[0], filename.name, PROGRESS_SKIPS
            )

            count = 0
            for _, nuseis_row in nuseis_df.iterrows():

                node_record = cls.parse_node_line(nuseis_row)

                if node_record.nuseis_sn:
                    node_record.id_file = id_file
                    node_records.append(node_record)

                if count % PROGRESS_SKIPS == 0:
                    next(progress_bar)
                count += 1

            if error_message := node_db.update_node_attributes_records(node_records):
                print(f'\n{error_message}')
                node_db.delete_node_file(id_file)

            progress_bar.finish()

    @staticmethod
    def parse_node_line(nuseis_row):
        empty_record = NuseisTable(*[None]*13)
        node_record = NuseisTable(*[None]*13)

        try:
            node_record.nuseis_sn = int(nuseis_row['Serial_Number'])
            node_record.line = int(nuseis_row['Line'])
            node_record.station = int(nuseis_row['Station'])
            node_record.rcvr_index = 1
            node_record.tilt = (
                float(180.0 - nuseis_row['Tilt_Angle'])
                if nuseis_row['Tilt_Angle'] > 0 else None
            )
            node_record.noise = (
                float(nuseis_row['Spread_Noise']) * 0.001
                if nuseis_row['Spread_Noise'] > 0 else None
            )
            node_record.resistance = (
                float(nuseis_row['Resistance'])
                if nuseis_row['Resistance'] > 0 else None
            )
            node_record.impedance = (
                float(nuseis_row['Impedance'])
                if nuseis_row['Impedance'] > 0 else None
            )
            node_record.thd = (
                float(nuseis_row['Total_Harmonic_Distortion'])
                if nuseis_row['Total_Harmonic_Distortion'] > 0 else None
            )
            node_record.time_deployment = (
                datetime.strptime(
                    nuseis_row['Deployment_Date_Time_UTC'], '%d-%m-%y %H:%M') +
                    timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')
            node_record.time_lastscan = (
                datetime.strptime(nuseis_row['DLast_Scan_UTC'], '%d-%m-%y %H:%M') +
                timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')

        except (ValueError, TypeError):
            return empty_record


        # skip records where scan date is same as the deployment date
        if node_record.time_lastscan[:10] == node_record.time_deployment[:10]:
            return empty_record

        # only except records where there are numerical values for all of the below keys
        keys = [
            'tilt', 'noise', 'resistance', 'impedance', 'thd'
        ]
        try:
            r = sum([v for k, v in node_record._asdict().items() if k in keys])
            if r < 0.5:
                return empty_record

        except TypeError:
            return empty_record



        return node_record


def main():
    node_db.create_table_node_files()
    node_db.create_table_node_attributes()

    rcv = Rcv()
    rcv.read_nodes()


if __name__ == '__main__':
    main()
