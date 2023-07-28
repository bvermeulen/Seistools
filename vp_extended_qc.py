""" application to work with vibrator extended QC
"""
from pathlib import Path
import pandas as pd
from seis_settings import GMT_OFFSET
from seis_utils import progress_message_generator
from seis_vibe_database import VpDb
import vp_extended_qc_parser as parser


# TODO calculation stiffness and viscosity only from linear part of sweep sample 9 (4.5 seconds); linear part starts at 4 seconds (sample 8)


class VpExtendedQc:
    def __init__(self, filename: Path):
        self.filename = filename
        self.vaps_df = None
        self.start_time_index = 3

    def get_location(self, production_date, vibrator_id, time_break):
        if self.vaps_df is None:
            self.vaps_df = VpDb().get_vp_data_by_date("VAPS", production_date)
            self.vaps_df["time_break"] = pd.to_datetime(
                self.vaps_df["time_break"], format="ISO8601"
            )
        try:
            s_line, s_point, easting, northing, elevation = self.vaps_df[
                (self.vaps_df["time_break"] == time_break)
                & (self.vaps_df["vibrator"] == vibrator_id)
            ][["line", "point", "easting", "northing", "elevation"]].values[0]
        except IndexError:
            s_line, s_point, easting, northing, elevation = -1, -1, -1, -1, -1

        return s_line, s_point, easting, northing, elevation

    def vp_attributes(self, location: bool = False) -> None:
        extended_qc_iterator = parser.extended_qc_generator(self.filename)
        columns_attributes_df = [
            "line",
            "station",
            "vibrator",
            "avg_phase",
            "peak_phase",
            "avg_dist",
            "peak_dist",
            "avg_force",
            "peak_force",
            "avg_target_force",
            "limit_t",
            "limit_m",
            "limit_v",
            "limit_f",
            "limit_r",
            "easting",
            "northing",
            "elevation",
            "start_time",
            "time_break",
        ]
        attributes_df = pd.DataFrame(columns=columns_attributes_df)
        progress_message = progress_message_generator(
            f"processing extended qc for {self.filename}"
        )
        self.vaps_df = None
        for extended_qc_record in extended_qc_iterator:
            ext_qc_df = extended_qc_record.attributes_df
            avg_vals = ext_qc_df[self.start_time_index :].mean()
            peak_vals = ext_qc_df[self.start_time_index :].max()
            count_limits = ext_qc_df[self.start_time_index :][
                ["limit_t", "limit_m", "limit_v", "limit_f", "limit_r"]
            ].sum()
            production_date = (extended_qc_record.time_break + GMT_OFFSET).date()
            vibrator_id = extended_qc_record.vibrator_id
            tb_ext_qc = extended_qc_record.time_break
            tb_vaps = tb_ext_qc + GMT_OFFSET
            s_line, s_point, easting, northing, elevation = (
                self.get_location(production_date, vibrator_id, tb_vaps)
                if location
                else (-1, -1, -1, -1, -1)
            )
            attributes_list = [
                s_line,
                s_point,
                vibrator_id,
                round(avg_vals["phase"]),
                round(peak_vals["phase"]),
                round(avg_vals["dist"]),
                round(peak_vals["dist"]),
                round(avg_vals["force"]),
                round(peak_vals["force"]),
                round(avg_vals["target"]),
                count_limits["limit_t"],
                count_limits["limit_m"],
                count_limits["limit_v"],
                count_limits["limit_f"],
                count_limits["limit_r"],
                easting,
                northing,
                elevation,
                ext_qc_df.iloc[self.start_time_index]["time"],
                tb_ext_qc,
            ]
            attributes_df = pd.concat(
                [
                    attributes_df,
                    pd.DataFrame([attributes_list], columns=columns_attributes_df),
                ],
                ignore_index=True,
            )
            next(progress_message)

        csv_file = self.filename.parent / "".join([self.filename.stem, ".csv"])
        print(attributes_df)
        attributes_df.to_csv(csv_file, date_format="%Y-%m-%d %H:%M:%S.%f")


if __name__ == "__main__":
    extended_qc = VpExtendedQc(Path("./data_files/230629_VIB08.txt"))
    extended_qc.vp_attributes(location=True)
