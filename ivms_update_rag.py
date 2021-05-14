import os
import re
import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from  seis_utils import progress_message_generator, set_val
from ivms_settings import IVMS_FOLDER, IvmsFileRag, IvmsRag
from ivms_database import IvmsDb

pattern = re.compile(
    r'^.*\n.*\n\n.*From\s+'
    r'(?P<date1>\d\d/\d\d/\d\d\d\d)\s+To\s+(?P<date2>\d\d/\d\d/\d\d\d\d)'
)

class Rag:

    def __init__(self, db):
        self.db = db
        self.db.create_table_rag_files()
        self.db.create_table_rag()

    def update_rag(self):

        for foldername, _, filenames in os.walk(IVMS_FOLDER / 'RAG'):
            foldername = Path(foldername)
            for filename in filenames:
                if 'RAG Report' not in filename:
                    continue

                abs_filename = foldername / filename
                rag_file = IvmsFileRag()
                rag_file.filename = filename
                rag_file.file_date = (
                    datetime.datetime.fromtimestamp(os.stat(abs_filename).st_mtime)
                )
                file_id = self.db.update_rag_file(rag_file)

                if file_id == -1:
                    continue

                header_data = pd.read_excel(
                    abs_filename, usecols='A', header=0, nrows=0).columns.values[0]
                report_date = datetime.datetime.strptime(
                    pattern.match(header_data).group('date1'), '%d/%m/%Y').date()

                rag_df = pd.read_excel(abs_filename, skiprows=7)

                rag_records = []
                for _, rag_row in rag_df.iterrows():
                    if rag_record := self.parse_rag(rag_row):
                        if set_val(rag_row['Driver Name'], 'str') == 'Totals':
                            break
                        rag_record.rag_report = set_val(report_date, 'date')
                        rag_record.id_file = set_val(file_id, 'int')
                        rag_records.append(rag_record)

                if rag_records:
                    self.db.update_rag_records(rag_records)

    @staticmethod
    def parse_rag(rag_df):
        rag_record = IvmsRag()
        try:
            rag_record.id_driver = set_val(
                rag_df['Driver ID'], 'int')
            rag_record.distance = set_val(
                rag_df['Distance (km)'], 'float')
            rag_record.driving_time = set_val(
                rag_df['Driving Time'], 'time')
            rag_record.harsh_accel = set_val(
                rag_df['Harsh Accel Occurrences'], 'int')
            rag_record.harsh_brake = set_val(
                rag_df['Harsh Brake Occurrences'], 'int')
            rag_record.highest_speed = set_val(
                rag_df['Highest Speed (km/h)'], 'float')
            rag_record.overspeeding_time = set_val(
                rag_df['Overspeeding Time'], 'time')
            rag_record.seatbelt_violation_time = set_val(
                rag_df['Seatbelt Violation Time'], 'time')
            rag_record.accel_violation_score = set_val(
                rag_df['Acceleration Violation Score'], 'float')
            rag_record.decel_violation_score = set_val(
                rag_df['Deceleration Violation Score'], 'float')
            rag_record.seatbelt_violation_score = set_val(
                rag_df['Seatbelt Violation Score'], 'float')
            rag_record.overspeeding_violation_score = set_val(
                rag_df['Overspeeding Violation Score'], 'float')
            rag_record.total_score = set_val(rag_df['Total Score'], 'float')

        except ValueError:
            return None

        if rag_record.id_driver:
            return rag_record

        else:
            return None


if __name__ == '__main__':
    rag = Rag(IvmsDb())
    rag.update_rag()
