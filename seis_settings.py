"""settings and data structures for vp app"""

import os
import json
import datetime
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

match os.name:
    case "nt":
        seis_config_file = (
            Path.home() / "AppData/Roaming/SeistoolsConfig" / "seis_config.json"
        )
    case "posix":
        seis_config_file = Path.home() / ".config/SeistoolsConfig" / "seis_config.json"
    case other:
        assert False, f"{os.name} is not implemented"

with open(seis_config_file, "rt") as json_file:
    seis_config = json.load(json_file)

files = seis_config["file_paths"]
PROJECT_PATH = Path(files["PROJECT_PATH"])
DATA_FILES_VP = (
    PROJECT_PATH / files["DATA_FILES_VP"] if files["DATA_FILES_VP"] else None
)
DATA_FILES_VAPS = (
    PROJECT_PATH / files["DATA_FILES_VAPS"] if files["DATA_FILES_VAPS"] else None
)
DATA_FILES_QUANTUM = (
    PROJECT_PATH / files["DATA_FILES_QUANTUM"] if files["DATA_FILES_QUANTUM"] else None
)
DATA_FILES_NUSEIS = (
    PROJECT_PATH / files["DATA_FILES_NUSEIS"] if files["DATA_FILES_NUSEIS"] else None
)
DATA_FILES_SPS = (
    PROJECT_PATH / files["DATA_FILES_SPS"] if files["DATA_FILES_SPS"] else None
)
DATA_FILES_WEATHER = (
    PROJECT_PATH / files["DATA_FILES_WEATHER"] if files["DATA_FILES_WEATHER"] else None
)
RESULTS_FOLDER = (
    PROJECT_PATH / files["RESULTS_FOLDER"] if files["RESULTS_FOLDER"] else None
)
DATABASE = PROJECT_PATH / files["DATABASE"]
PLOT_RESULTS = PROJECT_PATH / files["PLOT_RESULTS"]

VIBRATORS = seis_config["general"]["VIBRATORS"]
SWEEP_TIME = seis_config["general"]["SWEEP_TIME"]
PAD_DOWN_TIME = seis_config["general"]["PAD_DOWN_TIME"]
# if distance < DENSE_CRITERIUM then dense_flag is true
DENSE_CRITERIUM = seis_config["general"]["DENSE_CRITERIUM"]
GMT_OFFSET = seis_config["general"]["GMT_OFFSET"]
EPSG_PROJECT = seis_config["general"]["EPSG"]
REMOVE_DUPLICATES = seis_config["general"]["REMOVE_DUPLICATES"]

EXPIRY_DATE = datetime.date(2026, 8, 31)
LINK_VP_TO_VAPS = False
DATABASE_TABLE = "VAPS"
PROGRESS_SKIPS = 750
GMT_OFFSET = datetime.timedelta(hours=+GMT_OFFSET)
GPS_TIME_OFFSET = 315964782
MARKERSIZE_VP = 0.2
MARKERSIZE_NODE = 1.0
TOL_COLOR = "red"

vp_plt_settings = seis_config["vp_plt_settings"]
node_plt_settings = seis_config["node_plt_settings"]

if vp_plt_settings["vib_activity"]["activity_type"] == "EP":
    FLEETS = vp_plt_settings["vib_activity"]["fleets"]

else:
    FLEETS = VIBRATORS

NUMBER_VP_TYPES = seis_config["general"]["NUMBER_VP_TYPES"]


# type is (number of sweeps, number of vibrators, drive level)

vp_types = {
    f"V{i+1}": tuple(seis_config["general"][f"V{i+1}"])
    for i in range(NUMBER_VP_TYPES)
}
VpType = Enum("VpType", vp_types)

@dataclass
class FilesNodeTable:
    file_name: str
    file_date: datetime.datetime


@dataclass
class QuantumTable:
    line: int
    station: int
    rcvr_index: int
    id_file: int
    id_point: int
    qtm_sn: str
    software: str
    geoph_model: str
    test_time: datetime.datetime
    temp: float
    bat_charge: float
    project_id: int
    config_id: int
    bits_type: str
    tilt: float
    resistance: float
    noise: float
    thd: float
    polarity: str
    frequency: float
    damping: float
    sensitivity: float
    gain: float
    sample_rate: str
    ein_at_gain: float
    dr_at_gain: float
    gain_at_gain: float
    offset_at_gain: float
    gps_time: int
    ext_geophone: bool
    result: str
    result_descr: str


@dataclass
class NuseisTable:
    line: int
    station: int
    rcvr_index: int
    id_file: int
    id_point: int
    nuseis_sn: int
    tilt: float
    noise: float
    resistance: float
    impedance: float
    thd: float
    time_deployment: datetime.datetime
    time_lastscan: datetime.datetime


@dataclass
class RcvrTable:
    line: int
    station: int
    rcvr_index: int
    easting: float
    northing: float
    elevation: float


@dataclass
class FilesVpTable:
    id: int
    file_name: str
    file_date: datetime.datetime


@dataclass
class VpTable:
    id: int
    file_id: int
    vaps_id: int
    line: int
    station: int
    vibrator: int
    time_break: datetime.datetime
    planned_easting: float
    planned_northing: float
    easting: float
    northing: float
    elevation: float
    offset: float
    peak_force: int
    avg_force: int
    peak_dist: int
    avg_dist: int
    peak_phase: int
    avg_phase: int
    qc_flag: str
    distance: float
    time: float
    velocity: float
    dense_flag: bool


@dataclass
class FilesVapsTable:
    id: int
    file_name: str
    file_date: datetime.datetime


@dataclass
class VapsTable:
    id: int
    file_id: int
    line: int
    station: int
    fleet_nr: str
    vibrator: int
    drive: int
    avg_phase: int
    peak_phase: int
    avg_dist: int
    peak_dist: int
    avg_force: int
    peak_force: int
    avg_stiffness: int
    avg_viscosity: int
    easting: float
    northing: float
    elevation: float
    time_break: datetime.datetime
    hdop: float
    tb_date: str
    positioning: str
    distance: float
    time: float
    velocity: float
    dense_flag: bool


@dataclass
class FilesSpsTable:
    id: int
    file_name: str
    file_date: datetime.datetime
    block_name: str


@dataclass
class SpsTable:
    id: int
    file_id: int
    sps_type: str
    line: int
    point: int
    point_index: int
    source_type: str
    easting: float
    northing: float
    elevation: float
    dpg_filename: str
    time_break: datetime.datetime
    vibrator: int


@dataclass
class FilesWeatherTable:
    id: int
    file_name: str
    file_date: datetime.datetime


@dataclass
class WeatherTable:
    id: int
    file_id: int
    date_time: datetime.datetime
    wind_speed: float
    wind_gust: float
    pulse_count: int
    counter_value: int
    input_voltage: float
    temperature: float
