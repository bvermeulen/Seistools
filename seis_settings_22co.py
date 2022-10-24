''' settings and data structures for vp app
'''
import dataclasses
import datetime
from dataclasses import dataclass
from pathlib import Path
from enum import IntEnum

DATA_FILES_VP =       Path('D:/OneDrive/Work/PDO/Lekhwair 3D/VP data/VP_RECORD')
DATA_FILES_VAPS =     Path('D:/OneDrive/Work/PDO/Central Oman 2022/12 QC/vib_node_data/vaps')
DATA_FILES_QUANTUM =  Path('D:/OneDrive/Work/PDO/Central Oman 2022/12 QC/vib_node_data//quantum_nodes')
DATA_FILES_NUSEIS =   Path('D:/OneDrive/Work/PDO/Central Oman 2022/12 QC/vib_node_data/nuseis_nodes')
DATA_FILES_SPS =      Path('D:/OneDrive/Work/PDO/Central Oman 2022/12 QC/vib_node_data/sps_final')
RESULTS_FOLDER =      Path('D:/OneDrive/Work/PDO/Central Oman 2022/5 Financials/4 Less Vibs Penalty/Daily vibe activity')
DATABASE =            Path('D:/OneDrive/Work/PDO/Central Oman 2022/6 Mapping/central_oman_db.sqlite3')

LINK_VP_TO_VAPS = False
DATABASE_TABLE = 'VAPS'
PROGRESS_SKIPS = 750
GMT_OFFSET = datetime.timedelta(hours=+4)
DENSE_CRITERIUM = 15  # if distance < DENSE_CRITERIUM then dense_flag is true
SWEEP_TIME = 9
PAD_DOWN_TIME = 2.5

FLEETS = 15
MARKERSIZE_VP = 0.2
MARKERSIZE_NODE = 1.0
TOL_COLOR = 'red'
AREA_EASTING_MIN = 610_000
AREA_EASTING_MAX = 760_000
AREA_NORTHING_MIN = 2_345_000
AREA_NORHING_MAX = 2_455_000

URL_STAMEN = 'http://tile.stamen.com/terrain/{z}/{x}/{y}.png'
MAP_FILE = r'BackgroundMap/3D_31256.jpg'
EPSG_UTM_40N = 32640
EPSG_WGS84 = 4326
EPSG_OSM = 3857
EPSG_PSD93 = 3440

class MapTypes(IntEnum):
    local = 0
    osm = 1
    no_background = 3

