''' settings and data structures for vp app
'''
import datetime
from enum import IntEnum
from recordtype import recordtype

DATA_FILES_VAPS = r'D:\\OneDrive\\Work\\PDO\Lekhwair 3D\\VP data\VAPS\\'
DATA_FILES_VP = r'D:\\OneDrive\\Work\\PDO\\Lekhwair 3D\\VP data\\VP_RECORD\\'
DATA_FILES_RECEIVERS = r'D:\\OneDrive\\Work\\PDO\Lekhwair 3D\\Receiver data\\Test\\'

DATABASE = 'Lekhwair'
LINK_VP_TO_VAPS = False
DATABASE_TABLE = 'VP'
GMT_OFFSET = datetime.timedelta(hours=+4)
DENSE_CRITERIUM = 15  # if distance < DENSE_CRITERIUM then dense_flag is true
SWEEP_TIME = 9
PAD_DOWN_TIME = 2.5

FLEETS = 30
MARKERSIZE = 0.2
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

lines = [
    1001, 1010, 1008, 1028, 1007, 1006, 1004, 1002, 1003, 1009,
    1025, 1021, 1020, 1029, 1016, 1022, 1014, 1013, 1015, 1019,
    1018, 1005, 1025, 1012, 1023, 1024, 1027, 1017, 1011,
]


class MapTypes(IntEnum):
    local = 0
    osm = 1
    no_background = 3

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
    'point, '
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

plt_settings = {
    'peak_phase': {
        'title_attribute': 'Peak Phase',
        'y-axis_label_attribute': 'Degrees',
        'title_density': 'Peak Phase Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 30,
        'interval': 0.5,
        },

    'peak_dist': {
        'title_attribute': 'Peak Distortion',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Peak Distortion Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'interval': 1,
        },

    'peak_force': {
        'title_attribute': 'Peak Force',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Peak Force Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'interval': 1,
        },

    'avg_phase': {
        'title_attribute': 'Average Phase',
        'y-axis_label_attribute': 'Degrees',
        'title_density': 'Average Phase Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 20,
        'interval': 0.5,
        },

    'avg_dist': {
        'title_attribute': 'Average Distortion',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Average Distortion Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 80,
        'interval': 1,
        },

    'avg_force': {
        'title_attribute': 'Average Force',
        'y-axis_label_attribute': 'Percentage',
        'title_density': 'Average Force Density',
        'y-axis_label_density': '',
        'min': 0,
        'max': 100,
        'interval': 1,
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

}

FilesRcvTable = recordtype(
    'FilesRcvTable',
    'file_name, '
    'file_date'
)

RcvTable = recordtype(
    'RcvTable',
    'file_id, '
    'rcv_point_id, '
    'fdu_sn, '
    'line, '
    'station, '
    'sensor_type, '
    'resistance, '
    'tilt, '
    'noise, '
    'leakage, '
    'time_update, '
    'easting, '
    'northing, '
    'elevation'
)
