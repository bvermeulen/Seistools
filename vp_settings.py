''' settings and data structures for vp app
'''
from recordtype import recordtype

DATA_FILES_VAPS = "D:\\OneDrive\\Work\\PDO\\vp_data\\1 VAPS files\\"
DATA_FILES_VP = "D:\\OneDrive\\Work\\PDO\\vp_data\\1 VP Report\\"
FLEETS = 5

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
    'qc_flag'
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
    'positioning'
)

plt_settings = [
    {'key':'peak_phase',
     'title_attribute': 'Peak Phase',
     'y-axis_label_attribute': 'Degrees',
     'title_density': 'Peak Phase Density',
     'y-axis_label_density': '',
     'y-axis_min': 0,
     'y-axis_max': 10,
     'y-axis_int': 0.5,
    },
    {'key':'peak_dist',
     'title_attribute': 'Peak Distorion',
     'y-axis_label_attribute': 'Percentage',
     'title_density': 'Peak Distortion Density',
     'y-axis_label_density': '',
     'y-axis_min': 0,
     'y-axis_max': 60,
     'y-axis_int': 1,
    },
    {'key':'peak_force',
     'title_attribute': 'Peak Force',
     'y-axis_label_attribute': 'Percentage',
     'title_density': 'Peak Force Density',
     'y-axis_label_density': '',
     'y-axis_min': 0,
     'y-axis_max': 100,
     'y-axis_int': 1,
    },
    {'key':'avg_phase',
     'title_attribute': 'Average Phase',
     'y-axis_label_attribute': 'Degrees',
     'title_density': 'Average Phase Density',
     'y-axis_label_density': '',
     'y-axis_min': 0,
     'y-axis_max': 10,
     'y-axis_int': 0.5,
    },
    {'key':'avg_dist',
     'title_attribute': 'Average Distortion',
     'y-axis_label_attribute': 'Percentage',
     'title_density': 'Average Distortion Density',
     'y-axis_label_density': '',
     'y-axis_min': 0,
     'y-axis_max': 40,
     'y-axis_int': 1,
    },
    {'key':'avg_force',
     'title_attribute': 'Average Force',
     'y-axis_label_attribute': 'Percentage',
     'title_density': 'Average Force Density',
     'y-axis_label_density': '',
     'y-axis_min': 0,
     'y-axis_max': 100,
     'y-axis_int': 1,
    },
]
