""" module to parse Extended QC files
"""
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import pandas as pd
from pprint import pprint


@dataclass
class ExtendedQcFields:
    source_line: int
    station_number: int
    source_index: int
    sweep_number: int
    serial_number: int
    vibrator_id: int
    crew_number: int
    fleet_number: int
    sweep_id: int
    shot_id: int
    sweep_counter: int
    sweep_type: str
    force: int
    gga_string: str
    gsa_string: str
    gst_string: str
    vtg_string: str
    zda_string: str
    ptnl_string: str
    time_break: datetime
    vss_file_number: int
    vss_sample_interval: int
    time_end_to_up: int
    pad_up_time: datetime
    pad_down_time: datetime
    time_up_to_down: int
    time_down_to_switch_on: int
    time_down_to_ready: int
    time_down_to_sweep: int
    sweep_checksum: str
    param_checksum: str
    qc_window: int
    attributes_df: pd.DataFrame


df_columns = [
    "time",
    "valid",
    "phase",
    "force",
    "dist",
    "visc",
    "stiff",
    "md",
    "vd",
    "tm",
    "peak_force",
    "rm_force",
    "freq",
    "target",
    "limit_t",
    "limit_m",
    "limit_v",
    "limit_f",
    "limit_r",
]


def get_int(val):
    try:
        return int(float(val))

    except ValueError:
        return -1


def get_datetime(val, fmt):
    try:
        return datetime.strptime(val.strip(), fmt)

    except ValueError:
        return None


def concat_df(df, val):
    df_column_vals = []
    try:
        val_list = val.split()
        df_column_vals.append(float(val_list[0]))
        df_column_vals[1:] = [int(el) for el in val_list[1:]]

    except ValueError:
        df_column_vals = [None] * len(df_columns)

    df = pd.concat(
        [df, pd.DataFrame([df_column_vals], columns=df_columns)], ignore_index=True
    )
    return df


def read_line_generator(filename):
    with open(filename, mode="rt") as file_handler:
        while True:
            line = file_handler.readline()
            if not line:
                break

            yield line