vp_plt_settings = {
    'avg_phase': {
        'title_attribute': 'Average Phase',
        'y-axis_label_attribute': 'Degrees',
        'title_density': 'Average Phase Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 15,
        'interval': 0.1,
        'tol_min': None,
        'tol_max': 4,
    },
    'avg_dist': {
        'title_attribute': 'Average Distortion',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Average Distortion Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 80,
        'interval': 1,
        'tol_min': None,
        'tol_max': 25,
    },
    'avg_force': {
        'title_attribute': 'Average Force',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Average Force Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'interval': 1,
        'tol_min': None,
        'tol_max': 61,
    },
    'peak_phase': {
        'title_attribute': 'Peak Phase',
        'y-axis_label_attribute': 'Degrees',
        'title_density': 'Peak Phase Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 30,
        'interval': 0.1,
        'tol_min': None,
        'tol_max': 8,
    },
    'peak_dist': {
        'title_attribute': 'Peak Distortion',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Peak Distortion Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'interval': 1,
        'tol_min': None,
        'tol_max': 35,
    },
    'peak_force': {
        'title_attribute': 'Peak Force',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Peak Force Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'interval': 1,
        'tol_min': None,
        'tol_max': 85,
    },
    'elevation': {
        'title_attribute': 'Elevation',
        'y-axis_label_attribute': 'meters',
        'title_density': 'Elevation density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 200,
        'interval': 1,
    },
    'avg_stiffness': {
        'title_attribute': 'Stiffness',
        'y-axis_label_attribute': 'Level',
        'title_density': 'Stiffness density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 50,
        'interval': 1,
    },
    'avg_viscosity': {
        'title_attribute': 'Viscosity',
        'y-axis_label_attribute': 'Level',
        'title_density': 'Viscosity density',
        'y-axis_label_density': '',
        'min': 15,
        'max': 25,
        'interval': 1,
    },
    'none': {
        'title_attribute': '',
        'y-axis_label_attribute': '',
        'title_density': '',
        'y-axis_label_density': '',
        'min': 0,
        'max': 0,
        'interval': 0,
    },
    'vib_activity': {
        'fig_title': 'Vibrator activity: ',
        'max_vp_hour': 1800,
        'tick_intval_vp_hour': 100,
        'vp_hour_target': 900,
        'max_vibs': 15,
        'tick_intval_vibs': 1,
        'vibs_target': 0,
    },
}
node_plt_settings = {
    'frequency': {
        'title_attribute': 'Natural Frequency',
        'y-axis_label_attribute': 'Hz',
        'title_density': 'Natural Frequency',
        'y-axis_label_density': '',
        'min': 3,
        'max': 7,
        'interval': 0.01,
        'tol_min': 4.6,
        'tol_max': 5.4,
    },
    'damping': {
        'title_attribute': 'Damping',
        'y-axis_label_attribute': '%',
        'title_density': 'Damping',
        'y-axis_label_density': '',
        'min': 0.50,
        'max': 0.70,
        'interval': 0.01,
        'tol_min': 0.552,
        'tol_max': 0.648,
    },
    'sensitivity': {
        'title_attribute': 'Sensitivity',
        'y-axis_label_attribute': 'V / (m/s)',
        'title_density': 'Sensitivity',
        'y-axis_label_density': '',
        'min': 70,
        'max': 90,
        'interval': 0.1,
        'tol_min': 74.4,
        'tol_max': 85.6,
    },
    'resistance': {
        'title_attribute': 'Resistance',
        'y-axis_label_attribute': 'Ohm',
        'title_density': 'Resistance',
        'y-axis_label_density': '',
        'min': 1700,
        'max': 2000,
        'interval': 0.5,
        'tol_min': 1702,
        'tol_max': 1998,
    },
    'thd': {
        'title_attribute': 'Distortion',
        'y-axis_label_attribute': '%',
        'title_density': 'Distortion',
        'y-axis_label_density': '',
        'min': 0,
        'max': 0.15,
        'interval': 0.005,
        'tol_min': None,
        'tol_max': 0.1,
    },
    'noise': {
        'title_attribute': 'Noise',
        'y-axis_label_attribute': 'microVolt',
        'title_density': 'Noise',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'interval': 1,
        'tol_min': None,
        'tol_max': None,
    },
    'tilt': {
        'title_attribute': 'Tilt',
        'y-axis_label_attribute': 'Degrees',
        'title_density': 'Tilt',
        'y-axis_label_density': '',
        'min': 0,
        'max': 15,
        'interval': 0.05,
        'tol_min': None,
        'tol_max': 10,
    },
}
nuseis_plt_settings = {
    'resistance': {
        'title_attribute': 'Resistance',
        'y-axis_label_attribute': 'Ohm',
        'title_density': 'Resistance',
        'y-axis_label_density': '',
        'min': 1700,
        'max': 2000,
        'bins': 50,
        'interval': 0.5,
        'tol_min': 1739,
        'tol_max': 1961,
    },
    'thd': {
        'title_attribute': 'Distortion',
        'y-axis_label_attribute': '%',
        'title_density': 'Distortion',
        'y-axis_label_density': '',
        'min': 119,
        'max': 122,
        'bins': 28,
        'interval': 0.01,
        'tol_min': None,
        'tol_max': 121,
    },
    'noise': {
        'title_attribute': 'Noise',
        'y-axis_label_attribute': 'microVolt',
        'title_density': 'Noise',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'bins': 50,
        'interval': 1,
        'tol_min': None,
        'tol_max': None,
    },
    'tilt': {
        'title_attribute': 'Tilt',
        'y-axis_label_attribute': 'Degrees',
        'title_density': 'Tilt',
        'y-axis_label_density': '',
        'min': 0,
        'max': 20,
        'bins': 20,
        'interval': 0.05,
        'tol_min': None,
        'tol_max': 10,
    },
}

@dataclass
class SwathDefinition:
    first_swath: int = 100
    last_swath: int = 524
    first_line: int = 970
    line_spacing: int = 200
    point_spacing: int = 25

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
    bits_type: str
    tilt: float
    config_id: int
    resistance: float
    noise: float
    thd: float
    polarity: str
    frequency: float
    damping: float
    sensitivity: float
    dyn_range: float
    ein: float
    gain: float
    offset: float
    gps_time: int
    ext_geophone: bool

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
