""" application to work with vibrator extended QC
"""
from pathlib import Path
import datetime
import pandas as pd
import vp_extended_qc_parser as parser
from seis_vibe_database import VpDb
from seis_settings import GMT_OFFSET


class VpExtendedQc:
    def __init__(self, filename):
        self.filename = filename
        self.vaps_df = None

    def get_location(self, production_date, vibrator_id, time_break):
        if self.vaps_df is None:
            self.vaps_df = VpDb().get_vp_data_by_date("VAPS", production_date)
            self.vaps_df["time_break"] = pd.to_datetime(
                self.vaps_df["time_break"], format="ISO8601"
            )
        try:
            s_line, s_point = self.vaps_df[
                (self.vaps_df["time_break"] == time_break)
                & (self.vaps_df["vibrator"] == vibrator_id)
            ][["line", "point"]].values[0]
        except IndexError:
            s_line, s_point = -1, -1

        return s_line, s_point

    def vp_attributes(self, location=False):
        extended_qc_iterator = parser.extended_qc_generator(self.filename)
        vaps_df = None
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
            "avg_target_foce",
            "start_time",
            "time_break",
        ]
        attributes_df = pd.DataFrame(columns=columns_attributes_df)
        self.vaps_df = None
        for extended_qc_record in extended_qc_iterator:
            production_date = (extended_qc_record.time_break + GMT_OFFSET).date()
            ext_qc_df = extended_qc_record.attributes_df
            avg_vals = ext_qc_df[2:].mean()
            peak_vals = ext_qc_df[2:].max()
            tb_ext_qc = extended_qc_record.time_break
            tb_vaps = tb_ext_qc + GMT_OFFSET
            vibrator_id = extended_qc_record.vibrator_id
            s_line, s_point = (
                self.get_location(production_date, vibrator_id, tb_vaps)
                if location
                else (-1, -1)
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
                ext_qc_df.iloc[2]["time"],
                tb_ext_qc,
            ]
            attributes_df = pd.concat(
                [
                    attributes_df,
                    pd.DataFrame([attributes_list], columns=columns_attributes_df),
                ],
                ignore_index=True,
            )

        print(attributes_df)


if __name__ == "__main__":
    extended_qc = VpExtendedQc(Path("./data_files/230629_VIB08_test.txt"))
    extended_qc.vp_attributes(location=True)
