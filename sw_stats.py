from pathlib import Path
import numpy as np
import pandas as pd
from shapely.geometry.polygon import Polygon
import geopandas as gpd
from geopandas import GeoDataFrame, GeoSeries, overlay
import matplotlib.pyplot as plt

''' extract statistis based on GIS geometries
'''
RLS = 200
RPS = 25
SLS_sand = 400
SPS_sand = 12.5
SLS_flat = 50
SPS_flat = 25
project_azimuth = np.pi * 0
swath_length = 50_000  # length > length of block
EPSG_PSD93_UTM40 = 3440
project_base_folder = Path('D:/OneDrive/Work/PDO/Haima Central/QGIS - mapping/')


class GisCalc:

    def __init__(self):
        self.swath_stats = pd.DataFrame(columns=[
            'swath', 'area', 'area_flat', 'area_dune', 'vp_flat', 'vp_dune',
            'vp_receiver', 'dozer_km'])

        self.index = 0
        self.fig, self.ax = plt.subplots(figsize=(6, 6))

    def get_envelop_swath_cornerpoint(self, swath_origin, swath_nr, test_azimuth=-1):
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
        assert swath_nr > 0, 'swath_nr must be [1, n]'

        if test_azimuth == -1:
            azimuth = project_azimuth

        else:
            azimuth = np.pi * test_azimuth / 180
            swath_origin = (10, 20)

        swath_width_dx = RLS * np.cos(azimuth)
        swath_width_dy = -RLS * np.sin(azimuth)
        swath_length_dx = swath_length * np.sin(azimuth)
        swath_length_dy = swath_length * np.cos(azimuth)

        sw_ll = (swath_origin[0] + (swath_nr - 1) * swath_width_dx,
                 swath_origin[1] + (swath_nr - 1) * swath_width_dy)
        sw_lr = (sw_ll[0] + swath_width_dx, sw_ll[1] + swath_width_dy)
        sw_tl = (sw_ll[0] + swath_length_dx, sw_ll[1] + swath_length_dy)
        sw_tr = (sw_tl[0] + swath_width_dx, sw_tl[1] + swath_width_dy)

        return sw_ll, sw_lr, sw_tr, sw_tl

    @staticmethod
    def create_sw_gpd(cornerpoints):
        return GeoDataFrame(
            crs=EPSG_PSD93_UTM40, geometry=GeoSeries(Polygon(cornerpoints)))

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
        shapefile_gpd.to_crs(f'EPSG:{EPSG_PSD93_UTM40}')
        return shapefile_gpd

    def plot_gpd(self, shapefile_gpd, color='black'):
        shapefile_gpd.plot(ax=self.ax, facecolor='none', edgecolor=color)

    def collate_stats(self, swath_nr, area, area_dune):
        vp_dune = area_dune * 1000 / SLS_sand * 1000 / SPS_sand
        vp_receiver = area_dune * 1000 / RLS * 1000 / SPS_sand
        area_flat = area - area_dune
        results = {
            'swath': int(swath_nr),
            'area': area,
            'area_flat': area_flat,
            'area_dune': area_dune,
            'vp_flat': area_flat * 1000 / SLS_flat * 1000 / SPS_flat,
            'vp_dune': int(vp_dune),
            'vp_receiver': int(vp_receiver),
            'dozer_km': int((vp_dune + vp_receiver) * SPS_sand) / 1000,
        }
        self.swath_stats = self.swath_stats.append(results, ignore_index=True)

    def stats_to_excel(self, file_name):
        self.swath_stats.to_excel(file_name, index=False)

    def calc_areas(self):
        file_name = (project_base_folder /
                     'shape_files/blocks/20HN_Block_C_Sources_CO_6KM.shp')
        source_block_gpd = self.read_shapefile(file_name)
        self.plot_gpd(source_block_gpd)

        file_name = (project_base_folder /
                     'shape_files/BLOCK C SAND DUNE BOUNDARY.shp')
        dunes_gpd = self.read_shapefile(file_name)
        self.plot_gpd(dunes_gpd, 'green')

        bounds = source_block_gpd.geometry.bounds.iloc[0].to_list()
        sw_origin = (bounds[0], bounds[1])
        total_swaths = int(round(
            np.sqrt((bounds[2] - bounds[0])**2 + (bounds[3] - bounds[1])**2) / RLS))

        # create swaths area
        total_area, total_dune_area = 0, 0
        for swath_nr in range(1, total_swaths):
            swath_gpd = self.create_sw_gpd(
                self.get_envelop_swath_cornerpoint(sw_origin, swath_nr))
            swath_gpd = overlay(source_block_gpd, swath_gpd, how='intersection')
            swath_area = sum(swath_gpd.geometry.area.to_list())/ 1e6

            swath_dune_gpd = overlay(swath_gpd, dunes_gpd, how='intersection')
            swath_dune_area = sum(swath_dune_gpd.geometry.area.to_list())/ 1e6
            self.plot_gpd(swath_dune_gpd, 'yellow')

            self.collate_stats(swath_nr, swath_area, swath_dune_area)

            print(f'swath: {swath_nr}, area: {swath_area:.2f}, '
                  f'dune area: {swath_dune_area:.2f}')
            total_area += swath_area
            total_dune_area += swath_dune_area

        area_block = sum(source_block_gpd.geometry.area.to_list()) / 1e6
        print(f'area block: {area_block}')
        print(f'area block: {total_area}')

        area_dunes = sum(dunes_gpd.geometry.area.to_list()) / 1e6
        print(f'area dunes: {area_dunes}')
        print(f'area dunes: {total_dune_area}')

        print(self.swath_stats.head(20))
        self.stats_to_excel('./swath_stats.xlsx')


        plt.show()


if __name__ == '__main__':
    gis_calc = GisCalc()
    gis_calc.calc_areas()
