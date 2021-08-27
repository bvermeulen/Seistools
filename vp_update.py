''' module to update vaps and vp record files in the database
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021

'''
import warnings
import datetime
import numpy as np
import seis_utils
from seis_vibe_database import VpDb
from seis_settings import (DATA_FILES_VAPS, DATA_FILES_VP, LINK_VP_TO_VAPS, GMT_OFFSET,
                           FilesVpTable, VpTable, FilesVapsTable, VapsTable,
                          )

# ignore warning velocity =  dist / time in method update_vo_distance
warnings.filterwarnings("ignore", category=RuntimeWarning)
HEADER_ROWS = 71
PROGRESS_SKIPS = 750


class Vaps:

    vaps_base_folder = DATA_FILES_VAPS
    vp_db = VpDb()

    @classmethod
    def read_vaps(cls):
        for filename in cls.vaps_base_folder.glob('*.*'):
            if not filename.is_file() or filename.suffix.lower() not in ['.vaps', '.txt']:
                continue

            vaps_file = FilesVapsTable(*[None]*3)

            vaps_file.file_name = filename.name
            vaps_file.file_date = (
                datetime.datetime.fromtimestamp(filename.stat().st_mtime)
            )
            file_id = cls.vp_db.update_vaps_file(vaps_file)

            if file_id == -1:
                continue

            vaps_records = []
            vaps_signatures = np.array([])
            count = 0
            with open(filename, mode='rt') as vaps:

                vaps_lines = vaps.readlines()
                progress_bar = seis_utils.set_progress_bar(
                    len(vaps_lines) - HEADER_ROWS, vaps_file.file_name, PROGRESS_SKIPS
                )
                for vaps_line in vaps_lines:
                    if vaps_line[0] != 'A':
                        continue

                    vaps_record = cls.parse_vaps_line(vaps_line, file_id)
                    vaps_records, vaps_signatures = cls.update_vp_records(
                        vaps_records, vaps_signatures, vaps_record)

                    if count % PROGRESS_SKIPS == 0:
                        progress_bar.next()
                    count += 1

                print(f'\n{count - len(vaps_records)} '
                      f'duplicates have been deleted ...', end='')

                if vaps_records:
                    cls.vp_db.update_vaps(vaps_records)
                    cls.vp_db.update_vp_distance(
                        'VAPS', vaps_records[0].time_break.date()
                    )
                progress_bar.finish()

    @classmethod
    def parse_vaps_line(cls, vaps_line, file_id):
        vaps_record = VapsTable(*[None]*26)

        try:
            # create time break date
            doy = int(vaps_line[117:120])
            year = seis_utils.get_year(doy)

            time_break = (datetime.datetime.strptime(datetime.datetime.strptime(
                str(year) + f'{doy:03}', '%Y%j').strftime('%d-%m-%y') + ' ' +  \
                    vaps_line[120:126] + '.' + vaps_line[144:147], '%d-%m-%y %H%M%S.%f'))

            vaps_record.line = int(float(vaps_line[1:17]))
            vaps_record.station = int(float(vaps_line[17:25]))
            vaps_record.fleet_nr = vaps_line[26:27]
            vaps_record.vibrator = int(vaps_line[27:29])
            vaps_record.drive = int(vaps_line[29:32])
            vaps_record.avg_phase = int(vaps_line[32:36])
            vaps_record.peak_phase = int(vaps_line[36:40])
            vaps_record.avg_dist = int(vaps_line[40:42])
            vaps_record.peak_dist = int(vaps_line[42:44])
            vaps_record.avg_force = int(vaps_line[44:46])
            vaps_record.peak_force = int(vaps_line[46:49])
            vaps_record.avg_stiffness = int(vaps_line[49:52])
            vaps_record.avg_viscosity = int(vaps_line[52:55])
            vaps_record.easting = float(vaps_line[55:64])
            vaps_record.northing = float(vaps_line[64:74])
            vaps_record.elevation = float(vaps_line[74:80])
            vaps_record.time_break = time_break
            vaps_record.hdop = float(vaps_line[126:130])
            vaps_record.tb_date = vaps_line[130:150]
            vaps_record.positioning = vaps_line[150:225]

            vaps_record.file_id = file_id

        except ValueError:
            vaps_record = VapsTable(*[None]*26)

        return vaps_record

    @staticmethod
    def update_vp_records(vp_records, record_signatures, vp_record):
        ''' function to add vp_record to the list vp_records. For each record it makes a 10
            digits 'signature' being <line (4)><stations (4)><vibrator (2)>. It keeps a list
            of the indexes of duplicates
            arguments:
                vp_records: list of vp_records
                record_signatures: np array of record signatures
                duplicates: np array of duplicae indexes
                vp_record: vp attributes of type VpRecord
            return:
                vp_records: list of vp_records of type VpRecord
                record_signatures: np array of record signatures of type string
                duplicates: np array of indexes of type int
        '''
        if not vp_record.line:
            return vp_records, record_signatures

        # search duplicate records and remove
        line, station, vib = vp_record.line, vp_record.station, vp_record.vibrator
        record_signature = f'{line:04}' + f'{station:04}' + f'{vib:02}'

        # remove a duplicate. Note there should only be zero or one duplicate, as a duplicate
        # gets removed on first instance
        duplicate = np.where(record_signatures == record_signature)[0]

        # bug fix: if duplicate: returns False if first and only element of the array has a
        # a value of 0!! Therefore test on numpy size the array.
        if  duplicate.size != 0:
            vp_records.pop(duplicate[0])
            record_signatures = np.delete(record_signatures, duplicate)

        # add the record ...
        vp_records.append(vp_record)
        record_signatures = np.append(record_signatures, record_signature)

        return vp_records, record_signatures


