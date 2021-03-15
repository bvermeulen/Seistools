''' settings and data structures for vp app
'''
import datetime
from enum import IntEnum
from recordtype import recordtype

#DATA_FILES_VAPS = r'D:\\OneDrive\\Work\\PDO\Lekhwair 3D\\VP data\VAPS_TEST\\'
DATA_FILES_VP = r'D:\\OneDrive\\Work\\PDO\\Lekhwair 3D\\VP data\\VP_RECORD\\'
#DATA_FILES_RECEIVERS = r'D:\\OneDrive\\Work\\PDO\Lekhwair 3D\\Receiver data\\'
DATA_FILES_VAPS = r'data_files\\vibes\\'
DATA_FILES_RECEIVERS = r'data_files\\nodes\\'

DATABASE = 'Haniya_North_db.sqlite3'
INIT_DB = False
LINK_VP_TO_VAPS = False
DATABASE_TABLE = 'VAPS'
GMT_OFFSET = datetime.timedelta(hours=+4)
DENSE_CRITERIUM = 15  # if distance < DENSE_CRITERIUM then dense_flag is true
SWEEP_TIME = 9
PAD_DOWN_TIME = 2.5

FLEETS = 13
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
        'tol_max': None,
    },

    'avg_phase': {
        'title_attribute': 'Average Phase',
        'y-axis_label_attribute': 'Degrees',
        'title_density': 'Average Phase Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 20,
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
        'tol_max': None,
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
        'max_vp_hour': 200,
        'tick_intval_vp_hour': 20,
        'max_vibs': 5,
        'tick_intval_vibs': 1,
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
        'min': 50,
        'max': 70,
        'interval': 0.1,
        'tol_min': 55.2,
        'tol_max': 64.8,
    },

    'sensitivity': {
        'title_attribute': 'Sensitivity',
        'y-axis_label_attribute': 'V / (m/s)',
        'title_density': 'Sensitivity',
        'y-axis_label_density': '',
        'min': 70,
        'max': 90,
        'interval': 0.1,
        'tol_min': 75.2,
        'tol_max': 84.8,
    },

    'resistance': {
        'title_attribute': 'Resistance',
        'y-axis_label_attribute': 'Ohm',
        'title_density': 'Resistance',
        'y-axis_label_density': '',
        'min': 1700,
        'max': 2000,
        'interval': 0.5,
        'tol_min': 1739,
        'tol_max': 1961,
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

    'battery': {
        'title_attribute': 'Battery',
        'y-axis_label_attribute': 'Volt',
        'title_density': 'Battery',
        'y-axis_label_density': '',
        'min': 7,
        'max': 10,
        'interval': 0.05,
        'tol_min': 7,
        'tol_max': 9,
    },

    'noise': {
        'title_attribute': 'Noise',
        'y-axis_label_attribute': 'microVolt',
        'title_density': 'Noise',
        'y-axis_label_density': '',
        'min': 0,
        'max': 1,
        'interval': 0.01,
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

FilesNodeTable = recordtype(
    'FilesNodeTable',
    'file_name, '
    'file_date'
)

NodeTable = recordtype(
    'NodeTable',
    'line, '
    'station, '
    'rcvr_index, '
    'id_file, '
    'id_point, '
    'qtm_sn, '
    'battery, '
    'ch, '
    'type, '
    'noise, '
    'frequency, '
    'damping, '
    'sensitivity, '
    'resistance, '
    'leakage, '
    'thd, '
    'crossfeed, '
    'power, '
    'cmr, '
    'tilt, '
    'acqrate, '
    'time_stamp'
)

RcvrTable = recordtype(
    'RcvrTable',
    'line, '
    'station, '
    'rcvr_index, '
    'easting '
    'northing '
    'elevation'
)

FilesVpTable = recordtype(
    'FilesVpTable',
    'id, '
    'file_name, '
    'file_date'
)

VpTable = recordtype(
    'VpTable',
    'id, '
    'file_id, '
    'vaps_id, '
    'line, '
    'station, '
    'vibrator, '
    'time_break, '
    'planned_easting, '
    'planned_northing, '
    'easting, '
    'northing, '
    'elevation, '
    'offset, '
    'peak_force, '
    'avg_force, '
    'peak_dist, '
    'avg_dist, '
    'peak_phase, '
    'avg_phase, '
    'qc_flag, '
    'distance, '
    'time, '
    'velocity, '
    'dense_flag'
)

FilesVapsTable = recordtype(
    'FilesVapsTable',
    'id, '
    'file_name, '
    'file_date'
)

VapsTable = recordtype(
    'VapsTable',
    'id, '
    'file_id, '
    'line, '
    'station, '
    'fleet_nr, '
    'vibrator, '
    'drive, '
    'avg_phase, '
    'peak_phase, '
    'avg_dist, '
    'peak_dist, '
    'avg_force, '
    'peak_force, '
    'avg_stiffness, '
    'avg_viscosity, '
    'easting, '
    'northing, '
    'elevation, '
    'time_break, '
    'hdop, '
    'tb_date, '
    'positioning, '
    'distance, '
    'time, '
    'velocity, '
    'dense_flag'
)
