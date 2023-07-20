""" application to work with vibrator extended QC
"""
from pathlib import Path
import vp_extended_qc_parser as parser
from pprint import pprint


class VpExtendedQc:
    def __init__(self, filename):
        self.filename = filename

    def attributes_avg_peak(self):
        extended_qc_iterator = parser.extended_qc_generator(self.filename)
        for extended_qc_record in extended_qc_iterator:
            df = extended_qc_record.attributes_df
            avg_vals = df[2:].mean()
            peak_vals = df[2:].max()
            attributes_dict = {
                "vib": extended_qc_record.vibrator_id,
                "line": extended_qc_record.source_line,
                "station": extended_qc_record.station_number,
                "time_break": extended_qc_record.time_break,
                "start_time": df.iloc[2]["time"],
                "avg_phase": round(avg_vals["phase"]),
                "peak_phase": round(peak_vals["phase"]),
                "avg_dist": round(avg_vals["dist"]),
                "peak_dist": round(peak_vals["dist"]),
                "avg_force": round(avg_vals["force"]),
                "peak_force": round(peak_vals["force"]),
                "avg_target_force": round(avg_vals["target"]),
            }
            pprint(attributes_dict)
            input()


if __name__ == "__main__":
    extended_qc = VpExtendedQc(Path("./data_files/230629_VIB08_test.txt"))
    extended_qc.attributes_avg_peak()
