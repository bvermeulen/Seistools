from pathlib import Path
import numpy as np
from shapely.geometry.polygon import Polygon
import geopandas as gpd
from geopandas import GeoDataFrame, GeoSeries
import matplotlib.pyplot as plt
from boundary_data import boundary_data

''' extract statistis based on GIS geometries
'''
# pseudocode for sources
# enter project constants like SL, RL, etc
# calculate azimuth
# read block envelope
# read block source area
# read block dune area
# cut swath envelope to the left border of source area (area is zero)
# loop over swaths:
    # add RLS to the east
    # determine swath area
    # intersect swath area with with dune area -> sw dune area
    # calculate the percentage dunes in the swath
    # difference swath area with sq dune areaz -> sw flat area
    # calculate the statistics in dunes from sw dune area
    # calculate the statistics in flat from sw flat area
    # output the statistics to excel


RLS = 200
SLS_sand = 50
SLS_flat = 400
RPS = 25
SPS_sand = 12.5
SPS_flat = 25
project_azimuth = np.pi * 0
swath_length = 50_000
data_folder = Path('OneDrive/Work/PDO/Haima Central/QGIS - mapping/')
EPSG_PSD93_UTM40 = 3440
project_base_folder = Path('D:/OneDrive/Work/PDO/Haima Central/QGIS - mapping/')


class GisCalc:

    def __init__(self):
        self.block_boundary = boundary_data[-1]
        self.fig, self.ax = plt.subplots(figsize=(6, 6))

    def get_envelop_swath_cornerpoint(self, swath_nr, test_azimuth=-1):
        ''' get the corner points of the envelope of the swath, i.e. length
            of swath > actual swath length, so any shape of swath will be captured
            when intersected with the actual block

            azimuth is the angle between northing and receiver line in positive direction

            arguments:
                swath_nr: interger [1, n], counting from left to right (azimuth < 90)
                test_azimuth: float in degrees [0, 360], can be provided for tests
            returns:
                tuple with 4 corner point tuples of swath swath_nr (ll, lr, tr, tl)
        '''
        if test_azimuth == -1:
            azimuth = project_azimuth

        else:
            azimuth = np.pi * test_azimuth / 180

        swath_origin = self.block_boundary['vertices'][0]
        swath_width_dx = RLS * np.cos(azimuth)
        swath_width_dy = -RLS * np.sin(azimuth)
        swath_length_dx = swath_length * np.sin(azimuth)
        swath_length_dy = swath_length * np.cos(azimuth)

        sw_ll = (swath_origin[0] + swath_nr * swath_width_dx,
                 swath_origin[1] + swath_nr * swath_width_dy)
        sw_lr = (sw_ll[0] + swath_width_dx, sw_ll[1] + swath_width_dy)
        sw_tl = (sw_ll[0] + swath_length_dx, sw_ll[1] + swath_length_dy)
        sw_tr = (sw_tl[0] + swath_width_dx, sw_tl[1] + swath_width_dy)

        return sw_ll, sw_lr, sw_tr, sw_tl

    @staticmethod
    def create_sw_gpd(cornerpoints):
        return GeoDataFrame(
            crs=f'epsg:{EPSG_PSD93_UTM40}', geometry=GeoSeries(Polygon(cornerpoints)))

    @staticmethod
    def read_shapefile(file_name):
        ''' read a shape file and converts crs to UTM PSD93 Zone 40
            Arguments:
                file_name: string, full name of the shapefile with the
                           extension .shp
            Returns:
                geopandas dataframe with the shapefile data
        '''
        shapefile_gpd = gpd.read_file(file_name)
        shapefile_gpd.to_crs(EPSG_PSD93_UTM40)
        return shapefile_gpd

    def plot_shapefile(self, shapefile_gpd, color='black'):
        shapefile_gpd.plot(ax=self.ax, facecolor='none', edgecolor=color)

    def calc_stats(self):
        file_name = (project_base_folder /
                     'shape_files/blocks/20HN_Block_C_Sources_CO_6KM.shp')
        source_block_gpd = self.read_shapefile(file_name)
        self.plot_shapefile(source_block_gpd)

        file_name = (project_base_folder /
                     'shape_files/blocks/20HN_Block_C_Receivers_CO_6KM.shp')
        receiver_block_gpd = self.read_shapefile(file_name)
        self.plot_shapefile(receiver_block_gpd, 'red')

        plt.show()


if __name__ == '__main__':
    gis_calc = GisCalc()
    gis_calc.calc_stats()
