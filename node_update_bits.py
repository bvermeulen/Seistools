''' Read noise test and store to database
'''
import os
from datetime import datetime
import pandas as pd
from seis_settings import DATA_FILES_RECEIVERS, FilesNodeTable, NodeTable
import seis_utils
import seis_database

node_db = seis_database.RcvDb()

class Rcv:

    @classmethod
    def read_nodes(cls):
        for foldername, _, filenames in os.walk(DATA_FILES_RECEIVERS):
            for filename in filenames:
                if filename[-5:] not in ['.xlsx', '.XLSX']:
                    continue

                node_file = FilesNodeTable(*[None]*2)

                abs_filename = os.path.abspath(os.path.join(foldername, filename))
                node_file.file_name = abs_filename
                node_file.file_date = (
                    datetime.fromtimestamp(os.stat(abs_filename).st_mtime).strftime(
                        '%Y-%m-%d %H:%M:%S')
                )

                id_file = node_db.update_node_file(node_file)
                if id_file == -1:
                    continue

                progress_message = seis_utils.progress_message_generator(
                    f'reading receiver data from {node_file.file_name}   ')

                bits_df = pd.read_excel(abs_filename, header=None, skiprows=1)
                print(len(bits_df))
                bits_df = bits_df.drop_duplicates(subset=[0], keep='last')
                print(len(bits_df))

                node_records = []
                for _, bits_row in bits_df.iterrows():

                    node_record = cls.parse_node_line(bits_row)

                    if node_record.qtm_sn:
                        node_record.id_file = id_file
                        node_records.append(node_record)
                        next(progress_message)

                error_message = node_db.update_node_attributes_records(node_records)
                if error_message:
                    print(f'\n{error_message}')
                    node_db.delete_node_file(id_file)

    @staticmethod
    def parse_node_line(bits_row):
        empty_record = NodeTable(*[None]*26)
        node_record = NodeTable(*[None]*26)
        try:
            node_record.qtm_sn = bits_row[0]
            node_record.line = int(bits_row[1])
            node_record.station = int(bits_row[2])
            node_record.rcvr_index = 1
            node_record.software = bits_row[3]
            node_record.geoph_model = bits_row[4]
            node_record.test_time = bits_row[5].strftime('%Y-%m-%d %H:%M:%S')
            node_record.temp = bits_row[6] if bits_row[6] > 0 else None
            node_record.bits_type = bits_row[7]
            node_record.tilt = bits_row[8] if bits_row[8] > 0 else None
            node_record.config_id = bits_row[9]
            node_record.resistance = bits_row[10] if bits_row[10] > 0 else None
            node_record.noise = bits_row[11] if bits_row[11] > 0 else None
            node_record.thd = bits_row[12] if bits_row[12] > 0 else None
            node_record.polarity = bits_row[13]
            node_record.frequency = bits_row[14] if bits_row[14] > 0 else None
            node_record.damping = bits_row[15] if bits_row[15] > 0 else None
            node_record.sensitivity = bits_row[16] if bits_row[16] > 0 else None
            node_record.dyn_range = bits_row[17]
            node_record.ein = bits_row[18]
            node_record.gain = bits_row[19]
            node_record.offset = bits_row[20]
            node_record.gps_time = int(bits_row[21])
            node_record.ext_geophone = 1 if bits_row[22] == 'TRUE' else 0

        except (ValueError, TypeError):
            node_record = empty_record

        # only except records where there are numerical values for all of the below keys
        keys = [
            'tilt', 'resistance', 'noise', 'thd', 'frequency', 'damping', 'sensitivity'
        ]
        try:
            _ = sum([v for k, v in node_record._asdict().items() if k in keys])

        except TypeError:
            node_record = empty_record

        return node_record


def main():
    node_db.create_table_node_files()
    node_db.create_table_node_attributes()

    rcv = Rcv()
    rcv.read_nodes()


if __name__ == '__main__':
    main()
