''' application to calculate swath statistics based on shape files
    set parameters in the module swath_settings.py

    howdimain @2023
    bruno.vermeulen@hotmail.com
'''
from dataclasses import dataclass
import datetime
import numpy as np
import pandas as pd
import warnings
from typing import Literal, Any
from swath_settings import Config
from swath_gis import Gis
from swath_output import OutputMixin
''' extract statistis based on GIS geometries
'''
warnings.filterwarnings('ignore')
cfg = Config()
xy = tuple[float, float]

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
    layout_dune: float
    layout_infill: float
    pickup_flat: float
    pickup_dune: float
    pickup_infill: float


class SwathProdCalc(OutputMixin):

    def __init__(self) -> None:

        self.index = 0
        self.total_swaths = 0
        self.gis = Gis(cfg)

        bounds = self.gis.get_bounds(self.gis.source_block_gpd)
        self.sw_origin = (bounds[0], bounds[1])
        self.src_infill = (
            True if self.gis.src_infill_gpd is not None and not
            (cfg.sls_infill < 0.01 or cfg.sps_infill < 0.01) else False
        )
        self.rcv_infill = (
            True if self.gis.rcv_infill_gpd is not None and not
            (cfg.rls_infill < 0.01 or cfg.rps_infill < 0.01) else False
        )

        if not self.src_infill:
            self.swath_src_stats = pd.DataFrame(columns=[
                'swath', 'area', 'area_flat', 'area_rough', 'area_facilities', 'area_dunes',
                'area_sabkha', 'theor', 'flat', 'rough', 'facilities', 'dunes', 'sabkha',
                'skips', 'actual', 'dunes_src', 'dunes_rcv', 'doz_km', 'density', 'ctm'
            ])

        else:
            self.swath_src_stats = pd.DataFrame(columns=[
                'swath', 'area', 'area_flat', 'area_flat_infill', 'area_rough', 'area_rough_infill',
                'area_facilities', 'area_facilities_infill', 'area_dunes', 'area_dunes_infill',
                'area_sabkha', 'area_sabkha_infill', 'theor', 'flat', 'rough', 'facilities', 'dunes',
                'sabkha', 'skips', 'actual', 'flat_infill', 'rough_infill', 'facilities_infill',
                'dunes_src', 'dunes_rcv', 'dunes_infill', 'sabkha_infill', 'doz_km', 'density', 'ctm'
            ])

        if not self.rcv_infill:
            self.swath_rcv_stats = pd.DataFrame(columns=[
                'swath', 'area', 'area_flat', 'area_dunes', 'theor', 'flat',
                'dunes', 'actual', 'doz_km', 'density'
            ])

        else:
            self.swath_rcv_stats = pd.DataFrame(columns=[
                'swath', 'area', 'area_flat', 'area_dunes', 'area_infill', 'theor', 'flat',
                'dunes', 'infill', 'actual', 'doz_km', 'density'
            ])

        self.prod_stats = pd.DataFrame(columns=[
            'prod_day', 'date', 'swath_first', 'swath_last', 'vp_flat', 'vp_rough',
            'vp_facilities', 'vp_dunes', 'vp_sabkha', 'vp_prod', 'doz_km', 'doz_total_km',
            'layout_flat', 'layout_dune', 'layout_infill', 'layout', 'pickup_flat',
            'pickup_dune', 'pickup_infill', 'pickup', 'nodes_assigned', 'nodes_patch',
            'nodes_dune_advance', 'nodes_infill', 'nodes_ts', 'nodes_total_use', 'nodes_spare'
        ])

        # patch: assuming azimuth is zero
        if cfg.project_azimuth == 0:
            self.total_swaths = int(round((bounds[2] - bounds[0]) / cfg.rls_flat)) + 1

        else:
            self.total_swaths = int(input('Total number of swaths: '))

    @staticmethod
    def get_envelop_swath_cornerpoint(swath_origin: xy, swath_nr: int) -> tuple[xy, xy, xy, xy]:
        ''' get the corner points of the envelope of the swath, i.e. length
            of swath > actual swath length, so any shape of swath will be captured
            when intersected with the actual block

            azimuth is the angle between northing and receiver line in positive direction

            arguments:
                swath_origin: tuple (x, y), coordinates of origin point
                swath_nr: integer [swath_1, n], counting from left to right
                          (azimuth < 90)
                test_azimuth: float in degrees [0, 360], can be provided for tests

            returns:
                tuple with 4 corner point tuples of swath swath_nr (ll, lr, tr, tl)
        '''
        assert swath_nr > 0, 'swath_nr must be [swath_1, n]'

        swath_width_dx = cfg.rls_flat * np.cos(cfg.project_azimuth)
        swath_width_dy = -cfg.rls_flat * np.sin(cfg.project_azimuth)
        swath_length_dx = cfg.swath_length * np.sin(cfg.project_azimuth)
        swath_length_dy = cfg.swath_length * np.cos(cfg.project_azimuth)

        sw_ll = (swath_origin[0] + (swath_nr - cfg.swath_1) * swath_width_dx,
                 swath_origin[1] + (swath_nr - cfg.swath_1) * swath_width_dy)
        sw_lr = (sw_ll[0] + swath_width_dx, sw_ll[1] + swath_width_dy)
        sw_tl = (sw_ll[0] + swath_length_dx, sw_ll[1] + swath_length_dy)
        sw_tr = (sw_tl[0] + swath_width_dx, sw_tl[1] + swath_width_dy)

        return sw_ll, sw_lr, sw_tr, sw_tl

    def calc_src_stats(self, swath_nr: int) -> dict[str, float|int]:
        #pylint: disable=line-too-long
        swath_gpd = self.gis.create_sw_gpd(
            self.get_envelop_swath_cornerpoint(self.sw_origin, swath_nr),
            self.gis.source_block_gpd
        )
        areas: dict[str, float|int] = {}
        areas['swath'] = swath_nr

        areas['area'] = self.gis.calc_area_and_plot(swath_gpd, None)
        rough_gpd = self.gis.intersection(swath_gpd, self.gis.rough_gpd)
        areas['area_rough'] = self.gis.calc_area_and_plot(rough_gpd, 'cyan')
        facilities_gpd = self.gis.intersection(swath_gpd, self.gis.facilities_gpd)
        areas['area_facilities'] = self.gis.calc_area_and_plot(facilities_gpd, 'red')
        dunes_gpd = self.gis.intersection(swath_gpd, self.gis.dunes_gpd)
        areas['area_dunes'] = self.gis.calc_area_and_plot(dunes_gpd, 'yellow')
        sabkha_gpd = self.gis.intersection(swath_gpd, self.gis.sabkha_gpd)
        areas['area_sabkha'] = self.gis.calc_area_and_plot(sabkha_gpd, 'brown')
        areas['area_flat'] = (
            areas['area'] - areas['area_rough'] - areas['area_facilities'] -
            areas['area_dunes'] - areas['area_sabkha']
        )
        #calculate infill if geometry is defined
        if self.src_infill:
            src_infill_swath_gpd = self.gis.intersection(swath_gpd, self.gis.src_infill_gpd)
            rough_infill_gpd = self.gis.intersection(src_infill_swath_gpd, self.gis.rough_gpd)
            areas['area_rough_infill'] = self.gis.calc_area_and_plot(rough_infill_gpd, None)
            facilities_infill_gpd = self.gis.intersection(src_infill_swath_gpd, self.gis.facilities_gpd)
            areas['area_facilities_infill'] = self.gis.calc_area_and_plot(facilities_infill_gpd, None)
            dunes_infill_gpd = self.gis.intersection(src_infill_swath_gpd, self.gis.dunes_gpd)
            areas['area_dunes_infill'] = self.gis.calc_area_and_plot(dunes_infill_gpd, None)
            dunes_infill_gpd = self.gis.intersection(src_infill_swath_gpd, self.gis.dunes_gpd)
            areas['area_dunes_infill'] = self.gis.calc_area_and_plot(dunes_infill_gpd, None)
            sabkha_infill_gpd = self.gis.intersection(src_infill_swath_gpd, self.gis.sabkha_gpd)
            areas['area_sabkha_infill'] = self.gis.calc_area_and_plot(sabkha_infill_gpd, None)
            flat_infill_gpd = self.gis.difference(
                src_infill_swath_gpd, [
                    rough_infill_gpd, facilities_infill_gpd,
                    dunes_infill_gpd, sabkha_infill_gpd
                ]
            )
            areas['area_flat_infill'] = self.gis.calc_area_and_plot(flat_infill_gpd, None)

        points = self.convert_area_to_vps(areas)

        self.swath_src_stats = self.swath_src_stats.append(
            {**areas, **points}, ignore_index=True
        )
        return areas

    def convert_area_to_vps(self, areas: dict) -> dict[str, float|int]:
        #TODO include skip percentages
        source_density = 1000 / cfg.sls_flat * 1000 / cfg.sps_flat
        vp_theor = int(areas['area'] * source_density)
        vp_flat = int(
            areas['area_flat'] * (1 - cfg.flat_skip_perc) * source_density
        )
        vp_rough = int(
            areas['area_rough'] * (1 - cfg.rough_skip_perc) * source_density
        )
        vp_facilities = int(
            areas['area_facilities'] * (1 - cfg.facilities_skip_perc) *
            source_density
        )
        vp_dunes_src = int(
            areas['area_dunes'] * (1 - cfg.dunes_skip_perc) * 1000 / cfg.sls_sand *
            1000 / cfg.sps_sand
        )
        vp_dunes_rcv = (
            int(areas['area_dunes'] * (1 - cfg.dunes_skip_perc) * 1000 / cfg.rls_sand *
            1000 / cfg.sps_sand) if cfg.source_on_receivers else 0.0
        )
        vp_dunes = int(vp_dunes_src + vp_dunes_rcv)
        vp_sabkha = int(
            areas['area_sabkha'] * (1 - cfg.sabkha_skip_perc) * source_density
        )
        vp_actual = int(vp_flat + vp_rough + vp_facilities + vp_dunes + vp_sabkha)
        vp_skips = vp_theor - vp_flat - vp_rough - vp_facilities - vp_dunes - vp_sabkha
        km_access = (
            areas['area_dunes'] * 1000 / cfg.access_spacing if cfg.access_dozed else 0.0
        )
        dozer_km_vp = vp_dunes * cfg.sps_sand / 1000 + km_access
        result_dict: dict[str, float|int] = {
            'theor': vp_theor, 'dunes_src': vp_dunes_src, 'dunes_rcv': vp_dunes_rcv,
            'doz_km': dozer_km_vp,
        }
        if self.src_infill:
            density_infill = 1000 / cfg.sls_infill * 1000 / cfg.sps_infill
            vp_flat_infill = int(
                areas['area_flat_infill'] * (1 - cfg.flat_skip_perc) *
                density_infill
            )
            vp_rough_infill = int(
                areas['area_rough_infill'] * (1 - cfg.rough_skip_perc) *
                density_infill
            )
            vp_facilities_infill = int(
                areas['area_facilities_infill'] * (1 - cfg.facilities_skip_perc) *
                density_infill
            )
            vp_dunes_infill = int(
                areas['area_dunes_infill'] * (1 - cfg.dunes_skip_perc) *
                density_infill
            )
            vp_sabkha_infill = int(
                areas['area_sabkha_infill'] * (1 - cfg.sabkha_skip_perc) *
                density_infill
            )
            result_dict.update({
                'flat_infill': vp_flat_infill, 'rough_infill': vp_rough_infill,
                'facilities_infill': vp_facilities_infill,
                'dunes_infill': vp_dunes_infill, 'sabkha_infill': vp_sabkha_infill,
            })
            infill_total = (
                vp_flat_infill + vp_rough_infill + vp_facilities_infill +
                vp_dunes_infill + vp_sabkha_infill
            )
            vp_actual += infill_total
            vp_skips -= infill_total
            vp_flat += vp_flat_infill
            vp_rough += vp_rough_infill
            vp_facilities += vp_facilities_infill
            vp_dunes += vp_dunes_infill
            vp_sabkha += vp_sabkha_infill

        if areas['area'] > 0:
            vp_density = vp_actual / areas['area']
            ctm = (
                cfg.ctm_constant * (
                   vp_flat * cfg.flat_terrain +
                   vp_rough * cfg.rough_terrain +
                   vp_facilities * cfg.facilities_terrain +
                   vp_dunes * cfg.dunes_terrain +
                   vp_sabkha * cfg.sabkha_terrain
                ) / vp_actual
            )
        else:
            vp_density = np.nan
            ctm = np.nan

        result_dict.update({
            'flat': vp_flat, 'rough': vp_rough, 'facilities': vp_facilities,
            'dunes': vp_dunes, 'sabkha': vp_sabkha, 'actual': vp_actual,
            'skips': vp_skips, 'density': vp_density, 'ctm': ctm,
        })
        return result_dict

    def calc_rcv_stats(self, swath_nr: int, src_dozer_km: float) -> dict:
        swath_gpd = self.gis.create_sw_gpd(
            self.get_envelop_swath_cornerpoint(self.sw_origin, swath_nr),
            self.gis.receiver_block_gpd
        )
        areas: dict[str, float|int] = {}
        areas['swath'] = swath_nr
        areas['area'] = self.gis.calc_area_and_plot(swath_gpd, None)
        areas['area_dunes'] = self.gis.calc_area_and_plot(
            self.gis.intersection(swath_gpd, self.gis.dunes_gpd), 'yellow'
        )
        areas['area_flat'] = areas['area'] - areas['area_dunes']
        if self.rcv_infill:
            areas['area_infill'] = self.gis.calc_area_and_plot(
                self.gis.intersection(swath_gpd, self.gis.rcv_infill_gpd), 'green'
            )
        points = self.convert_area_to_rcv(areas, src_dozer_km)

        self.swath_rcv_stats = self.swath_rcv_stats.append(
            {**areas, **points}, ignore_index=True
        )
        return areas

    def convert_area_to_rcv(self, areas: dict, dozer_km_src: float) -> dict:
        density_flat = 1000 / cfg.rls_flat * 1000 / cfg.rps_flat
        rcv_theor = int(areas['area'] * density_flat)
        rcv_flat = int(areas['area_flat'] * density_flat)
        rcv_dune = int(areas['area_dunes'] * 1000 / cfg.rls_sand * 1000 / cfg.rps_sand)
        rcv_actual = int(rcv_flat + rcv_dune)
        dozer_km_rcv = (
            int(areas['area_dunes'] * 1000 / cfg.rls_sand) if cfg.rl_dozed else 0.0
        )
        result_dict = {
            'theor': rcv_theor, 'flat': rcv_flat, 'dunes': rcv_dune, 'doz_km': dozer_km_rcv,
            'doz_total_km': dozer_km_src + dozer_km_rcv,

        }
        if self.rcv_infill:
            rcv_infill = int(areas['area_infill'] * 1000 / cfg.rls_infill * 1000 / cfg.rps_infill)
            result_dict['infill'] = rcv_infill
            rcv_actual += rcv_infill

        result_dict['actual'] = rcv_actual
        result_dict['density'] = result_dict['actual'] / areas['area'] if areas['area'] > 0 else np.nan
        return result_dict

    def swath_range(self) -> range:
        ''' calculate ranges depending on swath order is reversed
        '''
        if cfg.swath_reverse:
            return range(self.total_swaths + cfg.swath_1 - 1, cfg.swath_1 - 1, -1)

        else:
            return range(cfg.swath_1, self.total_swaths + cfg.swath_1)

    def swaths_stats(self) -> None:
        ''' loop over the swaths, calculate areas and produce
            the source and receiver stastics based on source & receiver densities
        '''
        _ = self.gis.calc_area_and_plot(self.gis.receiver_block_gpd, color='blue')
        _ = self.gis.calc_area_and_plot(self.gis.source_block_gpd, color='red')

        total_src_area, total_src_sabkha_area, total_src_dune_area = 0.0, 0.0, 0.0
        total_rcv_area, total_rcv_dune_area = 0.0, 0.0

        for swath_nr in self.swath_range():
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

        self.print_totals(
            self.gis,
            total_src_area, total_src_sabkha_area, total_src_dune_area, total_rcv_area,
            total_rcv_dune_area
        )

    def aggregate_prod_stats(self, prod_day: float, swaths: list[int], prod: Production) -> None:
        ''' aggregate stats by production day
        '''
        try:
            swath_first = swaths[0]
            swath_last = swaths[-1]

        except IndexError:
            swath_first = None
            swath_last = None

        prod_date = cfg.start_date + datetime.timedelta(days=prod_day - 1)
        results = {
            'prod_day': prod_day,
            'date': prod_date,
            'swath_first': swath_first,
            'swath_last': swath_last,
            'vp_flat': prod.flat,
            'vp_rough': prod.rough,
            'vp_facilities': prod.facilities,
            'vp_dunes': prod.dunes,
            'vp_sabkha': prod.sabkha,
            'vp_prod': prod.prod,
            'doz_km': prod.doz_km,
            'doz_total_km': prod.doz_total_km,
            'layout_flat': prod.layout_flat,
            'layout_dune': prod.layout_dune,
            'layout_infill': prod.layout_infill,
            'layout': prod.layout_flat + prod.layout_dune + prod.layout_infill,
            'pickup_flat': prod.pickup_flat,
            'pickup_dune': prod.pickup_dune,
            'pickup_infill': prod.pickup_infill,
            'pickup': prod.pickup_flat + prod.pickup_dune + prod.pickup_infill,
            'nodes_assigned': cfg.nodes_assigned,
            'nodes_patch': None,
            'nodes_dune_advance': None,
            'nodes_infill': None,
            'nodes_ts': cfg.nodes_spare,
            'nodes_total_use': None,
            'nodes_spare': None,
        }
        results = self.add_nodes_totals(results)
        self.prod_stats = self.prod_stats.append(results, ignore_index=True)

    def add_nodes_totals(self, results: dict[str, Any]) -> dict[str, Any]:
        if results['swath_last'] is None or results['swath_first'] is None:
            return results

        half_patch = int(cfg.active_lines * 0.5)
        prod_swaths = abs(results['swath_last'] - results['swath_first'])
        if results['swath_last'] >= results['swath_first']:
            sw_patch_1 = int(results['swath_first'] - half_patch - 0.5 * prod_swaths)
            sw_patch_2 = int(results['swath_last'] + half_patch + prod_swaths)
            sw_adv_1 = results['swath_last'] + half_patch + prod_swaths
            sw_adv_2 = int(
                results['swath_last'] + half_patch +
                prod_swaths * (1 + cfg.nodes_sand_advance_days)
            )
        else:
            sw_patch_1 = int(results['swath_last'] - half_patch - prod_swaths)
            sw_patch_2 = int(results['swath_first'] + half_patch + 0.5 * prod_swaths)
            sw_adv_1 = int(
                results['swath_last'] - half_patch -
                prod_swaths * (1 + cfg.nodes_sand_advance_days)
            )
            sw_adv_2 = results['swath_last'] - half_patch - prod_swaths

        sw_patch_range = [sw for sw in range(sw_patch_1, sw_patch_2 +1)]
        sw_adv_range = [sw for sw in range(sw_adv_1, sw_adv_2 +1)]

        self.print_prod(
            results['swath_first'], results['swath_last'],
            sw_patch_1, sw_patch_2,
            sw_adv_1, sw_adv_2, print_status=True
        )

        n_flat = self.swath_rcv_stats[
            self.swath_rcv_stats['swath'].isin(sw_patch_range)]['flat'].sum()
        n_dunes = self.swath_rcv_stats[
            self.swath_rcv_stats['swath'].isin(sw_patch_range)]['dunes'].sum()

        if self.rcv_infill:
            n_infill = self.swath_rcv_stats[
                self.swath_rcv_stats['swath'].isin(sw_patch_range)]['infill'].sum()
            n_advance = (
                self.swath_rcv_stats[
                    self.swath_rcv_stats['swath'].isin(sw_adv_range)]['dunes'].sum() +
                self.swath_rcv_stats[
                    self.swath_rcv_stats['swath'].isin(sw_adv_range)]['infill'].sum()
            )
        else:
            n_infill = 0
            n_advance = (
                self.swath_rcv_stats[
                    self.swath_rcv_stats['swath'].isin(sw_adv_range)]['dunes'].sum()
            )

        results['nodes_patch'] = n_flat + n_dunes
        results['nodes_infill'] = n_infill
        results['nodes_dune_advance'] = n_advance
        results['nodes_total_use'] = sum([n_flat, n_dunes, n_infill, n_advance, results['nodes_ts']])
        results['nodes_spare'] = results['nodes_assigned'] - results['nodes_total_use']
        return results

    @staticmethod
    def init_production(production: Production, vp_prod: np.ndarray, layout: np.ndarray, dozer_km: float) -> Production:
        production.doz_km = dozer_km
        production.prod = vp_prod[5]
        production.flat = vp_prod[0]
        production.rough = vp_prod[1]
        production.facilities = vp_prod[2]
        production.dunes = vp_prod[3]
        production.sabkha = vp_prod[4]
        production.layout_flat = layout[0]
        production.layout_dune = layout[1]
        production.layout_infill = layout[2]
        production.pickup_flat = layout[3]
        production.pickup_dune = layout[4]
        production.pickup_infill = layout[5]
        return production

    @staticmethod
    def sum_production(production: Production, vp_prod: np.ndarray, layout: np.ndarray, dozer_km: float) -> Production:
        production.doz_km += dozer_km
        production.prod += vp_prod[5]
        production.flat += vp_prod[0]
        production.rough += vp_prod[1]
        production.facilities += vp_prod[2]
        production.dunes += vp_prod[3]
        production.sabkha += vp_prod[4]
        production.layout_flat += layout[0]
        production.layout_dune += layout[1]
        production.layout_infill += layout[2]
        production.pickup_flat += layout[3]
        production.pickup_dune += layout[4]
        production.pickup_infill += layout[5]
        return production

    def calc_prod_stats(self) -> None:
        production = Production(*[0]*14)

        def sign() -> Literal[-1, 1]:
            return -1 if cfg.swath_reverse else 1

        # determine dozer and receiver lead required before start of production
        # on day zero
        if cfg.swath_reverse:
            start_swath = cfg.swath_1 + self.total_swaths
            sw_doz_range = [sw for sw in range(
                start_swath, start_swath - cfg.lead_dozer, -1)]
            sw_rcv_range = [sw for sw in range(
                start_swath, start_swath - cfg.lead_receiver, -1)]

        else:
            start_swath = cfg.swath_1
            sw_doz_range = [sw for sw in range(
                start_swath, start_swath + cfg.lead_dozer)]
            sw_rcv_range = [sw for sw in range(
                start_swath, start_swath + cfg.lead_receiver)]

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
        if self.rcv_infill:
            production.layout_infill = self.swath_rcv_stats[
                self.swath_rcv_stats['swath'].isin(sw_rcv_range)]['infill'].sum()

        self.aggregate_prod_stats(0, [], production)

        prod_day = 1
        day_duration = 0
        day_swaths = []
        production = self.init_production(production, np.zeros(6), np.zeros(6), 0)
        dozer_swath = sw_doz_range[-1] + sign()
        rcv_swath_front = sw_rcv_range[-1] + sign()
        rcv_swath_back = sw_rcv_range[-1] - sign() * cfg.active_lines

        for swath in self.swath_range():

            # get vp production
            result_src = self.swath_src_stats[self.swath_src_stats['swath'] == swath]
            vp_prod = np.array([
                result_src['flat'].sum(), result_src['rough'].sum(), result_src['facilities'].sum(),
                result_src['dunes'].sum(), result_src['sabkha'].sum(), result_src['actual'].sum()
            ])
            vp_prod = vp_prod * cfg.repeat_factor
            ctm = result_src['ctm'].sum() * cfg.repeat_factor
            for swath_interval, prod_cap in cfg.prod_cap.items():
                apply_prod_cap = (
                    prod_cap and swath_interval[0] <= swath <= swath_interval[1] and
                    ctm > prod_cap
                )
                ctm = prod_cap if apply_prod_cap else ctm

            sw_duration = vp_prod[5] / ctm if ctm > 0 else 0
            day_duration += sw_duration

            # get receiver production
            layout = self.swath_rcv_stats[self.swath_rcv_stats['swath'] == rcv_swath_front]
            pickup = self.swath_rcv_stats[self.swath_rcv_stats['swath'] == rcv_swath_back]
            if self.rcv_infill:
                layout_pickup = np.array([
                    layout['flat'].sum(), layout['dunes'].sum(), layout['infill'].sum(),
                    pickup['flat'].sum(), pickup['dunes'].sum(), pickup['infill'].sum(),
                ])

            else:
                layout_pickup = np.array([
                    layout['flat'].sum(), layout['dunes'].sum(), 0,
                    pickup['flat'].sum(), pickup['dunes'].sum(), 0,
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
                    sw_doz_km * portion_today
                )
                day_swaths.append(swath)

                production.doz_total_km += production.doz_km
                self.aggregate_prod_stats(prod_day, day_swaths, production)

                # set up for next day
                prod_day += 1
                production = self.init_production(
                    production, vp_prod * portion_tomorrow,
                    layout_pickup * portion_tomorrow, sw_doz_km * portion_tomorrow
                )
                day_duration = production.prod / ctm
                day_swaths = [swath]

            else:
                production = self.sum_production(
                    production, vp_prod, layout_pickup, sw_doz_km
                )
                day_swaths.append(swath)

            dozer_swath += sign()
            rcv_swath_front += sign()
            rcv_swath_back += sign()

        production.doz_total_km += production.doz_km
        self.aggregate_prod_stats(prod_day, day_swaths, production)

        # TODO add final pickup

    def plot_map(self) -> None:
        self.gis.plot()


def main() -> None:
    swath_prod_calc = SwathProdCalc()
    swath_prod_calc.swaths_stats()
    swath_prod_calc.calc_prod_stats()
    swath_prod_calc.stats_to_excel(cfg)
    swath_prod_calc.plot_map()


if __name__ == '__main__':
    main()
