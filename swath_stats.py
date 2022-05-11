from dataclasses import dataclass
import numpy as np
import pandas as pd
from shapely.geometry.polygon import Polygon
import geopandas as gpd
from geopandas import GeoDataFrame, GeoSeries, overlay
import matplotlib.pyplot as plt
import swath_settings as settings
''' extract statistis based on GIS geometries
'''
# project parameters
RLS = settings.RLS
RPS = settings.RPS
RLS_SAND = settings.RLS_sand
SLS_SAND = settings.SLS_sand
SPS_SAND = settings.SPS_sand
SLS_FLAT = settings.SLS_flat
SPS_FLAT = settings.SPS_flat
PROJECT_AZIMUTH = np.pi * settings.project_azimuth
REPEAT_FACTOR = settings.repeat_factor
SWATH_LENGTH = settings.swath_length  # length > length of block
SWATH_1 = settings.swath_1
ACTIVE_LINES = settings.active_lines
# calculate dozer and receiver lead for half the spread
LEAD_RECEIVER = int(ACTIVE_LINES * REPEAT_FACTOR / 2)
LEAD_DOZER = LEAD_RECEIVER + int(5000 / RLS)

# parameters CTM fixed
flat_terrain = 0.85
rough_terrain = 0.60
facilities_terrain = 0.55
dunes_terrain = 0.60
sabkha_terrain = 0.60
hours_day = 24
sweep_time = settings.sweep_time
move_up_time = settings.move_up_time
number_vibes = settings.number_vibes
ctm_constant = 3600 / (sweep_time + move_up_time) * hours_day * number_vibes


@dataclass
class Production:
    doz_km: float
    doz_total_km: float
    prod: float
    flat: float
    rough: float
    facilities: float
    dunes: float
    sabkha: float
    layout_flat: float
    layout_dube: float
    pickup_flat: float
    pickup_dune: float


