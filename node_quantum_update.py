"""Read noise test for Quantum nodes and store to database"""

from datetime import datetime
import dataclasses
import pandas as pd
import seis_utils
from seis_quantum_database import QuantumDb
from seis_settings import DATA_FILES_QUANTUM, FilesNodeTable, QuantumTable

PROGRESS_SKIPS = 200
node_db = QuantumDb()


class Rcv:
    @classmethod
    def read_nodes(cls):
        for filename in DATA_FILES_QUANTUM.glob("*.*"):
            if not filename.is_file() or filename.suffix.lower() != ".xlsx":
                continue

            node_file = FilesNodeTable(*[None] * 2)

            node_file.file_name = filename.name
            node_file.file_date = datetime.fromtimestamp(
                filename.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S")

            id_file = node_db.update_node_file(node_file)
            if id_file == -1:
                continue

            try:
                bits_df = pd.read_excel(filename)

            except PermissionError:
                node_db.delete_node_file(id_file)
                bits_df = pd.DataFrame()

            if bits_df.empty:
                continue

            # filter out duplicate tests on the same day and keep the last
            bits_df.sort_values(by=["Test Time"], inplace=True)
            bits_df["test_date"] = bits_df.apply(lambda x: x["Test Time"].date(), axis=1)
            bits_df = bits_df.drop_duplicates(
                subset=["Serial #", "test_date"], keep="last"
            )
            # sort on line and station
            bits_df.sort_values(
                by=["Deployment Line", "Deployment Station"], inplace=True
            )
            node_records = []

            progress_bar = seis_utils.set_progress_bar(
                bits_df.shape[0], filename.name, PROGRESS_SKIPS
            )

            count = 0
            for _, bits_row in bits_df.iterrows():
                node_record = cls.parse_node_line(bits_row)

                if node_record.qtm_sn:
                    node_record.id_file = id_file
                    node_records.append(node_record)

                if count % PROGRESS_SKIPS == 0:
                    progress_bar.next()
                count += 1

            if error_message := node_db.update_node_attributes_records(node_records):
                print(f"\n{error_message}")
                node_db.delete_node_file(id_file)

            progress_bar.finish()

    @staticmethod
    def parse_node_line(bits_row):
        empty_record = QuantumTable(*[None] * 26)
        node_record = QuantumTable(*[None] * 26)

        try:
            node_record.qtm_sn = bits_row["Serial #"]
            node_record.line = int(bits_row["Deployment Line"])
            node_record.station = int(bits_row["Deployment Station"])
            node_record.rcvr_index = 1
            node_record.software = bits_row["Software Version"]
            node_record.geoph_model = bits_row["Geophone Model"]
            node_record.test_time = bits_row["Test Time"].strftime("%Y-%m-%d %H:%M:%S")
            node_record.temp = (
                bits_row["Temperature"] if bits_row["Temperature"] > -30 else None
            )
            node_record.bits_type = bits_row["BITs Type"]
            node_record.tilt = bits_row["Tilt Angle"] if bits_row["Tilt Angle"] > 0 else None
            node_record.config_id = bits_row["Config ID"]
            node_record.resistance = (
                float(bits_row["Geophone Resistance, Ohms"])
                if bits_row["Geophone Resistance, Ohms"] > 0
                else None
            )
            node_record.noise = (
                bits_row["Sensor Noise, uV/µg"]
                if bits_row["Sensor Noise, uV/µg"] > 0
                else None
            )
            node_record.thd = (
                bits_row["Sensor THD, %"] if bits_row["Sensor THD, %"] > 0 else None
            )
            node_record.polarity = None
            node_record.frequency = (
                bits_row["Nat. Frequency"] if bits_row["Nat. Frequency"] > 0 else None
            )
            node_record.damping = (
                bits_row["Damping"] if bits_row["Damping"] > 0 else None
            )
            node_record.sensitivity = (
                bits_row["Sensitivity"] if bits_row["Sensitivity"] > 0 else None
            )
            node_record.dyn_range = bits_row["DR at Config Gain, dB"]
            node_record.ein = bits_row["EIN at Config Gain, uV"]
            node_record.gain = bits_row["Gain at Config Gain"]
            node_record.offset = bits_row["Offset at Config Gain, uV"]
            node_record.gps_time = int(bits_row["GPS Time"])
            node_record.ext_geophone = (
                1 if bits_row["Using External Geophone"] == "TRUE" else 0
            )

        except (ValueError, TypeError):
            return empty_record

        # only except records where there are numerical values for all of the below keys
        keys = [
            "tilt",
            "resistance",
            "noise",
            "thd",
            "frequency",
            "damping",
            "sensitivity",
        ]
        try:
            _ = sum(
                [v for k, v in dataclasses.asdict(node_record).items() if k in keys]
            )

        except TypeError:
            return empty_record

        if node_record.line > 99999:
            return empty_record

        return node_record


def main():
    node_db.create_table_node_files()
    node_db.create_table_node_attributes()

    rcv = Rcv()
    rcv.read_nodes()


if __name__ == "__main__":
    main()
