''' module to update vaps and vp record files in the database
'''
import os
import warnings
import datetime
import seis_database
import seis_utils
from seis_settings import (DATA_FILES_VAPS, DATA_FILES_VP, LINK_VP_TO_VAPS, GMT_OFFSET,
                           FilesVpTable, VpTable, FilesVapsTable, VapsTable,
                          )

# ignore warning velocity =  dist / time in method patch_add_distance_column
warnings.filterwarnings("ignore", category=RuntimeWarning)

class Vaps:

    vaps_base_folder = DATA_FILES_VAPS
    vp_db = seis_database.VpDb()

    @classmethod
    def read_vaps(cls):
        for foldername, _, filenames in os.walk(cls.vaps_base_folder):
            for filename in filenames:
                if not (filename[-5:] in ['.vaps', '.VAPS'] or
                        filename[-4:] in ['.txt', '.TXT']):
                    continue

                vaps_file = FilesVapsTable(*[None]*3)

                abs_filename = os.path.abspath(os.path.join(foldername, filename))
                vaps_file.file_name = abs_filename
                vaps_file.file_date = (
                    datetime.datetime.fromtimestamp(os.stat(abs_filename).st_mtime))

                file_id = cls.vp_db.update_vaps_file(vaps_file)

                if file_id == -1:
                    continue

                progress_message = seis_utils.progress_message_generator(
                    f'reading vaps from {vaps_file.file_name}   ')

                vaps_records = []
                with open(abs_filename, mode='rt') as vaps:
                    for vaps_line in vaps.readlines():
                        if vaps_line[0] != 'A':
                            continue

                        vaps_record = cls.parse_vaps_line(vaps_line)
                        if  vaps_record.line:
                            vaps_record.file_id = file_id
                            vaps_records.append(vaps_record)

                        next(progress_message)

                cls.vp_db.update_vaps(vaps_records)
                if vaps_records:
                    _date = vaps_records[0].time_break.date()
                    cls.vp_db.patch_add_distance_column('VAPS', _date, _date)

                print()

    @classmethod
    def parse_vaps_line(cls, vaps_line):
        vaps_record = VapsTable(*[None]*26)

        try:
            # create time break date
            doy = int(vaps_line[117:120])
            year = seis_utils.get_year(doy)

            time_break = (datetime.datetime.strptime(datetime.datetime.strptime(
                str(year) + f'{doy:03}', '%Y%j').strftime('%d-%m-%y') + ' ' +  \
                    vaps_line[120:126] + '.' + vaps_line[144:147], '%d-%m-%y %H%M%S.%f'))

            vaps_record.line = int(float(vaps_line[1:17]))
            vaps_record.point = int(float(vaps_line[17:25]))
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

        except ValueError:
            vaps_record = VapsTable(*[None]*26)

        return vaps_record

class Vp:

    vp_base_folder = DATA_FILES_VP
    vp_db = seis_database.VpDb()

    @classmethod
    def read_vp(cls):
        for foldername, _, filenames in os.walk(cls.vp_base_folder):
            for filename in filenames:
                if filename[-4:] not in ['.txt', '.TXT']:
                    continue

                vp_file = FilesVpTable(*[None]*3)

                abs_filename = os.path.abspath(os.path.join(foldername, filename))
                vp_file.file_name = abs_filename
                vp_file.file_date = (
                    datetime.datetime.fromtimestamp(os.stat(abs_filename).st_mtime))

                file_id = cls.vp_db.update_vp_file(vp_file)

                if file_id == -1:
                    continue

                progress_message = seis_utils.progress_message_generator(
                    f'reading vp from {vp_file.file_name}   ')

                vp_records = []
                with open(abs_filename, mode='rt') as vp:
                    for vp_line in vp.readlines():
                        if vp_line[0:9].strip() == 'Line':
                            continue

                        vp_record = cls.parse_vp_line(vp_line)
                        if vp_record.line:
                            vp_record.file_id = file_id
                            vp_records.append(vp_record)

                        next(progress_message)

                cls.vp_db.update_vp(vp_records, link_vaps=LINK_VP_TO_VAPS)
                if vp_records:
                    _date = vp_records[0].time_break.date()
                    cls.vp_db.patch_add_distance_column('VP', _date, _date)

                print()

    @staticmethod
    def parse_vp_line(vp_line):
        vp_record = VpTable(*[None]*24)

        try:
            # create time break date
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

        except ValueError:
            vp_record = VpTable(*[None]*24)

        return vp_record


if __name__ == '__main__':
    vp_db = seis_database.VpDb()
    vp_db.create_table_vaps_files()
    vp_db.create_table_vaps()
    vp_db.create_table_vp_files()
    vp_db.create_table_vp()

    vaps = Vaps()
    vaps.read_vaps()

    vp = Vp()
    vp.read_vp()