class Vp:
    vp_base_folder = DATA_FILES_VP
    vp_db = VpDb()

    @classmethod
    def read_vp(cls):
        for filename in cls.vp_base_folder.glob('*.*'):
            if not filename.is_file() or filename.suffix.lower != '.txt':
                continue

            vp_file = FilesVpTable(*[None]*3)

            vp_file.file_name = filename.name
            vp_file.file_date = (
                datetime.datetime.fromtimestamp(filename.stat().st_mtime)
            )
            file_id = cls.vp_db.update_vp_file(vp_file)

            if file_id == -1:
                continue

            vp_records = []
            vp_signatures = np.array([])
            count = 0
            with open(filename, mode='rt') as vp:

                vp_lines = vp.readlines()
                progress_bar = seis_utils.set_progress_bar(
                    len(vp_lines) - HEADER_ROWS, vp_file.file_name, PROGRESS_SKIPS
                )
                for vp_line in vp_lines:
                    if vp_line[0:9].strip() == 'Line':
                        continue

                    vp_record = cls.parse_vp_line(vp_line, file_id)
                    vp_records, vp_signatures = cls.update_vp_records(
                        vp_records, vp_signatures, vp_record)

                    if count % PROGRESS_SKIPS == 0:
                        progress_bar.next()
                    count += 1

                print(f'\n{count - len(vp_records)} '
                      f'duplicates have been deleted ...', end='')

                if vp_records:
                    cls.vp_db.update_vp(vp_records, link_vaps=LINK_VP_TO_VAPS)
                    cls.vp_db.update_vp_distance(
                        'VP', vp_records[0].time_break.date()
                    )
                progress_bar.finish()

    @staticmethod
    def parse_vp_line(vp_line, file_id):
        vp_record = VpTable(*[None]*24)

        try:
            # create time break date and adjust to local time
            time_break = (datetime.datetime.strptime(datetime.datetime.strptime(
                vp_line[32:51], '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%y %H:%M:%S') +  \
                    '.' + vp_line[52:55] + '000', '%d-%m-%y %H:%M:%S.%f'))

            time_break += GMT_OFFSET

            vp_record.line = int(vp_line[0:9])
            vp_record.station = int(vp_line[9:19])
            vp_record.vibrator = int(vp_line[19:29].strip()[3:])
            vp_record.time_break = time_break
            vp_record.planned_easting = float(vp_line[64:79])
            vp_record.planned_northing = float(vp_line[79:94])
            vp_record.easting = float(vp_line[109:124])
            vp_record.northing = float(vp_line[124:139])
            vp_record.elevation = float(vp_line[139:154])
            vp_record.offset = float(vp_line[154:166])
            vp_record.peak_force = int(vp_line[166:178])
            vp_record.avg_force = int(vp_line[178:190])
            vp_record.peak_dist = int(vp_line[190:202])
            vp_record.avg_dist = int(vp_line[202:214])
            vp_record.peak_phase = int(vp_line[214:226])
            vp_record.avg_phase = int(vp_line[226:238])
            vp_record.qc_flag = vp_line[238:248].strip()

            vp_record.file_id = file_id

        except ValueError:
            vp_record = VpTable(*[None]*24)

        return vp_record

    @staticmethod
    def update_vp_records(vp_records, record_signatures, vp_record):
        ''' function to add vp_record to the list vp_records. For each record it makes a 10
            digits 'signature' being <line (4)><stations (4)><vibrator (2)>. It keeps a list
            of the indexes of duplicates
            arguments:
                vp_records: list of vp_records
                record_signatures: np array of record signatures
                duplicates: np array of duplicae indexes
                vp_record: vp attributes of type VpRecord
            return:
                vp_records: list of vp_records of type VpRecord
                record_signatures: np array of record signatures of type string
                duplicates: np array of indexes of type int
        '''
        if not vp_record.line:
            return vp_records, record_signatures

        # search duplicate records and remove
        line, station, vib = vp_record.line, vp_record.station, vp_record.vibrator
        record_signature = f'{line:04}' + f'{station:04}' + f'{vib:02}'

        # remove a duplicate. Note there should only be zero or one duplicate, as a duplicate
        # gets removed on first instance
        duplicate = np.where(record_signatures == record_signature)[0]

        # bug fix: if duplicate: returns False if first and only element of the array has a
        # a value of 0!! Therefore test on numpy size the array.
        if  duplicate.size != 0:
            vp_records.pop(duplicate[0])
            record_signatures = np.delete(record_signatures, duplicate)

        # add the record ...
        vp_records.append(vp_record)
        record_signatures = np.append(record_signatures, record_signature)

        return vp_records, record_signatures


if __name__ == '__main__':
    vp_db = VpDb()
    vp_db.create_table_vaps_files()
    vp_db.create_table_vaps()
    # vp_db.create_table_vp_files()
    # vp_db.create_table_vp()

    vaps = Vaps()
    vaps.read_vaps()

    # vp = Vp()
    # vp.read_vp()
