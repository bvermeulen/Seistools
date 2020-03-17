from pathlib import Path
import numpy as np
import pandas as pd
from shapely.geometry.polygon import Polygon
import geopandas as gpd
from geopandas import GeoDataFrame, GeoSeries, overlay
import matplotlib.pyplot as plt
''' extract statistis based on GIS geometries
'''
# project parameters
RLS = 200
RPS = 25
SLS_sand = 400
SPS_sand = 12.5
SLS_flat = 25    # 25 m Block C, 50 m Block D
SPS_flat = 25
project_azimuth = np.pi * 0
swath_length = 50_000  # length > length of block
swath_1 = 100
active_lines = 46
# calculate dozer lead for half the spread only, so excluding buffer
lead_dozer = int(active_lines / 2)

# parameter CTM
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

# GIS parameters
EPSG_PSD93_UTM40 = 3440
project_base_folder = Path('D:/OneDrive/Work/PDO/Haima Central/QGIS - mapping/')

#output parameters
title_chart = 'Block C'


class GisCalc:

    def __init__(self):
        self.swath_src_stats = pd.DataFrame(columns=[
            'swath', 'area', 'area_flat', 'area_sabkha', 'area_dune', 'theor',
            'flat', 'sabkha', 'dune_src', 'dune_rcv', 'dune', 'actual', 'doz_km',
            'density', 'ctm'
            ])

        self.swath_rcv_stats = pd.DataFrame(columns=[
            'swath', 'area', 'area_flat', 'area_dune', 'theor', 'flat',
            'dune', 'actual', 'doz_km', 'density'
            ])

        self.prod_stats = pd.DataFrame(columns=[
            'prod_day', 'swath_first', 'swath_last', 'area', 'area_flat', 'area_sabkha',
            'area_dune', 'doz_km', 'doz_total_km', 'vp_prod'
            ])

        self.index = 0
        self.total_swaths = None
        self.fig, self.ax = plt.subplots(figsize=(6, 6))

        file_name = (project_base_folder /
                     'shape_files/blocks/20HN_Block_C_Sources_CO_6KM.shp')
        self.source_block_gpd = self.read_shapefile(file_name)

        file_name = (project_base_folder /
                     'shape_files/blocks/20HN_Block_C_Receivers_CO_6KM.shp')
        self.receiver_block_gpd = self.read_shapefile(file_name)

        file_name = (project_base_folder /
                     'shape_files/BLOCK C SAND DUNE BOUNDARY.shp')
        self.dunes_gpd = self.read_shapefile(file_name)

        file_name = (project_base_folder /
                     'shape_files/Sabkha.shp')
        self.sabkha_gpd = self.read_shapefile(file_name)

        bounds = self.source_block_gpd.geometry.bounds.iloc[0].to_list()
        self.sw_origin = (bounds[0], bounds[1])

        # patch: assuming azimuth is zero
        if project_azimuth == 0:
            self.total_swaths = int(round((bounds[2] - bounds[0]) / RLS)) + 1
        else:
            self.total_swaths = int(input('Total number of swaths: '))

        # TODO remove after debugging
        # self.total_swaths = 20

    @staticmethod
    def get_envelop_swath_cornerpoint(swath_origin, swath_nr, test_azimuth=-1):
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

    def plot_gpd(self, shape_gpd, color='black'):
        shape_gpd.plot(ax=self.ax, facecolor='none', edgecolor=color, linewidth=0.5)

    @staticmethod
    def convert_area_to_vps(areas):
        area, area_sabkha, area_dune = areas['area'], areas['area_sabkha'], areas['area_dune']  #pylint: disable=line-too-long

        area_flat = area - area_sabkha - area_dune
        vp_theor = int(area * 1000 / SLS_flat * 1000 / SPS_flat)
        vp_flat = int(area_flat * 1000 / SLS_flat * 1000 / SPS_flat)
        vp_sabkha = int(area_sabkha * 1000 / SLS_flat * 1000 / SPS_flat)
        vp_dune_src = int(area_dune * 1000 / SLS_sand * 1000 / SPS_sand)
        vp_dune_rcv = int(area_dune * 1000 / RLS * 1000 / SPS_sand)
        vp_dune = int(vp_dune_src)
        vp_actual = int(vp_flat + vp_sabkha + vp_dune)
        ctm = (ctm_constant *
               (vp_flat * flat_terrain +
                vp_sabkha * sabkha_terrain +
                vp_dune * dunes_terrain) / vp_actual)
        vp_dozer_km = vp_dune_src * SPS_sand / 1000

        try:
            vp_density = vp_actual / area

        except ZeroDivisionError:
            vp_density = np.nan

        return {
            'theor': vp_theor,
            'flat': vp_flat,
            'sabkha': vp_sabkha,
            'dune_src': vp_dune_src,
            'dune_rcv': vp_dune_rcv,
            'dune': vp_dune,
            'actual': vp_actual,
            'doz_km': vp_dozer_km,
            'density': vp_density,
            'ctm': ctm,
        }

    def aggregate_src_stats(self, swath_nr, area, area_sabkha, area_dune):
        area_flat = area - area_sabkha - area_dune
        areas = {
            'swath': swath_nr,
            'area': area,
            'area_flat': area_flat,
            'area_sabkha': area_sabkha,
            'area_dune': area_dune,
        }

        points = self.convert_area_to_vps(areas)
        self.swath_src_stats = self.swath_src_stats.append(
            {**areas, **points}, ignore_index=True)

        return areas

    @staticmethod
    def convert_area_to_rcv(areas):
        area, area_dune = areas['area'], areas['area_dune']

        area_flat = area - area_dune
        rcv_theor = int(area * 1000 / RLS * 1000 / RPS)
        rcv_flat = int(area_flat * 1000 / RLS * 1000 / RPS)
        rcv_dune = int(area_dune * 1000 / RLS * 1000 / RPS)
        rcv_actual = int(rcv_flat + rcv_dune)
        rcv_dozer_km = rcv_dune * RPS / 1000

        try:
            rcv_density = rcv_actual / area

        except ZeroDivisionError:
            rcv_density = np.nan

        return {
            'theor': rcv_theor,
            'flat': rcv_flat,
            'dune': rcv_dune,
            'actual': rcv_actual,
            'doz_km': rcv_dozer_km,
            'density': rcv_density,
        }

    def aggregate_rcv_stats(self, swath_nr, area, area_dune):
        area_flat = area - area_dune
        areas = {
            'swath': swath_nr,
            'area': area,
            'area_flat' : area_flat,
            'area_dune': area_dune,
        }

        points = self.convert_area_to_rcv(areas)

        self.swath_rcv_stats = self.swath_rcv_stats.append(
            {**areas, **points}, ignore_index=True)

        return areas

    def aggregate_prod_stats(self, prod_day, swaths, sw_areas, doz, doz_total, prod):
        ''' aggregate stats by production day
        '''
        try:
            swath_first = swaths[0]
            swath_last = swaths[-1]

        except IndexError:
            swath_first = np.nan
            swath_last = np.nan

        results = {
            'prod_day': prod_day,
            'swath_first': swath_first,
            'swath_last': swath_last,
            'area': sw_areas[0],
            'area_flat': sw_areas[1],
            'area_sabkha': sw_areas[2],
            'area_dune': sw_areas[3],
            'doz_km': doz,
            'doz_total_km': doz_total,
            'vp_prod': prod,
        }
        self.prod_stats = self.prod_stats.append(results, ignore_index=True)

    def calc_src_stats(self, swath_nr):
        swath_gpd = self.create_sw_gpd(
            self.get_envelop_swath_cornerpoint(self.sw_origin, swath_nr))
        swath_gpd = overlay(self.source_block_gpd, swath_gpd, how='intersection')
        swath_area = sum(swath_gpd.geometry.area.to_list())/ 1e6

        swath_sabkha_gpd = overlay(swath_gpd, self.sabkha_gpd, how='intersection')
        swath_sabkha_area = sum(swath_sabkha_gpd.geometry.area.to_list())/ 1e6
        if swath_sabkha_area > 0:
            self.plot_gpd(swath_sabkha_gpd, 'brown')

        swath_dune_gpd = overlay(swath_gpd, self.dunes_gpd, how='intersection')
        swath_dune_area = sum(swath_dune_gpd.geometry.area.to_list())/ 1e6
        if swath_dune_area > 0:
            self.plot_gpd(swath_dune_gpd, 'yellow')

        areas = self.aggregate_src_stats(
            swath_nr, swath_area, swath_sabkha_area, swath_dune_area)

        return areas

    def calc_rcv_stats(self, swath_nr):
        swath_gpd = self.create_sw_gpd(
            self.get_envelop_swath_cornerpoint(self.sw_origin, swath_nr))
        swath_gpd = overlay(self.receiver_block_gpd, swath_gpd, how='intersection')
        swath_area = sum(swath_gpd.geometry.area.to_list())/ 1e6

        swath_dune_gpd = overlay(swath_gpd, self.dunes_gpd, how='intersection')
        swath_dune_area = sum(swath_dune_gpd.geometry.area.to_list())/ 1e6
        if swath_dune_area > 0:
            self.plot_gpd(swath_dune_gpd, 'yellow')

        areas = self.aggregate_rcv_stats(swath_nr, swath_area, swath_dune_area)

        return areas

    def swath_range(self, swath_reverse=False):
        ''' calculate ranges depending on swath order is reversed
        '''
        if swath_reverse:
            return range(self.total_swaths + swath_1 - 1, swath_1 - 1, -1)

        return range(swath_1, self.total_swaths + swath_1)

    def swaths_stats(self, swath_reverse=False):
        ''' loop over the swaths, calculate areas and produce
            the source and receiver stastics based on source & receiver densities
        '''
        self.plot_gpd(self.receiver_block_gpd, color='blue')
        self.plot_gpd(self.source_block_gpd, color='red')

        total_src_area, total_src_sabkha_area, total_src_dune_area = 0, 0, 0
        total_rcv_area, total_rcv_dune_area = 0, 0

        for swath_nr in self.swath_range(swath_reverse=swath_reverse):
            areas_src = self.calc_src_stats(swath_nr)
            total_src_area += areas_src['area']
            total_src_sabkha_area += areas_src['area_sabkha']
            total_src_dune_area += areas_src['area_dune']

            areas_rcv = self.calc_rcv_stats(swath_nr)
            total_rcv_area += areas_rcv['area']
            total_rcv_dune_area += areas_rcv['area_dune']

            self.print_status(swath_nr, areas_src)

        self.print_totals(total_src_area, total_src_sabkha_area, total_src_dune_area,
                          total_rcv_area, total_rcv_dune_area)

    def calc_prod_stats(self, swath_reverse=False):
        def sign():
            if swath_reverse:
                return -1
            return 1

        # determine dozer lead required before start of production on day zero
        if swath_reverse:
            start_swath = swath_1 + self.total_swaths
            sw_doz_range = [sw for sw in range(start_swath, start_swath - lead_dozer, -1)]

        else:
            start_swath = swath_1
            sw_doz_range = [sw for sw in range(start_swath, start_swath + lead_dozer)]

        doz_src_km = self.swath_src_stats[
            self.swath_src_stats['swath'].isin(sw_doz_range)]['doz_km'].sum()
        doz_rcv_km = self.swath_rcv_stats[
            self.swath_rcv_stats['swath'].isin(sw_doz_range)]['doz_km'].sum()
        doz = doz_src_km + doz_rcv_km
        doz_total = doz
        self.aggregate_prod_stats(0, [], np.zeros(4), doz, doz_total, 0)

        prod_day = 1
        day_duration = 0
        day_prod = 0
        day_areas = np.zeros(4)
        day_doz = 0
        day_swaths = []
        dozer_swath = sw_doz_range[-1] + sign()

        for swath in self.swath_range(swath_reverse=swath_reverse):
            result_src = self.swath_src_stats[self.swath_src_stats['swath'] == swath]
            sw_areas = np.array([
                result_src['area'].values[0],
                result_src['area_flat'].values[0],
                result_src['area_sabkha'].values[0],
                result_src['area_dune'].values[0],
            ])
            actual_vp = result_src['actual'].values[0]
            ctm = result_src['ctm'].values[0]
            sw_duration = actual_vp / ctm
            day_duration += sw_duration

            # get dozer km
            doz_src_km = self.swath_src_stats[
                self.swath_src_stats['swath'] == dozer_swath]['doz_km'].sum()
            doz_rcv_km = self.swath_rcv_stats[
                self.swath_rcv_stats['swath'] == dozer_swath]['doz_km'].sum()
            sw_doz = doz_src_km + doz_rcv_km

            if day_duration > 1:
                # swath is overflowing to next day, assume swath can only overflow 1 day!
                portion_tomorrow = (day_duration - 1) / sw_duration
                portion_today = 1 - portion_tomorrow
                day_prod += portion_today * actual_vp
                day_areas += portion_today * sw_areas
                day_doz += portion_today * sw_doz
                doz_total += day_doz
                day_swaths.append(swath)

                self.aggregate_prod_stats(
                    prod_day, day_swaths, day_areas, day_doz, doz_total, day_prod)

                # set up for next day
                prod_day += 1
                day_prod = portion_tomorrow * actual_vp
                day_areas = portion_tomorrow * sw_areas
                day_doz = portion_tomorrow * sw_doz
                day_duration = day_prod / ctm
                day_swaths = [swath]

            else:
                day_prod += actual_vp
                day_areas += sw_areas
                day_doz += sw_doz
                day_swaths.append(swath)

            dozer_swath += sign()

        doz_total += day_doz
        self.aggregate_prod_stats(
            prod_day, day_swaths, day_areas, day_doz, doz_total, day_prod)

    @staticmethod
    def print_status(swath_nr, areas):
        ''' print a status line '''
        print(f'swath: {swath_nr}, '
              f'area: {areas["area"]:.2f}, '
              f'sabkha area: {areas["area_sabkha"]:.2f}, '
              f'dune area: {areas["area_dune"]:.2f}\r', end='')

    def print_totals(self, total_src_area, total_src_sabkha_area, total_src_dune_area,
                     total_rcv_area, total_rcv_dune_area):
        # check if totals match the sum of the swathss
        area_src_block = sum(self.source_block_gpd.geometry.area.to_list()) / 1e6
        print(f'\n\narea source block: {area_src_block}')
        print(f'area source block: {total_src_area}\n')

        area_sabkha = sum(self.sabkha_gpd.geometry.area.to_list()) / 1e6
        print(f'area sabkha: {area_sabkha}')
        print(f'area source sabkha: {total_src_sabkha_area}\n')

        area_dunes = sum(self.dunes_gpd.geometry.area.to_list()) / 1e6
        print(f'area dunes: {area_dunes}')
        print(f'area source dunes: {total_src_dune_area}\n')

        area_rcv_block = sum(self.receiver_block_gpd.geometry.area.to_list()) / 1e6
        print(f'area receiver block: {area_rcv_block}')
        print(f'area receiver block: {total_rcv_area}\n')

        print(f'area dunes: {area_dunes}')
        print(f'area dunes: {total_rcv_dune_area}')

    def stats_to_excel(self, file_name):
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')  #pylint: disable=abstract-class-instantiated
        workbook = writer.book

        self.swath_src_stats.to_excel(writer, sheet_name='Source', index=False)
        self.swath_rcv_stats.to_excel(writer, sheet_name='Receiver', index=False)
        self.prod_stats.to_excel(writer, sheet_name='Prod', index=False)

        ws_charts = workbook.add_worksheet('Charts')
        total_swaths = len(self.swath_src_stats)
        total_production_days = len(self.prod_stats)
        name_font_title = {'name': 'Arial', 'size': 10}

        # Chart 1: VP by type
        # format ['sheet', first_row, first_column, last_row, last_column]
        chart1 = workbook.add_chart({'type': 'line'})
        for col in [5, 6, 7, 10, 11]:
            chart1.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
                })

        chart1.set_title({'name': title_chart + ' - VP by type',
                          'name_font': name_font_title,})
        chart1.set_x_axis({'name': 'swath'})
        chart1.set_y_axis({'name': 'vp'})
        chart1.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B2', chart1)

        # Chart 2: CTM by swath
        chart2 = workbook.add_chart({'type': 'line'})
        for col in [14]:
            chart2.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
                })

        chart2.set_title({'name': title_chart + ' - CTM by swath',
                          'name_font': name_font_title,})
        chart2.set_x_axis({'name': 'swath'})
        chart2.set_y_axis({'name': 'vp'})
        chart2.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B18', chart2)

        # Chart 3: Source density by swath
        chart3 = workbook.add_chart({'type': 'line'})
        for col in [13]:
            chart3.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
                })

        chart3.set_title({'name': title_chart + ' - Source density by swath',
                          'name_font': name_font_title,})
        chart3.set_x_axis({'name': 'swath'})
        chart3.set_y_axis({'name': 'vp'})
        chart3.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B34', chart3)

        # Chart 4: dozer used by production day
        chart4 = workbook.add_chart({'type': 'line'})
        for col in [7]:
            chart4.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
                })

        chart4.set_title({'name': title_chart + ' - Dozer lead used by day',
                          'name_font': name_font_title,})
        chart4.set_x_axis({'name': 'Day'})
        chart4.set_y_axis({'name': 'km'})
        chart4.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('J2', chart4)

        # # Chart 5: dozer used cumulative
        chart5 = workbook.add_chart({'type': 'line'})
        for col in [8]:
            chart5.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
                })

        chart5.set_title({'name': title_chart + ' - Cumul. dozer lead used',
                          'name_font': name_font_title,})
        chart5.set_x_axis({'name': 'Day'})
        chart5.set_y_axis({'name': 'km'})
        chart5.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('J18', chart5)

        # Chart 6: Production
        chart6 = workbook.add_chart({'type': 'line'})
        for col in [9]:
            chart6.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
                })

        chart6.set_title({'name': title_chart + ' - Production',
                          'name_font': name_font_title,})
        chart6.set_x_axis({'name': 'Day'})
        chart6.set_y_axis({'name': 'vp'})
        chart6.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('R2', chart6)

        # ... and save it all to excel
        ws_charts.activate()
        writer.save()


def main():
    gis_calc = GisCalc()
    gis_calc.swaths_stats(swath_reverse=True)
    gis_calc.calc_prod_stats(swath_reverse=True)
    gis_calc.stats_to_excel('./swath_stats.xlsx')

    plt.show()


if __name__ == '__main__':
    main()
