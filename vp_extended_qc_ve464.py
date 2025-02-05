""" application to work with vibrator extended QC
"""
from pathlib import Path
import pandas as pd
from seis_settings import GMT_OFFSET
from seis_utils import progress_message_generator
from seis_vibe_database import VpDb
import vp_extended_qc_parser_ve464 as parser


qc_columns= [
    "line",
    "station",
    "vibrator",
    "avg_phase",
    "peak_phase",
    "avg_dist",
    "peak_dist",
    "avg_force",
    "peak_force",
    "avg_visc",
    "peak_visc",
    "avg_stiff",
    "peak_stiff",
    "limit_f",
    "limit_p",
    "limit_m",
    "limit_v",
    "limit_e",
    "easting",
    "northing",
    "elevation",
    "start_time",
    "start_visc",
    "time_break",
]

class VpExtendedQc:
    def __init__(self, filename: Path):
        self.filename = filename
        self.vaps_df = None

    def get_location(self, production_date, vibrator_id, time_break):
        if self.vaps_df is None:
            self.vaps_df = VpDb().get_vp_data_by_date("VAPS", production_date)
            self.vaps_df["time_break"] = pd.to_datetime(
                self.vaps_df["time_break"], format="ISO8601"
            )
        try:
            easting, northing, elevation = self.vaps_df[
                (self.vaps_df["time_break"] == time_break)
                & (self.vaps_df["vibrator"] == vibrator_id)
            ][["easting", "northing", "elevation"]].values[0]
        except IndexError:
            easting, northing, elevation = -1, -1, -1

        return easting, northing, elevation

    def vp_attributes(self, location: bool = False) -> None:
        extended_qc_iterator = parser.extended_qc_generator(self.filename)
        attributes_df = pd.DataFrame(columns=qc_columns)
        progress_message = progress_message_generator(
            f"processing extended qc for {self.filename}"
        )
        self.vaps_df = None
        for extended_qc_record in extended_qc_iterator:
            start_time_index = extended_qc_record.time_inhibit - 1
            start_visc_index = extended_qc_record.time_inhibit - 1
            ext_qc_df = extended_qc_record.attributes_df
            avg_vals = ext_qc_df[start_time_index :][
                ["phase", "dist", "force"]
            ].mean()
            peak_vals = ext_qc_df[start_time_index :][
                ["phase", "dist", "force"]
            ].max()
            avg_visc = ext_qc_df[start_visc_index :][["visc", "stiff"]].mean()
            peak_visc = ext_qc_df[start_visc_index :][["visc", "stiff"]].max()
            count_limits = ext_qc_df[start_time_index :][
                ["limit_f", "limit_p", "limit_m", "limit_v", "limit_e"]
            ].sum()
            production_date = (extended_qc_record.time_break + GMT_OFFSET).date()
            vibrator_id = extended_qc_record.fleet_number
            tb_ext_qc = extended_qc_record.time_break
            tb_vaps = tb_ext_qc + GMT_OFFSET
            easting, northing, elevation = (
                self.get_location(production_date, vibrator_id, tb_vaps)
                if location
                else (-1, -1, -1)
            )
            attributes_list = [
                extended_qc_record.source_line,
                extended_qc_record.station_number,
                extended_qc_record.fleet_number,
                round(avg_vals["phase"]),
                round(peak_vals["phase"]),
                round(avg_vals["dist"]),
                round(peak_vals["dist"]),
                round(avg_vals["force"]),
                round(peak_vals["force"]),
                round(avg_visc["visc"]),
                round(peak_visc["visc"]),
                round(avg_visc["stiff"]),
                round(peak_visc["stiff"]),
                count_limits["limit_f"],
                count_limits["limit_p"],
                count_limits["limit_m"],
                count_limits["limit_v"],
                count_limits["limit_e"],
                easting,
                northing,
                elevation,
                ext_qc_df.iloc[start_time_index]["time"],
                ext_qc_df.iloc[start_visc_index]["time"],
                tb_ext_qc,
            ]
            attributes_df = pd.concat(
                [
                    attributes_df,
                    pd.DataFrame([attributes_list], columns=qc_columns),
                ],
                ignore_index=True,
            )
            next(progress_message)

        csv_file = self.filename.parent / "".join([self.filename.stem, ".csv"])
        print(attributes_df)
        attributes_df.to_csv(csv_file, date_format="%Y-%m-%d %H:%M:%S.%f", index=False)


if __name__ == "__main__":
    filename = Path("./data_files/dsd05_250202.txt")
    extended_qc = VpExtendedQc(filename)
    extended_qc.vp_attributes(location=False)
