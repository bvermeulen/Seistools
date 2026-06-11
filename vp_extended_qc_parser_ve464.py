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
    stack_number: int
    fleet_number: int
    dsd_number: int
    sweep_counter: int
    sweep_type: str
    sweep_status: int
    drive: int
    gps_status: str
    time_break: datetime
    qc_type: str
    servo_setup: str
    time_inhibit: int
    time_end_to_up: int
    pad_up_time: datetime
    pad_down_time: datetime
    time_up_to_down: int
    time_down_to_switch_on: int
    time_down_to_ready: int
    time_down_to_sweep: int
    sweep_length: int
    attributes_df: pd.DataFrame


qc_columns = [
    "time",
    "phase",
    "force",
    "dist",
    "visc",
    "stiff",
    "m1",
    "m2",
    "m3",
    "p1",
    "p2",
    "p3",
    "b1",
    "b2",
    "b3",
    "b4",
    "b5",
    "b6",
    "limit_f",
    "limit_p",
    "limit_m",
    "limit_v",
    "limit_e",
]


def get_float(val):
    try:
        return float(val)

    except ValueError:
        return -1


def get_int(val):
    return int(get_float(val))


def get_datetime(val, fmt):
    try:
        return datetime.strptime(val.strip(), fmt)

    except ValueError:
        return None


def concat_df(df, val):
    qc_column_vals = []
    try:
        val_list = val.split()
        qc_column_vals.append(float(val_list[0]))
        qc_column_vals[1:] = [int(el) for el in val_list[1:]]

    except ValueError:
        qc_column_vals = [None] * len(qc_columns)

    qc_df = pd.DataFrame([qc_column_vals], columns=qc_columns)

    if df.empty:
        df = qc_df

    else:
        df = pd.concat([df, qc_df], ignore_index=True)
    return df


def read_line_generator(filename):
    with open(filename, mode="rt") as file_handler:
        while True:
            line = file_handler.readline()
            if not line:
                break

            yield line


def parse_line(ext_qc, line):
    if matches := re.match(r"^(% VE464 V3.0.12)\s*$", line):
        return ext_qc, "complete"

    elif matches := re.match(r"^% SL\s*:(.+)$", line):
        ext_qc.source_line = get_float(matches.group(1))

    elif matches := re.match(r"^% SN\s*:(.+)$", line):
        ext_qc.station_number = get_float(matches.group(1))

    elif matches := re.match(r"^% SI\s*:(.+)$", line):
        ext_qc.source_index = get_int(matches.group(1))

    elif matches := re.match(r"^% StackNb\s*:(.+)$", line):
        ext_qc.stack_number = get_int(matches.group(1))

    elif matches := re.match(r"^% FleetNb\s*:(.+)$", line):
        ext_qc.fleet_number = get_int(matches.group(1))

    elif matches := re.match(r"^% DsdNb\s*:(.+)$", line):
        ext_qc.dsd_number = get_int(matches.group(1))

    elif matches := re.match(r"^% SweepCounter\s*:(.+)$", line):
        ext_qc.sweep_counter = get_int(matches.group(1))

    elif matches := re.match(r"^% Sweep  Type\s*:(.+)$", line):
        ext_qc.sweep_type = matches.group(1).strip()

    elif matches := re.match(r"^% Sweep Status\s*:(.+)$", line):
        ext_qc.sweep_status = get_int(matches.group(1))

    elif matches := re.match(r"^% Drive\s*:(.+)$", line):
        ext_qc.drive = get_int(matches.group(1))

    elif matches := re.match(r"^% Gps Status\s*:(.+)$", line):
        ext_qc.gps_status = matches.group(1).strip()

    elif matches := re.match(r"^% TB\s*:(.+)\[.+$", line):
        ext_qc.time_break = get_datetime(matches.group(1), "%y/%m/%d %H:%M:%S:%f")

    elif matches := re.match(r"^% QC type\s*:(.+)$", line):
        ext_qc.qc_type = matches.group(1)

    elif matches := re.match(r"^% SERVO Setup\s*:(.+)$", line):
        ext_qc.servo_setup = matches.group(1).strip()

    elif matches := re.match(r"^% Time Inhibit\s*:(.+)$", line):
        ext_qc.time_inhibit = get_int(matches.group(1))

    elif matches := re.match(r"^% time end of prev sweep to up\s*:(.+)ms.*$", line):
        ext_qc.time_end_to_up = get_float(matches.group(1))

    elif matches := re.match(r"^% pad up\s*:(.+)$", line):
        ext_qc.pad_up_time = get_datetime(matches.group(1), "%y/%m/%d %H:%M:%S:%f")

    elif matches := re.match(r"^% pad down\s*:(.+)$", line):
        ext_qc.pad_down_time = get_datetime(matches.group(1), "%y/%m/%d %H:%M:%S:%f")

    elif matches := re.match(r"^% time up to down\s*:(.+)ms.*$", line):
        ext_qc.time_up_to_down = get_float(matches.group(1))

    elif matches := re.match(r"^% time down to pressure switch ON\s*:(.+)ms.*$", line):
        ext_qc.time_down_to_switch_on = get_float(matches.group(1))

    elif matches := re.match(r"^% time down to ready\s*:(.+)ms.*$", line):
        ext_qc.time_down_to_ready = get_float(matches.group(1))

    elif matches := re.match(r"^% time down to sweep\s*:(.+)ms.*$", line):
        ext_qc.time_down_to_sweep = get_float(matches.group(1))

    elif matches := re.match(r"^% sweep length\s*:(.+)ms.*$", line):
        ext_qc.sweep_length = get_int(matches.group(1))

    elif matches := re.match(r"^\d+\.\d(.+)$", line):
        ext_qc.attributes_df = concat_df(ext_qc.attributes_df, matches.group(0))

    return ext_qc, None


def extended_qc_generator(fn: Path):
    read_lines = read_line_generator(fn)
    ext_qc = ExtendedQcFields(*[None] * len(ExtendedQcFields.__annotations__))
    ext_qc.attributes_df = pd.DataFrame(columns=qc_columns)
    for line in read_lines:
        ext_qc, status = parse_line(ext_qc, line)
        if status == "complete" and ext_qc.sweep_length:
            yield ext_qc
            ext_qc = ExtendedQcFields(*[None] * len(ExtendedQcFields.__annotations__))
            ext_qc.attributes_df = pd.DataFrame(columns=qc_columns)

    yield ext_qc


if __name__ == "__main__":
    filename = Path("./data_files/Addaimah/dsd08_260609.txt")
    extended_qc_iterator = extended_qc_generator(filename)

    for i, extended_qc_record in enumerate(extended_qc_iterator):
        pprint(extended_qc_record)
        ...
