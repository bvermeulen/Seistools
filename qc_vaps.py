''' module to update vaps and vp record files in the database
    author: Bruno Vermeulen
    email: bvermeulen@hotmail.com
    Copyright: 2021

'''
import warnings
import datetime
from pathlib import Path
import pandas as pd
import seis_utils
from seis_settings import GMT_OFFSET, VapsTable, PROGRESS_SKIPS
from pprint import pprint

# ignore warning velocity =  dist / time in method update_vo_distance
warnings.filterwarnings("ignore", category=RuntimeWarning)
HEADER_ROWS = 71

class Vaps:
    record_vaps_header = [
        'vibrator', 'time_break', 'avg_phase_v', 'peak_phase_v', 'avg_dist_v',
        'peak_dist_v', 'avg_force_v', 'peak_force_v',
    ]

    def __init__(self, filename):
        self.filename = filename
        self._avg_peak_df = pd.DataFrame(columns=self.record_vaps_header)

    @property
    def avg_peak_df(self):
        return self._avg_peak_df

    def read_vaps(self):
        with open(self.filename, mode='rt') as vaps:

            vaps_lines = vaps.readlines()
            progress_bar = seis_utils.set_progress_bar(
                len(vaps_lines) - HEADER_ROWS, self.filename, PROGRESS_SKIPS
            )
            count = 0
            for vaps_line in vaps_lines:
                if vaps_line[0] != 'A':
                    continue

                vaps_record = self.parse_vaps_line(vaps_line)
                self.concat_avg_peak_df(vaps_record)

                if count % PROGRESS_SKIPS == 0:
                    progress_bar.next()
                count += 1


    @staticmethod
    def parse_vaps_line(vaps_line):
        vaps_record = VapsTable(*[None]*26)

        try:
            # create time break date
            doy = int(vaps_line[117:120])
            year = seis_utils.get_year(doy)

            time_break = (datetime.datetime.strptime(datetime.datetime.strptime(
                str(year) + f'{doy:03}', '%Y%j').strftime('%d-%m-%y') + ' ' +  \
                    vaps_line[120:126] + '.' + vaps_line[144:147], '%d-%m-%y %H%M%S.%f'))
            time_break -= GMT_OFFSET

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
            vaps_record.file_id = 1

        except ValueError:
            vaps_record = VapsTable(*[None]*26)

        return vaps_record

    def concat_avg_peak_df(self, record):
        if not record:
            return

        vibrator = record.vibrator
        time_break = record.time_break
        avg_phase = record.avg_phase
        peak_phase = record.peak_phase
        avg_dist = record.avg_dist
        peak_dist = record.peak_dist
        avg_force = record.avg_force
        peak_force = record.peak_force

        attributes_row_df = pd.DataFrame(
            [[
                vibrator, time_break, avg_phase, peak_phase,
                avg_dist, peak_dist, avg_force, peak_force
            ]],
            columns=self._avg_peak_df.columns
        )

        self._avg_peak_df = pd.concat(
            [attributes_row_df, self._avg_peak_df], ignore_index=True
        )

if __name__ == '__main__':
    vaps_file = Path('./data_files/211006 - check VAPS/jd21263dpg.txt')
    vaps = Vaps(vaps_file)
    vaps.read_vaps()
    pprint(vaps.avg_peak_df)
