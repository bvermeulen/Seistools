''' project settings Central Oman
'''
from pathlib import Path

# project parameters
RLS = 200
RPS = 25
RLS_sand = 1000
RPS_sand = 25
SLS_flat = 37.5
SPS_flat = 25
SLS_sand = 375
SPS_sand = 25
RLS_infill = 25
RPS_infill = 200
project_azimuth = 0
repeat_factor = 1
swath_length = 120_000  # length > length of block
swath_1 = 100
active_lines = 50
swath_reverse = True
source_on_receivers = False

# parameter CTM
sweep_time = 9
move_up_time = 17
number_vibes = 10

# GIS parameters
EPSG = 3440  # PSD93_UTM40
project_base_folder = Path('D:/PDO/Central Oman 2022/6 Mapping/4 shape files')

shapefile_src = (
    project_base_folder / 'boundaries/Central Oman Block_A_S.shp'
)
shapefile_rcv = (
    project_base_folder / 'boundaries/Central Oman Block_A_R.shp'
)
shapefile_dune = (
    project_base_folder / 'terrain/dunes_a.shp'
)
shapefile_infill = (
    project_base_folder / 'dunes/dunes_infill.shp'
)
shapefile_rough = (
    project_base_folder / 'terrain/rough_a.shp'
)
shapefile_facilities = (
    project_base_folder / 'terrain/facilities_a.shp'
)
shapefile_sabkha = ''

# excel and chart parameters
excel_file = './swath_stats_central_oman.xlsx'
title_chart = 'Central Oman'