class GisCalc:

    def __init__(self):
        self.swath_src_stats = pd.DataFrame(columns=[
            'swath', 'area', 'area_flat', 'area_rough', 'area_facilities', 'area_dunes',
            'area_sabkha', 'theor', 'flat', 'rough', 'facilities', 'dune_src', 'dune_rcv',
            'dunes', 'sabkha', 'skips', 'actual', 'doz_km', 'density', 'ctm'
            ])

        self.swath_rcv_stats = pd.DataFrame(columns=[
            'swath', 'area', 'area_flat', 'area_dunes', 'theor', 'flat', 'dunes',
            'actual', 'doz_km', 'density'
            ])

        self.prod_stats = pd.DataFrame(columns=[
            'prod_day', 'swath_first', 'swath_last', 'vp_flat', 'vp_rough',
            'vp_facilities', 'vp_dunes', 'vp_sabkha', 'vp_prod', 'doz_km', 'doz_total_km',
            'layout_flat', 'layout_dune', 'layout', 'pickup_flat', 'pickup_dune', 'pickup'
            ])

        self.index = 0
        self.total_swaths = None
        self.fig, self.ax = plt.subplots(figsize=(6, 6))

        self.source_block_gpd = self.read_shapefile(settings.shapefile_src)
        self.receiver_block_gpd = self.read_shapefile(settings.shapefile_rcv)

        if settings.shapefile_rough:
            self.rough_gpd = self.read_shapefile(settings.shapefile_rough)

        else:
            self.rough_gpd = None

        if settings.shapefile_facilities:
            self.facilities_gpd = self.read_shapefile(settings.shapefile_facilities)

            try:
                self.facilities_gpd = overlay(
                    self.facilities_gpd, self.rough_gpd, how='difference')

            except AttributeError:
                pass

        else:
            self.facilities_gpd = None


        if settings.shapefile_dune:
            self.dunes_gpd = self.read_shapefile(settings.shapefile_dune)

            try:
                self.dune_gpd = overlay(
                    self.dune_gpd, self.facilties_gpd, how='difference')

            except AttributeError:
                pass

            try:
                self.dune_gpd = overlay(
                    self.dune_gpd, self.rough_gpd, how='difference')
            except AttributeError:
                pass

        else:
            self.dunes_gpd = None

        if settings.shapefile_sabkha:
            self.sabkha_gpd = self.read_shapefile(settings.shapefile_sabkha)

            try:
                self.sabkha_gpd = overlay(
                    self.sabkha_gpd, self.dune_gpd, how='difference')

            except AttributeError:
                pass

            try:
                self.sabkha_gpd = overlay(
                    self.sabkha_gpd, self.facilties_gpd, how='difference')

            except AttributeError:
                pass

            try:
                self.sabkha_gpd = overlay(
                    self.sabkha_gpd, self.rough_gpd, how='difference')

            except AttributeError:
                pass

        else:
            self.sabkha_gpd = None


        bounds = self.source_block_gpd.geometry.bounds.iloc[0].to_list()
        self.sw_origin = (bounds[0], bounds[1])

        # patch: assuming azimuth is zero
        if PROJECT_AZIMUTH == 0:
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
            azimuth = PROJECT_AZIMUTH

        else:
            azimuth = np.pi * test_azimuth / 180
            swath_origin = (10, 20)

        swath_width_dx = RLS * np.cos(azimuth)
        swath_width_dy = -RLS * np.sin(azimuth)
        swath_length_dx = SWATH_LENGTH * np.sin(azimuth)
        swath_length_dy = SWATH_LENGTH * np.cos(azimuth)

        sw_ll = (swath_origin[0] + (swath_nr - SWATH_1) * swath_width_dx,
                 swath_origin[1] + (swath_nr - SWATH_1) * swath_width_dy)
        sw_lr = (sw_ll[0] + swath_width_dx, sw_ll[1] + swath_width_dy)
        sw_tl = (sw_ll[0] + swath_length_dx, sw_ll[1] + swath_length_dy)
        sw_tr = (sw_tl[0] + swath_width_dx, sw_tl[1] + swath_width_dy)

        return sw_ll, sw_lr, sw_tr, sw_tl

    @staticmethod
    def create_sw_gpd(cornerpoints):
        return GeoDataFrame(
            crs=settings.EPSG, geometry=GeoSeries(Polygon(cornerpoints)))

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
        shapefile_gpd.to_crs(f'EPSG:{settings.EPSG}')
        return shapefile_gpd[shapefile_gpd['geometry'].notnull()]

    def plot_gpd(self, shape_gpd, color='black'):
        shape_gpd.plot(ax=self.ax, facecolor='none', edgecolor=color, linewidth=0.5)

    def swath_intersection(self, swath_gpd, terrain_gpd, color):

        try:
            terrain_gpd = overlay(swath_gpd, terrain_gpd, how='intersection')
            terrain_area = sum(terrain_gpd.geometry.area.to_list())/ 1e6
            if terrain_area > 0 and terrain_gpd['geometry'].all():
                self.plot_gpd(terrain_gpd, color)

        except (AttributeError, IndexError, KeyError):
            terrain_area = 0

        return terrain_area

    @staticmethod
    def convert_area_to_vps(areas):
        vp_theor = int(areas['area'] * 1000 / SLS_FLAT * 1000 / SPS_FLAT)
        vp_flat = int(areas['area_flat'] * 1000 / SLS_FLAT * 1000 / SPS_FLAT)
        vp_rough = int(areas['area_rough'] * 1000 / SLS_FLAT * 1000 / SPS_FLAT)
        vp_facilities = int(areas['area_facilities'] * 1000 / SLS_FLAT * 1000 / SPS_FLAT)
        vp_dune_src = int(areas['area_dunes'] * 1000 / SLS_SAND * 1000 / SPS_SAND)
        vp_dune_rcv = (
            int(areas['area_dunes'] * 1000 / RLS_SAND * 1000 / SPS_SAND)
            if settings.source_on_receivers else 0.0
        )
        vp_dune = int(vp_dune_src + vp_dune_rcv)
        vp_sabkha = int(areas['area_sabkha'] * 1000 / SLS_FLAT * 1000 / SPS_FLAT)
        vp_actual = int(vp_flat + vp_rough + vp_facilities + vp_dune + vp_sabkha)
        vp_dozer_km = vp_dune_src * SPS_SAND / 1000
        vp_skips = vp_theor - vp_flat - vp_rough - vp_facilities - vp_dune - vp_sabkha

        if areas['area'] > 0:
            vp_density = vp_actual / areas['area']
            ctm = (
                ctm_constant *
                   (vp_flat * flat_terrain +
                    vp_rough * rough_terrain +
                    vp_facilities * facilities_terrain +
                    vp_dune * dunes_terrain +
                    vp_sabkha * sabkha_terrain) / vp_actual
                )
        else:
            vp_density = np.nan
            ctm = np.nan

        return {
            'theor': vp_theor,
            'flat': vp_flat,
            'rough': vp_rough,
            'facilities': vp_facilities,
            'dune_src': vp_dune_src,
            'dune_rcv': vp_dune_rcv,
            'dunes': vp_dune,
            'sabkha': vp_sabkha,
            'skips': vp_skips,
            'actual': vp_actual,
            'doz_km': vp_dozer_km,
            'density': vp_density,
            'ctm': ctm,
        }

    def calc_src_stats(self, swath_nr):
        #pylint: disable=line-too-long
        swath_gpd = self.create_sw_gpd(
            self.get_envelop_swath_cornerpoint(self.sw_origin, swath_nr))
        swath_gpd = overlay(self.source_block_gpd, swath_gpd, how='intersection')

        areas = {}
        areas['swath'] = swath_nr
        areas['area'] = sum(swath_gpd.geometry.area.to_list())/ 1e6
        areas['area_rough'] = self.swath_intersection(swath_gpd, self.rough_gpd, 'cyan')
        areas['area_facilities'] = self.swath_intersection(swath_gpd, self.facilities_gpd, 'red')
        areas['area_dunes'] = self.swath_intersection(swath_gpd, self.dunes_gpd, 'yellow')
        areas['area_sabkha'] = self.swath_intersection(swath_gpd, self.sabkha_gpd, 'brown')
        areas['area_flat'] = (
            areas['area'] - areas['area_rough'] - areas['area_facilities'] -
            areas['area_dunes'] - areas['area_sabkha']
        )
        points = self.convert_area_to_vps(areas)

        self.swath_src_stats = self.swath_src_stats.append(
            {**areas, **points}, ignore_index=True
        )
        return areas

    @staticmethod
    def convert_area_to_rcv(areas, src_dozer_km):
        rcv_theor = int(areas['area'] * 1000 / RLS * 1000 / RPS)
        rcv_flat = int(areas['area_flat'] * 1000 / RLS * 1000 / RPS)
        rcv_dune = int(areas['area_dunes'] * 1000 / RLS * 1000 / RPS)
        rcv_actual = int(rcv_flat + rcv_dune)
        rcv_dozer_km = rcv_dune * RPS / 1000 * (RLS / RLS_SAND)
        rcv_density = rcv_actual / areas['area'] if areas['area'] > 0 else np.nan


        return {
            'theor': rcv_theor,
            'flat': rcv_flat,
            'dunes': rcv_dune,
            'actual': rcv_actual,
            'doz_km': rcv_dozer_km,
            'density': rcv_density,
            'doz_total_km': src_dozer_km + rcv_dozer_km,
        }

    def calc_rcv_stats(self, swath_nr, src_dozer_km):
        swath_gpd = self.create_sw_gpd(
            self.get_envelop_swath_cornerpoint(self.sw_origin, swath_nr))
        swath_gpd = overlay(self.receiver_block_gpd, swath_gpd, how='intersection')

        areas = {}
        areas['swath'] = swath_nr
        areas['area'] = sum(swath_gpd.geometry.area.to_list())/ 1e6
        areas['area_dunes'] = self.swath_intersection(swath_gpd, self.dunes_gpd, 'yellow')
        areas['area_flat'] = areas['area'] - areas['area_dunes']

        points = self.convert_area_to_rcv(areas, src_dozer_km)

        self.swath_rcv_stats = self.swath_rcv_stats.append(
            {**areas, **points}, ignore_index=True)

        return areas

    def swath_range(self, swath_reverse=False):
        ''' calculate ranges depending on swath order is reversed
        '''
        if swath_reverse:
            return range(self.total_swaths + SWATH_1 - 1, SWATH_1 - 1, -1)

        return range(SWATH_1, self.total_swaths + SWATH_1)

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
            total_src_dune_area += areas_src['area_dunes']

            areas_rcv = self.calc_rcv_stats(
                swath_nr,
                self.swath_src_stats[self.swath_src_stats['swath'] == swath_nr]['doz_km'].sum()
            )
            total_rcv_area += areas_rcv['area']
            total_rcv_dune_area += areas_rcv['area_dunes']

            self.print_status(swath_nr, areas_src)

        self.print_totals(total_src_area, total_src_sabkha_area, total_src_dune_area,
                          total_rcv_area, total_rcv_dune_area)

    def aggregate_prod_stats(self, prod_day, swaths, prod):
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
            'vp_flat': prod.flat,
            'vp_rough': prod.rough,
            'vp_facilities': prod.facilities,
            'vp_sabkha': prod.sabkha,
            'vp_dunes': prod.dunes,
            'vp_prod': prod.prod,
            'doz_km': prod.doz_km,
            'doz_total_km': prod.doz_total_km,
            'layout_flat': prod.layout_flat,
            'layout_dune': prod.layout_dune,
            'layout': prod.layout_flat + prod.layout_dune,
            'pickup_flat': prod.pickup_flat,
            'pickup_dune': prod.pickup_dune,
            'pickup': prod.pickup_flat + prod.pickup_dune,
        }
        self.prod_stats = self.prod_stats.append(results, ignore_index=True)

    @staticmethod
    def init_production(production, vp_prod, layout, dozer_km):
        production.doz_km = dozer_km
        production.prod = vp_prod[5]
        production.flat = vp_prod[0]
        production.rough = vp_prod[1]
        production.facilities = vp_prod[2]
        production.dunes = vp_prod[3]
        production.sabkha = vp_prod[4]
        production.layout_flat = layout[0]
        production.layout_dune = layout[1]
        production.pickup_flat = layout[2]
        production.pickup_dune = layout[3]

        return production

    @staticmethod
    def sum_production(production, vp_prod, layout, dozer_km):
        production.doz_km += dozer_km
        production.prod += vp_prod[5]
        production.flat += vp_prod[0]
        production.rough += vp_prod[1]
        production.facilities += vp_prod[2]
        production.dunes += vp_prod[3]
        production.sabkha += vp_prod[4]
        production.layout_flat += layout[0]
        production.layout_dune += layout[1]
        production.pickup_flat += layout[2]
        production.pickup_dune += layout[3]

        return production

    def calc_prod_stats(self, swath_reverse=False):
        production = Production(*[0]*12)

        def sign():
            if swath_reverse:
                return -1
            return 1

        # determine dozer and receiver lead required before start of production
        # on day zero
        if swath_reverse:
            start_swath = SWATH_1 + self.total_swaths
            sw_doz_range = [sw for sw in range(
                start_swath, start_swath - LEAD_DOZER, -1)]
            sw_rcv_range = [sw for sw in range(
                start_swath, start_swath - LEAD_RECEIVER, -1)]

        else:
            start_swath = SWATH_1
            sw_doz_range = [sw for sw in range(
                start_swath, start_swath + LEAD_DOZER)]
            sw_rcv_range = [sw for sw in range(
                start_swath, start_swath + LEAD_RECEIVER)]

        doz_src_km = self.swath_src_stats[
            self.swath_src_stats['swath'].isin(sw_doz_range)]['doz_km'].sum()
        doz_rcv_km = self.swath_rcv_stats[
            self.swath_rcv_stats['swath'].isin(sw_doz_range)]['doz_km'].sum()
        production.doz_km = doz_src_km + doz_rcv_km
        production.doz_total_km = production.doz_km

        production.layout_flat = self.swath_rcv_stats[
            self.swath_rcv_stats['swath'].isin(sw_rcv_range)]['flat'].sum()
        production.layout_dune = self.swath_rcv_stats[
            self.swath_rcv_stats['swath'].isin(sw_rcv_range)]['dunes'].sum()

        self.aggregate_prod_stats(0, [], production)

        prod_day = 1
        day_duration = 0
        day_swaths = []
        production = self.init_production(production, np.zeros(6), np.zeros(4), 0)
        dozer_swath = sw_doz_range[-1] + sign()
        rcv_swath_front = sw_rcv_range[-1] + sign()
        rcv_swath_back = sw_rcv_range[-1] - sign() * ACTIVE_LINES

        for swath in self.swath_range(swath_reverse=swath_reverse):

            # get vp production
            result_src = self.swath_src_stats[self.swath_src_stats['swath'] == swath]
            vp_prod = np.array([
                result_src['flat'].sum(),
                result_src['rough'].sum(),
                result_src['facilities'].sum(),
                result_src['dunes'].sum(),
                result_src['sabkha'].sum(),
                result_src['actual'].sum()
            ])

            vp_prod = vp_prod * REPEAT_FACTOR
            ctm = result_src['ctm'].sum() * REPEAT_FACTOR

            if ctm == 0:
                sw_duration = 0
            else:
                sw_duration = vp_prod[5] / ctm

            day_duration += sw_duration

            # get receiver production
            layout = self.swath_rcv_stats[self.swath_rcv_stats['swath'] == rcv_swath_front]  #pylint: disable=line-too-long
            pickup = self.swath_rcv_stats[self.swath_rcv_stats['swath'] == rcv_swath_back]
            layout_pickup = np.array([
                layout['flat'].sum(),
                layout['dunes'].sum(),
                pickup['flat'].sum(),
                pickup['dunes'].sum(),
            ])

            # get dozer km
            doz_src_km = self.swath_src_stats[
                self.swath_src_stats['swath'] == dozer_swath]['doz_km'].sum()
            doz_rcv_km = self.swath_rcv_stats[
                self.swath_rcv_stats['swath'] == dozer_swath]['doz_km'].sum()
            sw_doz_km = doz_src_km + doz_rcv_km

            if day_duration > 1:
                # swath is overflowing to next day, assume swath can only overflow 1 day!
                portion_tomorrow = (day_duration - 1) / sw_duration
                portion_today = 1 - portion_tomorrow
                production = self.sum_production(
                    production, vp_prod * portion_today, layout_pickup * portion_today,
                    sw_doz_km * portion_today)

                day_swaths.append(swath)

                production.doz_total_km += production.doz_km
                self.aggregate_prod_stats(prod_day, day_swaths, production)

                # set up for next day
                prod_day += 1
                production = self.init_production(
                    production, vp_prod * portion_tomorrow,
                    layout_pickup * portion_tomorrow, sw_doz_km * portion_tomorrow)

                day_duration = production.prod / ctm
                day_swaths = [swath]

            else:
                production = self.sum_production(
                    production, vp_prod, layout_pickup, sw_doz_km)

                day_swaths.append(swath)

            dozer_swath += sign()
            rcv_swath_front += sign()
            rcv_swath_back += sign()

        production.doz_total_km += production.doz_km
        self.aggregate_prod_stats(prod_day, day_swaths, production)

        # TODO add final pickup

    @staticmethod
    def print_status(swath_nr, areas):
        ''' print a status line '''
        print(f'swath: {swath_nr}, '
              f'area: {areas["area"]:.2f}, '
              f'sabkha area: {areas["area_sabkha"]:.2f}, '
              f'dune area: {areas["area_dunes"]:.2f}\r', end='')

    def print_totals(self, total_src_area, total_src_sabkha_area, total_src_dune_area,
                     total_rcv_area, total_rcv_dune_area):
        # check if totals match the sum of the swathss
        area_src_block = sum(self.source_block_gpd.geometry.area.to_list()) / 1e6
        print(f'\n\narea source block: {area_src_block}')
        print(f'area source block: {total_src_area}\n')

        try:
            area_sabkha = sum(self.sabkha_gpd.geometry.area.to_list()) / 1e6
            print(f'area sabkha: {area_sabkha}')
            print(f'area source sabkha: {total_src_sabkha_area}\n')
        except AttributeError:
            pass

        try:
            area_dunes = sum(self.dunes_gpd.geometry.area.to_list()) / 1e6
            print(f'area dunes: {area_dunes}')
            print(f'area source dunes: {total_src_dune_area}\n')
        except AttributeError:
            pass

        area_rcv_block = sum(self.receiver_block_gpd.geometry.area.to_list()) / 1e6
        print(f'area receiver block: {area_rcv_block}')
        print(f'area receiver block: {total_rcv_area}\n')

        if area_dunes > 0:
            print(f'area dunes: {area_dunes}')
            print(f'area dunes: {total_rcv_dune_area}')

    def stats_to_excel(self, file_name):
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')  #pylint: disable=abstract-class-instantiated
        workbook = writer.book

        # sum the columns
        self.swath_src_stats.loc['Totals'] = self.swath_src_stats.sum()
        self.swath_rcv_stats.loc['Totals'] = self.swath_rcv_stats.sum()
        self.prod_stats.loc['Totals'] = self.prod_stats.sum()

        # write to excel
        self.swath_src_stats.to_excel(writer, sheet_name='Source', index=False)
        self.swath_rcv_stats.to_excel(writer, sheet_name='Receiver', index=False)
        self.prod_stats.to_excel(writer, sheet_name='Prod', index=False)

        ws_charts = workbook.add_worksheet('Charts')
        total_swaths = len(self.swath_src_stats) - 1
        total_production_days = len(self.prod_stats) - 1
        name_font_title = {'name': 'Arial', 'size': 10}

        # Chart 1: VP by type
        # format ['sheet', first_row, first_column, last_row, last_column]
        chart1 = workbook.add_chart({'type': 'line'})
        for col in [7, 8, 9, 10, 13, 14, 16]:
            chart1.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
            })
        chart1.set_title({'name': settings.title_chart + ' - VP by type',
                          'name_font': name_font_title,})
        chart1.set_x_axis({'name': 'swath'})
        chart1.set_y_axis({'name': 'vp'})
        chart1.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B2', chart1)

        # Chart 2: CTM by swath
        chart2 = workbook.add_chart({'type': 'line'})
        for col in [19]:
            chart2.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
            })
        chart2.set_title({'name': settings.title_chart + ' - CTM by swath',
                          'name_font': name_font_title,})
        chart2.set_x_axis({'name': 'swath'})
        chart2.set_y_axis({'name': 'vp'})
        chart2.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B18', chart2)

        # Chart 3: Source density by swath
        chart3 = workbook.add_chart({'type': 'line'})
        for col in [18]:
            chart3.add_series({
                'name': ['Source', 0, col],
                'categories': ['Source', 1, 0, total_swaths, 0],
                'values': ['Source', 1, col, total_swaths, col],
            })
        chart3.set_title({'name': settings.title_chart + ' - Source density by swath',
                          'name_font': name_font_title,})
        chart3.set_x_axis({'name': 'swath'})
        chart3.set_y_axis({'name': 'vp'})
        chart3.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('B34', chart3)

        # Chart 4: dozer km per day
        chart4 = workbook.add_chart({'type': 'line'})
        for col in [9]:
            chart4.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart4.set_title({'name': settings.title_chart + ' - Dozer km',
                          'name_font': name_font_title,})
        chart4.set_x_axis({'name': 'Day'})
        chart4.set_y_axis({'name': 'km'})
        chart4.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('J2', chart4)

        # # Chart 5: dozer cumulative km
        chart5 = workbook.add_chart({'type': 'line'})
        for col in [10]:
            chart5.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart5.set_title({'name': settings.title_chart + ' - Cumul. dozer km',
                          'name_font': name_font_title,})
        chart5.set_x_axis({'name': 'Day'})
        chart5.set_y_axis({'name': 'km'})
        chart5.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('J18', chart5)

        # Chart 6: Production
        chart6 = workbook.add_chart({'type': 'line'})
        for col in [8]:
            chart6.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart6.set_title({'name': settings.title_chart + ' - Production',
                          'name_font': name_font_title,})
        chart6.set_x_axis({'name': 'Day'})
        chart6.set_y_axis({'name': 'vp'})
        chart6.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('R2', chart6)

        # Chart 7: Layout
        chart7 = workbook.add_chart({'type': 'line'})
        for col in [11, 12, 13]:
            chart7.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart7.set_title({'name': settings.title_chart + ' - Layout',
                          'name_font': name_font_title,})
        chart7.set_x_axis({'name': 'Day'})
        chart7.set_y_axis({'name': 'Stations'})
        chart7.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('R18', chart7)

        # Chart 8: Pickup
        chart8 = workbook.add_chart({'type': 'line'})
        for col in [14, 15, 16]:
            chart8.add_series({
                'name': ['Prod', 0, col],
                'categories': ['Prod', 1, 0, total_production_days, 0],
                'values': ['Prod', 1, col, total_production_days, col],
            })
        chart8.set_title({'name': settings.title_chart + ' - Pickup',
                          'name_font': name_font_title,})
        chart8.set_x_axis({'name': 'Day'})
        chart8.set_y_axis({'name': 'vp'})
        chart8.set_legend({'position': 'bottom'})
        ws_charts.insert_chart('R34', chart8)

        # ... and save it all to excel
        ws_charts.activate()
        writer.save()


def main():
    gis_calc = GisCalc()
    gis_calc.swaths_stats(swath_reverse=settings.swath_reverse)
    gis_calc.calc_prod_stats(swath_reverse=settings.swath_reverse)
    gis_calc.stats_to_excel(settings.excel_file)

    plt.show()


if __name__ == '__main__':
    main()
