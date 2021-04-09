''' Read noise test and store to database
'''
import os
from datetime import datetime
from seis_settings import DATA_FILES_RECEIVERS, FilesNodeTable, NodeTable
import seis_utils
import seis_database

node_db = seis_database.RcvDb()

class Rcv:

    @classmethod
    def read_nodes(cls):
        for foldername, _, filenames in os.walk(DATA_FILES_RECEIVERS):
            for filename in filenames:
                if filename[-4:] not in ['.txt', '.TXT']:
                    continue

                node_file = FilesNodeTable(*[None]*2)

                abs_filename = os.path.abspath(os.path.join(foldername, filename))
                node_file.file_name = abs_filename
                node_file.file_date = (
                    datetime.fromtimestamp(os.stat(abs_filename).st_mtime))

                id_file = node_db.update_node_file(node_file)
                if id_file == -1:
                    continue

                progress_message = seis_utils.progress_message_generator(
                    f'reading receiver data from {node_file.file_name}   ')

                node_records = []
                with open(abs_filename, mode='rt') as node:
                    node_lines = node.readlines()

                time_stamp = ''
                for node_line in node_lines:
                    if node_line[0:13] == 'Date and Time':
                        time_stamp = datetime.strptime(
                            node_line[40:61].strip(), '%b %d %H:%M:%S %Y')

                    if node_line[1:2] == 'Q':
                        node_record = cls.parse_node_line(node_line)

                        if node_record.qtm_sn:
                            node_record.id_file = id_file
                            node_record.time_stamp = time_stamp
                            node_records.append(node_record)
                            next(progress_message)

                error_message = node_db.update_node_attributes_records(node_records)
                if error_message:
                    print(f'\n{error_message}')
                    node_db.delete_node_file(id_file)


    @staticmethod
    def parse_node_line(node_line):
        def cval(val):
            val = val.strip().lower()
            if val[0:2] == '--':
                return None
            elif val[0:2] == 'pa':
                return None
            elif val[0:3] == 'n/a':
                return None

            return val

        empty_record = NodeTable(*[None]*23)
        # fix variable length for attribute noise QC
        node_line = node_line.strip('\n')
        s = len(node_line) - 162
        node_line = node_line[:69] + node_line[69+s:]

        node_record = NodeTable(*[None]*23)
        try:
            node_record.line = int(cval(node_line[24:35]))
            node_record.station = int(cval(node_line[36:47]))
            node_record.rcvr_index = 1
            node_record.qtm_sn = cval(node_line[1:8])
            node_record.battery = float(
                cval(node_line[18:23])) if cval(node_line[18:23]) else None
            node_record.ch = int(
                cval(node_line[48:50])) if cval(node_line[48:50]) else None
            node_record.type = node_line[57:72]
            node_record.noise_qc = float(
                cval(node_line[73:78])) if cval(node_line[73:78]) else None
            node_record.noise_bits = float(
                cval(node_line[80:85])) if cval(node_line[80:85]) else None
            node_record.frequency = float(
                cval(node_line[87:91])) if cval(node_line[87:91]) else None
            node_record.damping = float(
                cval(node_line[93:98])) if cval(node_line[93:98]) else None
            node_record.sensitivity = float(
                cval(node_line[100:106])) if cval(node_line[100:106]) else None
            node_record.resistance = float(
                cval(node_line[108:113])) if cval(node_line[108:113]) else None
            node_record.leakage = float(
                cval(node_line[115:119])) if cval(node_line[115:119]) else None
            node_record.thd = float(
                cval(node_line[121:128])) if cval(node_line[121:128]) else None
            node_record.crossfeed = float(
                cval(node_line[130:134])) if cval(node_line[130:134]) else None
            node_record.power = float(
                cval(node_line[136:140])) if cval(node_line[136:140]) else None
            node_record.cmr = float(
                cval(node_line[142:146])) if cval(node_line[142:146]) else None
            node_record.tilt = float(
                cval(node_line[148:154])) if cval(node_line[148:154]) else None
            node_record.acqrate = float(
                cval(node_line[155:161])) if cval(node_line[155:161]) else None

        except (ValueError, TypeError):
            node_record = empty_record


        # only except records where there are numerical values for all of the below keys
        keys = [
            'battery', 'noise_qc', 'noise_bits', 'frequency', 'damping', 'sensitivity',
            'resistance', 'thd', 'tilt'
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
