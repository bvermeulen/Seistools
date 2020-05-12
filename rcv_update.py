''' Read noise test and store to database
'''
import os
from datetime import datetime
from seis_settings import DATA_FILES_RECEIVERS, FilesRcvTable, RcvTable
import seis_utils
import seis_database


class Rcv:
    rcv_base_folder = DATA_FILES_RECEIVERS
    rcv_db = seis_database.RcvDb()

    @classmethod
    def read_rcv(cls):
        for foldername, _, filenames in os.walk(cls.rcv_base_folder):
            for filename in filenames:
                if filename[-5:] not in ['.noon', '.NOON']:
                    continue

                rcv_file = FilesRcvTable(*[None]*2)

                abs_filename = os.path.abspath(os.path.join(foldername, filename))
                rcv_file.file_name = abs_filename
                rcv_file.file_date = (
                    datetime.fromtimestamp(os.stat(abs_filename).st_mtime))

                id_file = cls.rcv_db.update_rcv_file(rcv_file)

                if id_file == -1:
                    continue

                progress_message = seis_utils.progress_message_generator(
                    f'reading receiver data from {rcv_file.file_name}   ')

                rcv_records = []
                with open(abs_filename, mode='rt') as rcv:
                    for rcv_line in rcv.readlines():
                        # if rcv_line[0:7].strip() != 'FDU-428':
                        #     continue

                        rcv_record = cls.parse_rcv_line(rcv_line)
                        if rcv_record.fdu_sn:
                            rcv_record.id_file = id_file
                            rcv_records.append(rcv_record)
                            next(progress_message)

                cls.rcv_db.update_rcv(rcv_records)

    @staticmethod
    def parse_rcv_line(rcv_line):
        rcv_record = RcvTable(*[None]*15)

        rcv_line = rcv_line.strip('\n')
        attributes = rcv_line.split('\t')

        if len(attributes) != 13:
            return rcv_record

        try:
            rcv_record.fdu_sn = int(attributes[1])
            rcv_record.line = int(attributes[2])
            rcv_record.station = int(attributes[3])
            rcv_record.sensor_type = int(attributes[4])
            rcv_record.resistance = float(attributes[5])
            rcv_record.tilt = float(attributes[6])
            rcv_record.noise = float(attributes[7])
            rcv_record.leakage = float(attributes[8])

            try:
                rcv_record.time_update = datetime.strptime(
                    attributes[9], '%m/%d/%y %I:%M:%S %p')

            except ValueError:
                rcv_record.time_update = datetime.strptime(
                    attributes[9], '%m-%d-%y %H:%M')

            rcv_record.easting = float(attributes[10])
            rcv_record.northing = float(attributes[11])
            rcv_record.elevation = float(attributes[12])

        except ValueError:
            rcv_record = RcvTable(*[None]*15)

        if rcv_record.fdu_sn:
            # crew occasional is mixing up easting and northing, therefore assert
            assert rcv_record.northing > rcv_record.easting, (
                f'northing must be > easting: '
                f'{rcv_record.northing:,.0f} > {rcv_record.easting:,.0f}')

        return rcv_record

def main():
    rcv_db = seis_database.RcvDb()
    rcv_db.create_table_files()
    rcv_db.create_table_records()

    rcv = Rcv()
    rcv.read_rcv()

if __name__ == '__main__':
    main()