def parse_line(ext_qc, line):
    if matches := re.match(r"^(% VibProHD V24.14)\s*$", line):
        return ext_qc, "complete"

    elif matches := re.match(r"^% Source Line\s*:(.+)$", line):
        ext_qc.source_line = get_int(matches.group(1))

    elif matches := re.match(r"^% Station Number\s*:(.+)$", line):
        ext_qc.station_number = get_int(matches.group(1))

    elif matches := re.match(r"^% Source Index\s*:(.+)$", line):
        ext_qc.source_index = get_int(matches.group(1))

    elif matches := re.match(r"^% Sweep#\s*:(.+)$", line):
        ext_qc.sweep_number = get_int(matches.group(1))

    elif matches := re.match(r"^% Serial Number\s*:(.+)$", line):
        ext_qc.serial_number = get_int(matches.group(1))

    elif matches := re.match(r"^% Vibrator ID\s*:(.+)$", line):
        ext_qc.vibrator_id = get_int(matches.group(1))

    elif matches := re.match(r"^% Crew Number\s*:(.+)$", line):
        ext_qc.crew_number = get_int(matches.group(1))

    elif matches := re.match(r"^% Fleet Number\s*:(.+)$", line):
        ext_qc.fleet_number = get_int(matches.group(1))

    elif matches := re.match(r"^% Sweep ID\s*:(.+)$", line):
        ext_qc.sweep_id = get_int(matches.group(1))

    elif matches := re.match(r"^% Shot ID\s*:(.+)$", line):
        ext_qc.shot_id = get_int(matches.group(1))

    elif matches := re.match(r"^% SweepCounter\s*:(.+)$", line):
        ext_qc.sweep_counter = get_int(matches.group(1))

    elif matches := re.match(r"^% Sweep\s+Type\s*:(.+)$", line):
        ext_qc.sweep_type = matches.group(1).strip()

    elif matches := re.match(r"^% Force\s*:(.+)$", line):
        ext_qc.force = get_int(matches.group(1))

    elif matches := re.match(r"^% GGA\s*:(.+)$", line):
        ext_qc.gga_string = matches.group(1).strip()

    elif matches := re.match(r"^% GSA\s*:(.+)$", line):
        ext_qc.gsa_string = matches.group(1).strip()

    elif matches := re.match(r"^% GST\s*:(.+)$", line):
        ext_qc.gst_string = matches.group(1).strip()

    elif matches := re.match(r"^% VTG\s*:(.+)$", line):
        ext_qc.vtg_string = matches.group(1).strip()

    elif matches := re.match(r"^% ZDA\s*:(.+)$", line):
        ext_qc.zda_string = matches.group(1).strip()

    elif matches := re.match(r"^% PTNL\s*\(GGK\)\s*:(.+)$", line):
        ext_qc.ptnl_string = matches.group(1).strip()

    elif matches := re.match(r"^% Time Break\s*:(.+)\[.+$", line):
        ext_qc.time_break = get_datetime(matches.group(1), "%y/%m/%d %H:%M:%S.%f")

    elif matches := re.match(r"^% VSS File Number\s*:(.+)$", line):
        ext_qc.vss_file_number = get_int(matches.group(1))

    elif matches := re.match(r"^% VSS Sample Interval\s*:(.+)msec.*$", line):
        ext_qc.vss_sample_interval = get_int(matches.group(1))

    elif matches := re.match(r"^% time end of prev sweep to up\s*:(.+)ms.*$", line):
        ext_qc.time_end_to_up = get_int(matches.group(1))

    elif matches := re.match(r"^% pad up\s*:(.+)$", line):
        ext_qc.pad_up_time = get_datetime(matches.group(1), "%y/%m/%d %H:%M:%S.%f")

    elif matches := re.match(r"^% pad down\s*:(.+)$", line):
        ext_qc.pad_down_time = get_datetime(matches.group(1), "%y/%m/%d %H:%M:%S.%f")

    elif matches := re.match(r"^% time up to down\s*:(.+)ms.*$", line):
        ext_qc.time_up_to_down = get_int(matches.group(1))

    elif matches := re.match(r"^% time down to pressure switch ON\s*:(.+)ms.*$", line):
        ext_qc.time_down_to_switch_on = get_int(matches.group(1))

    elif matches := re.match(r"^% time down to ready\s*:(.+)ms.*$", line):
        ext_qc.time_down_to_ready = get_int(matches.group(1))

    elif matches := re.match(r"^% time down to sweep\s*:(.+)ms.*$", line):
        ext_qc.time_down_to_sweep = get_int(matches.group(1))

    elif matches := re.match(r"^% Sweep checksum\s*:(.+)$", line):
        ext_qc.sweep_checksum = matches.group(1).strip()

    elif matches := re.match(r"^% Param checksum\s*:(.+)$", line):
        ext_qc.param_checksum = matches.group(1).strip()

    elif matches := re.match(r"^% QC Window\s*:(.+)msec.*$", line):
        ext_qc.qc_window = get_int(matches.group(1))

    elif matches := re.match(r"^\d+\.\d(.+)$", line):
        ext_qc.attributes_df = concat_df(ext_qc.attributes_df, matches.group(0))

    return ext_qc, None


def extended_qc_generator(fn: Path) -> list:
    read_lines = read_line_generator(fn)
    ext_qc = ExtendedQcFields(*[None] * len(ExtendedQcFields.__annotations__))
    ext_qc.attributes_df = pd.DataFrame(columns=df_columns)
    for line in read_lines:
        ext_qc, status = parse_line(ext_qc, line)
        if status == "complete" and ext_qc.source_line:
            yield ext_qc
            ext_qc = ExtendedQcFields(*[None] * len(ExtendedQcFields.__annotations__))
            ext_qc.attributes_df = pd.DataFrame(columns=df_columns)

    yield ext_qc


if __name__ == "__main__":
    filename = Path("./data_files/230629_VIB08_test.txt")
    extended_qc_iterator = extended_qc_generator(filename)

    for i, extended_qc_record in enumerate(extended_qc_iterator):
        print(f"record: {i}:\n{extended_qc_record.attributes_df.loc[[0]]}")

    pprint(extended_qc_record)
