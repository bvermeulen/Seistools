import os
from pathlib import Path
import pandas as pd
import numpy as np
from seis_utils import set_val
from ivms_settings import IVMS_FOLDER, DRIVER_TRAINING, IvmsDriver
from ivms_database import IvmsDb


class Driver:

    def __init__(self, db):
        self.db = db
        self.db.create_table_driver()

    def update_driver_rag(self):

        for foldername, _, filenames in os.walk(IVMS_FOLDER / 'RAG'):
            foldername = Path(foldername)
            for filename in filenames:
                if 'RAG Report' not in filename:
                    continue

                rag_df = pd.read_excel(foldername / filename, skiprows=7)

                driver_records = []
                for _, rag_row in rag_df.iterrows():
                    if driver_record := self.parse_driver(rag_row):
                        driver_records.append(driver_record)

                self.db.update_driver_records(driver_records)

    def update_driver_training(self):
        training_df = pd.read_excel(DRIVER_TRAINING, skiprows=2)
        driver_records = self.db.fetch_driver_records()

        new_driver_records = []
        for driver_record in driver_records:
            training_record = training_df[training_df['ivms_id'] == driver_record.ivms_id]
            if not training_record.empty:
                driver_record.contractor = set_val(
                    training_record['contractor'].values[0], 'str')
                driver_record.employee_no = set_val(
                    training_record['employee_no'].values[0], 'int')
                driver_record.name = set_val(
                    training_record['name'].values[0], 'str')
                driver_record.dob = set_val(
                    training_record['dob'].values[0], 'date')
                driver_record.mobile = set_val(
                    training_record['mobile'].values[0], 'str')
                driver_record.hse_passport = set_val(
                    training_record['hse_passport'].values[0], 'str')
                driver_record.ROP_license = set_val(
                    training_record['ROP_license'].values[0], 'str')
                driver_record.date_issue_license = set_val(
                    training_record['date_issue_license'].values[0], 'date')
                driver_record.date_expiry_license = set_val(
                    training_record['date_expiry_license'].values[0], 'date')
                driver_record.PDO_permit = set_val(
                    training_record['PDO_permit'].values[0], 'str')
                driver_record.date_expiry_permit = set_val(
                    training_record['date_expiry_permit'].values[0], 'date')

                driver_record.vehicle_light = set_val(
                    training_record['vehicle_light'].values[0], 'bool')

                driver_record.vehicle_heavy = set_val(
                    training_record['vehicle_heavy'].values[0], 'bool')

                driver_record.date_dd01 = set_val(
                    training_record['date_dd01'].values[0], 'date')
                driver_record.date_dd02 = set_val(
                    training_record['date_dd02'].values[0], 'date')
                driver_record.date_dd03 = set_val(
                    training_record['date_dd03'].values[0], 'date')
                driver_record.date_dd04 = set_val(
                    training_record['date_dd04'].values[0], 'date')
                driver_record.date_dd05 = set_val(
                    training_record['date_dd05'].values[0], 'date')
                driver_record.date_dd06 = set_val(
                    training_record['date_dd06'].values[0], 'date')
                driver_record.date_dd06_due = set_val(
                    training_record['date_dd06_due'].values[0], 'date')
                driver_record.date_assessment_day = set_val(
                    training_record['date_assessment_day'].values[0], 'date')
                driver_record.date_assessment_night = set_val(
                    training_record['date_assessment_night'].values[0], 'date')
                driver_record.date_assessment_rough = set_val(
                    training_record['date_assessment_rough'].values[0], 'date')
                driver_record.assessment_comment = set_val(
                    training_record['assessment_comment'].values[0], 'str')
                driver_record.training_comment = set_val(
                    training_record['training_comment'].values[0], 'str')

                new_driver_records.append(driver_record)

        self.db.update_driver_records(new_driver_records)

    @staticmethod
    def parse_driver(rag_df):
        driver_record = IvmsDriver()
        try:
            driver_record.name = str(rag_df['Driver Name'])[:50]
            driver_record.ivms_id = int(rag_df['Driver ID'])
            driver_record.site_name = str(rag_df['Site Name'])[:30]

        except ValueError:
            return None

        if driver_record.ivms_id:
            return driver_record

        else:
            return None


if __name__ == '__main__':
    db = IvmsDb()

    driver = Driver(IvmsDb())
    driver.update_driver_rag()
    driver.update_driver_training()


