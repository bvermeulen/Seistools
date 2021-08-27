''' module to update sps files in the database
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021

'''
from vp_update import PROGRESS_SKIPS
import warnings
import datetime
import numpy as np
import seis_utils
from seis_sps_database import SpsDb
from seis_settings import (
    DATA_FILES_SPS, GMT_OFFSET, FilesSpsTable, SpsTable,
)

# ignore warning velocity =  dist / time in method update_vo_distance
warnings.filterwarnings("ignore", category=RuntimeWarning)
HEADER_ROWS = 89
PROGRESS_SKIPS = 750


class Sps:
    sps_base_folder = DATA_FILES_SPS
    sps_db = SpsDb()

    @classmethod
    def read_sps(cls, block_name):
        sps_folder = cls.sps_base_folder / block_name

        for filename in sps_folder.glob('*.*'):
            if not filename.is_file() or filename.suffix.lower() != '.sps':
                continue

            sps_file = FilesSpsTable(*[None]*4)

            sps_file.file_name = filename.name
            sps_file.file_date = (
                datetime.datetime.fromtimestamp(filename.stat().st_mtime)
            )
            sps_file.block_name = block_name
            file_id = cls.sps_db.update_sps_file(sps_file)

            if file_id == -1:
                continue

            sps_records = []
            sps_signatures = np.array([])
            count = 0
            with open(filename, mode='rt') as sps:

                sps_lines = sps.readlines()
                progress_bar = seis_utils.set_progress_bar(
                    len(sps_lines) - HEADER_ROWS, sps_file.file_name, PROGRESS_SKIPS
                )
                for sps_line in sps_lines:

                    if sps_line[0] != 'S':
                        continue

                    sps_record = cls.parse_sps_line(sps_line, file_id)
                    sps_records, sps_signatures = cls.update_sps_records(
                        sps_records, sps_signatures, sps_record)

                    if count % PROGRESS_SKIPS == 0:
                        progress_bar.next()
                    count += 1

            print(f'\n{count - len(sps_records)} '
                  f'duplicates have been deleted ...', end='')

            if sps_records:
                cls.sps_db.update_sps(sps_records)

            progress_bar.finish()

    @classmethod
    def parse_sps_line(cls, sps_line, file_id):
        sps_record = SpsTable(*[None]*13)

        try:
            # create time break date
            time_break_str = ''.join([
                sps_line[84:86], '-',    # day
                sps_line[82:84], '-',    # month
                sps_line[80:82], ' ',    # year
                sps_line[87:89],         # hour
                sps_line[89:91],         # minute
                sps_line[91:93], '.000', # second
                sps_line[93:96]          # millisecond
            ])
            time_break_time = datetime.datetime.strptime(
                time_break_str, '%d-%m-%y %H%M%S.%f'
            )
            sps_record.file_id = file_id
            sps_record.sps_type = sps_line[0:1]
            sps_record.line = int(float(sps_line[6:11]))
            sps_record.point = int(float(sps_line[16:21]))
            sps_record.point_index = int(float(sps_line[23:24]))
            sps_record.source_type = sps_line[24:29]
            sps_record.easting = float(sps_line[46:55])
            sps_record.northing = float(sps_line[55:65])
            sps_record.elevation = float(sps_line[65:71])
            sps_record.dpg_filename = sps_line[80:103]
            sps_record.time_break = time_break_time
            sps_record.vibrator = int(float(sps_line[97:99]))

        except ValueError:
            sps_record = SpsTable(*[None]*13)

        return sps_record

    @staticmethod
    def update_sps_records(sps_records, record_signatures, sps_record):
        ''' function that adds sps_record to the list sps_records. It keeps a list
            of duplicate dpg_filesnames
            arguments:
              sps_records: list of vp_records
              record_signatures: np array of record signatures
              duplicates: np array of duplicate indexes
              sps_record: sps attributes of type SpsRecord
            return:
              sps_records: list of sps_records of type SpsRecord
              record_signatures: np array of record signatures of type string
              duplicates: np array of indexes of type int
        '''
        if not sps_record.line:
            return sps_records, record_signatures

        # search duplicate records and remove
        record_signature = sps_record.dpg_filename

        # remove a duplicate. Note there should only be zero or one duplicate, as a duplicate
        # gets removed on first instance
        duplicate = np.where(record_signatures == record_signature)[0]

        # bug fix: if duplicate: returns False if first and only element of the array has a
        # a value of 0!! Therefore test on numpy size the array.
        if  duplicate.size != 0:
            sps_records.pop(duplicate[0])
            record_signatures = np.delete(record_signatures, duplicate)

        # add the record ...
        sps_records.append(sps_record)
        record_signatures = np.append(record_signatures, record_signature)

        return sps_records, record_signatures


if __name__ == '__main__':
    sps_db = SpsDb()
    sps_db.create_table_sps_files()
    sps_db.create_table_sps()

    sps = Sps()
    block_name = input('Please enter the block folder name: ')
    sps.read_sps(block_name)
