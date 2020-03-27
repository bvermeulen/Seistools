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

# parameter CTM
sweep_time = 9
move_up_time = 18
number_vibes = 6

# GIS parameters
EPSG = 3440  # PSD93_UTM40
project_base_folder = Path('D:/OneDrive/Work/PDO/Haima Central/QGIS - mapping/')

shapefile_src = (
    project_base_folder / 'shape_files/blocks/Whole_Shell_Option_4_Source.shp')

shapefile_rcv = (
    project_base_folder / 'shape_files/blocks/Whole_Shell_Option_4_Rec.shp')

shapefile_dune = (
    project_base_folder / 'shape_files/dunes/Whole_Shell_Option_4_Source_SD.shp')

# shapefile_dune = (
#     project_base_folder / 'shape_files/dunes/Shell - Dunes (BGP).shp')

shapefile_sabkha = (
    project_base_folder / 'shape_files/Sabkha.shp')


# excel and chart parameters
excel_file = './swath_stats_lekhwair_block_a.xlsx'
title_chart = 'Lekhwair Block A'
