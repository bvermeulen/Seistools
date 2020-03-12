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
SLS_flat = 25    # 25 m Block C, 50 m Block D
SPS_flat = 25
project_azimuth = np.pi * 0
swath_length = 50_000  # length > length of block
swath_1 = 100

# parameter CTF
flat_terrain = 0.85
rough_terrain = 0.50
facility_terrain = 0.55
dunes_terrain = 0.60
sabkha_terrain = 0.60
sweep_time = 9
move_up_time = 18
number_vibes = 12
hours_day = 22
ctm_constant = 3600 / (sweep_time + move_up_time) * hours_day * number_vibes

EPSG_PSD93_UTM40 = 3440
project_base_folder = Path('D:/OneDrive/Work/PDO/Haima Central/QGIS - mapping/')


class GisCalc:

    def __init__(self):
        self.swath_stats = pd.DataFrame(columns=[
            'swath', 'area', 'area_flat', 'area_dune', 'vp_theor', 'vp_flat',
            'vp_dune_src', 'vp_dune_rcv', 'vp_dune', 'vp_actual', 'dozer_km',
            'source_density', 'ctm', 'prod_day'])

        self.index = 0
        self.total_swaths = None
        self.fig, self.ax = plt.subplots(figsize=(6, 6))

        file_name = (project_base_folder /
                     'shape_files/blocks/20HN_Block_C_Sources_CO_6KM.shp')
        self.source_block_gpd = self.read_shapefile(file_name)
        self.plot_gpd(self.source_block_gpd)

        file_name = (project_base_folder /
                     'shape_files/BLOCK C SAND DUNE BOUNDARY.shp')
        self.dunes_gpd = self.read_shapefile(file_name)
        self.plot_gpd(self.dunes_gpd, 'green')

        bounds = self.source_block_gpd.geometry.bounds.iloc[0].to_list()
        self.sw_origin = (bounds[0], bounds[1])

        # patch: assuming azimuth is zero
        if project_azimuth == 0:
            self.total_swaths = int(round((bounds[2] - bounds[0]) / RLS)) + 1
        else:
            self.total_swaths = int(input('Total number of swaths: '))

    def get_envelop_swath_cornerpoint(self, swath_origin, swath_nr, test_azimuth=-1):
        ''' get the corner points of the envelope of the swath, i.e. length
            of swath > actual swath length, so any shape of swath will be captured
            when intersected with the actual block

            azimuth is the angle between northing and receiver line in positive direction

            arguments:
                swath_nr: interger [swath_1, n], counting from left to right
                          (azimuth < 90)
                test_azimuth: float in degrees [0, 360], can be provided for tests
            returns:
                tuple with 4 corner point tuples of swath swath_nr (ll, lr, tr, tl)
        '''
        assert swath_nr > 0, 'swath_nr must be [swath_1, n]'

        if test_azimuth == -1:
            azimuth = project_azimuth

        else:
            azimuth = np.pi * test_azimuth / 180
            swath_origin = (10, 20)

        swath_width_dx = RLS * np.cos(azimuth)
        swath_width_dy = -RLS * np.sin(azimuth)
        swath_length_dx = swath_length * np.sin(azimuth)
        swath_length_dy = swath_length * np.cos(azimuth)

        sw_ll = (swath_origin[0] + (swath_nr - swath_1) * swath_width_dx,
                 swath_origin[1] + (swath_nr - swath_1) * swath_width_dy)
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

    def aggregate_stats(self, swath_nr, area, area_dune, prod_day):
        area_flat = area - area_dune
        vp_theor = int(area * 1000 / SLS_flat * 1000 / SPS_flat)
        vp_flat = int(area_flat * 1000 / SLS_flat * 1000 / SPS_flat)
        vp_dune_src = int(area_dune * 1000 / SLS_sand * 1000 / SPS_sand)
        vp_dune_rcv = int(area_dune * 1000 / RLS * 1000 / SPS_sand)
        vp_dune = int(vp_dune_src + vp_dune_rcv)
        vp_actual = int(vp_flat + vp_dune)
        ctm = (ctm_constant *
               ((vp_flat * flat_terrain) + (vp_dune * dunes_terrain)) / vp_actual)
        prod_day += vp_actual / ctm

        results = {
            'swath': swath_nr,
            'area': area,
            'area_flat': area_flat,
            'area_dune': area_dune,
            'vp_theor': vp_theor,
            'vp_flat': vp_flat,
            'vp_dune_src': vp_dune_src,
            'vp_dune_rcv': vp_dune_rcv,
            'vp_dune': vp_dune,
            'vp_actual': vp_actual,
            'dozer_km': vp_dune * SPS_sand / 1000,
            'source_density': (vp_flat + vp_dune) / area,
            'ctm': ctm,
            'prod_day': prod_day,
        }
        self.swath_stats = self.swath_stats.append(results, ignore_index=True)
        return prod_day

    def check_totals(self, total_area, total_dune_area):
        # check if totals match the sum of the swathss
        area_block = sum(self.source_block_gpd.geometry.area.to_list()) / 1e6
        print(f'area block: {area_block}')
        print(f'area block: {total_area}')

        area_dunes = sum(self.dunes_gpd.geometry.area.to_list()) / 1e6
        print(f'area dunes: {area_dunes}')
        print(f'area dunes: {total_dune_area}')

    def stats_to_excel(self, file_name):
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')  #pylint: disable=abstract-class-instantiated
        self.swath_stats.to_excel(writer, sheet_name='Swaths', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Swaths']
        chart = workbook.add_chart({'type': 'line'})

        # format ['sheet', first_row, first_column, last_row, last_column]
        total_swaths = len(self.swath_stats)
        for col in [4, 5, 8, 9]:
            chart.add_series({
                'name': ['Swaths', 0, col],
                'categories': ['Swaths', 1, 0, total_swaths, 0],
                'values': ['Swaths', 1, col, total_swaths, col],
                })

        chart.set_title({'name': 'Block C'})
        chart.set_x_axis({'name': 'swath'})
        chart.set_y_axis({'name': 'vp'})
        chart.set_legend({'position': 'bottom'})

        worksheet.insert_chart('P2', chart)
        writer.save()

    def swath_range(self, swath_reverse=False):
        if swath_reverse:
            return range(self.total_swaths + swath_1 - 1, swath_1 - 1, -1)

        return range(swath_1, self.total_swaths + swath_1)

    def calc_swath_stats(self, swath_reverse=False):
        # loop over the swaths and create swaths area
        total_area, total_dune_area, prod_day = 0, 0, 0

        for swath_nr in self.swath_range(swath_reverse=swath_reverse):
            swath_gpd = self.create_sw_gpd(
                self.get_envelop_swath_cornerpoint(self.sw_origin, swath_nr))
            swath_gpd = overlay(self.source_block_gpd, swath_gpd, how='intersection')
            swath_area = sum(swath_gpd.geometry.area.to_list())/ 1e6

            swath_dune_gpd = overlay(swath_gpd, self.dunes_gpd, how='intersection')
            swath_dune_area = sum(swath_dune_gpd.geometry.area.to_list())/ 1e6
            self.plot_gpd(swath_dune_gpd, 'yellow')

            prod_day = self.aggregate_stats(
                swath_nr, swath_area, swath_dune_area, prod_day)

            print(f'swath: {swath_nr}, area: {swath_area:.2f}, '
                  f'dune area: {swath_dune_area:.2f}, production day: {prod_day:.1f}')
            total_area += swath_area
            total_dune_area += swath_dune_area

        self.check_totals(total_area, total_dune_area)
        self.stats_to_excel('./swath_stats.xlsx')


if __name__ == '__main__':
    gis_calc = GisCalc()
    gis_calc.calc_swath_stats(swath_reverse=True)
    plt.show()
