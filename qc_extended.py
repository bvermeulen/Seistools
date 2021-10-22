''' module to parse extended QC
'''
import re
import datetime
import pandas as pd
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ExtendedQcRecord:
    vibrator_id: int
    time_break: datetime.datetime
    attributes: pd.DataFrame


class ExtendedQc:
    record_start_token = '% VibProHD'
    record_end_token = '9.0'
    record_vibrator_id = '% Vibrator ID   '
    record_time_break = '% Time Break    '
    record_columns_header = [
        'sweep_time', 'valid', 'phase', 'force', 'dist', 'visc', 'stiff', 'md', 'vd',
        'tm', 'peak_force', 'rm_force', 'freq', 'target', 'limit_t', 'limit_m', 'limit_v',
        'limit_f', 'limit_r',
    ]
    record_avg_peak_header = [
        'vibrator', 'time_break', 'avg_phase', 'peak_phase', 'avg_dist', 'peak_dist',
        'avg_force', 'peak_force',
    ]

    def __init__(self, file_name):
        self.extended_qc_file = file_name
        self._extended_qc_records = []
        self._avg_peak_df = pd.DataFrame(columns=self.record_avg_peak_header)

    @property
    def extended_qc_records(self):
        return self._extended_qc_records

    @property
    def avg_peak_df(self):
        return self._avg_peak_df

    def read_extended_qc(self):
        with open(self.extended_qc_file, mode='rt') as extended_qc:
            while True:
                line = extended_qc.readline()
                if not line:
                    break

                elif line[0:10] == self.record_start_token:
                    raw_qc_record = []

                raw_qc_record.append(line.replace('\n',''))
                if line[0:3] == self.record_end_token:
                    extended_qc_record = self.parse_extended_qc(raw_qc_record)
                    self._extended_qc_records.append(extended_qc_record)
                    self.concat_avg_peak_df(extended_qc_record)

    def parse_extended_qc(self, raw_qc_record):
        extended_qc_record = ExtendedQcRecord(None, None, None)
        extended_qc_df = pd.DataFrame(columns=self.record_columns_header)

        for line in raw_qc_record:
            if line[0:16] == self.record_vibrator_id:
                extended_qc_record.vibrator_id = int(line[18:20])

            elif line[0:16] == self.record_time_break:
                extended_qc_record.time_break = (
                    datetime.datetime.strptime(
                        line[18:42],
                        '%y/%m/%d %H:%M:%S.%f'
                    )
                )
            elif sweep_time := re.match('\d.\d', line[0:3]):
                    attributes_row_df = pd.DataFrame(
                        [[float(sweep_time.group(0))] +
                         [int(val) for val in line[4:95].split()]],
                        columns=extended_qc_df.columns
                    )
                    extended_qc_df = pd.concat(
                        [attributes_row_df, extended_qc_df], ignore_index=True
                    )

        extended_qc_record.attributes = extended_qc_df
        return extended_qc_record

    def concat_avg_peak_df(self, record):
        avg_phase = record.attributes[record.attributes['valid'] == 1.0]['phase'].mean()
        peak_phase = record.attributes[record.attributes['valid'] == 1.0]['phase'].max()
        avg_dist = record.attributes[record.attributes['valid'] == 1.0]['dist'].mean()
        peak_dist = record.attributes[record.attributes['valid'] == 1.0]['dist'].max()
        avg_force = record.attributes[record.attributes['valid'] == 1.0]['force'].mean()
        peak_force = record.attributes[record.attributes['valid'] == 1.0]['force'].max()

        attributes_row_df = pd.DataFrame(
            [[
                record.vibrator_id, record.time_break, avg_phase, peak_phase,
                avg_dist, peak_dist, avg_force, peak_force
            ]],
            columns=self._avg_peak_df.columns
        )
        self._avg_peak_df = pd.concat(
            [attributes_row_df, self._avg_peak_df], ignore_index=True
        )
