''' project settings Greater Lekhwair - Block A
'''
from pathlib import Path

# project parameters
RLS = 200
RPS = 25
SLS_sand = 200
SPS_sand = 12.5
SLS_flat = 50
SPS_flat = 25
project_azimuth = 0
repeat_factor = 1
swath_length = 50_000  # length > length of block
swath_1 = 100
active_lines = 46
swath_reverse = True

# parameter CTM
sweep_time = 9
move_up_time = 18
number_vibes = 12

# GIS parameters
EPSG = 3440  # PSD93_UTM40
project_base_folder = Path(
    'D:/OneDrive/Work/PDO/Lekhwair 3D/QGIS - mapping/Lekhwair Block C - Shapefiles/')

shapefile_src = (
    project_base_folder / 'Block A&B&C  boundary/block_a_source.shp')

shapefile_rcv = (
    project_base_folder / 'Block A&B&C  boundary/block_a_receiver.shp')

shapefile_rough = (
    project_base_folder / 'Terrain/Rough boundary of Block B.shp')

shapefile_facilities = (
    project_base_folder / 'Terrain/Facility boundary of Block B.shp')

shapefile_dune = (
    project_base_folder / 'Terrain/Dunes polygon.shp')

shapefile_sabkha = ''

# excel and chart parameters
excel_file = './swath_stats_lekhwair_block_a_2.xlsx'
title_chart = 'Lekhwair Block A'
