''' project settings Central Oman - Block A
'''
import datetime
from dataclasses import dataclass, field
from pathlib import Path
import geopandas as gpd
from geopandas import overlay


@dataclass
class Config:
    rls_flat: float = 200.0
    rps_flat: float = 25.0
    rls_sand: float = 200.0
    rps_sand: float = 25.0
    sls_flat: float = 37.5
    sps_flat: float = 25.0
    sls_sand: float = 375.0
    sps_sand: float = 25.0
    rls_infill: float = 200.0
    rps_infill: float = 25.0
    access_spacing: float = 1000.0
    project_azimuth: float = 0.0
    repeat_factor: int = 1
    swath_length: float = 120_000.0  # length > length of block
    swath_1: int = 100
    active_lines: int = 50
    dozer_buffer: float = 5000.0
    nodes_assigned: int = 48_100
    nodes_spare: int = 500
    swath_reverse: bool = True
    source_on_receivers: bool = False
    rl_dozed: bool = False
    access_dozed: bool = True
    sweep_time: float = 9.0
    move_up_time: float = 17.0
    number_vibes: int = 10
    flat_terrain: float = 0.85
    rough_terrain: float = 0.60
    facilities_terrain: float = 0.55
    dunes_terrain: float = 0.60
    sabkha_terrain: float = 0.60
    hours_day: float = 24.0
    prod_cap: dict[tuple, float] = field(default_factory=lambda: {(100, 800):  None})
    ctm_constant: float = field(init=False)
    lead_receiver: int = field(init=False)
    lead_dozer: int = field(init=False)
    excel_file: str = './swath_stats_central_oman_a_new.xlsx'
    title_chart: str = 'Central Oman - Block A'
    start_date: datetime.date = (2022, 5, 7)

    def __post_init__(self):
        self.ctm_constant = 3600 / (
            self.sweep_time + self.move_up_time) * self.hours_day * self.number_vibes
        self.lead_receiver = int(self.active_lines * self.repeat_factor / 2)
        self.lead_dozer = self.lead_receiver + int(self.dozer_buffer / self.rls)


@dataclass
class Gis:
    # GIS parameters
    EPSG: int = 3440  # PSD93_UTM40
    project_base_folder: Path = Path('D:/OneDrive/Work/PDO/Central Oman 2022/6 Mapping/4 shape files')
    shapefile_src: Path = field(init=False)
    shapefile_rcv: Path = field(init=False)
    shapefile_dune: Path = field (init=False)
    shapefile_infill: Path = field(init=False)
    shapefile_rough: Path = field(init=False)
    shapefile_facilities: Path = field(init=False)
    shapefile_sabkha: Path = field(init=False)

    def __post_init__(self):
        self.shapefile_src = (
            self.project_base_folder / 'boundaries/Central Oman Block_A_S.shp'
        )
        self.shapefile_rcv = (
            self.project_base_folder / 'boundaries/Central Oman Block_A_R.shp'
        )
        self.shapefile_dune = (
            self.project_base_folder / 'terrain/dunes_a_v2.shp'
        )
        self.shapefile_infill = (
            self.project_base_folder / 'dunes/dunes_infill.shp'
        )
        self.shapefile_rough = (
            self.project_base_folder / 'terrain/rough_a.shp'
        )
        self.shapefile_facilities = (
            self.project_base_folder / 'terrain/facilities_a.shp'
        )
        self.shapefile_sabkha = None

        self.create_gp_dataframes()

    def create_gp_dataframes(self):
        # create the geopandas data frames
        self.source_block_gpd = self.read_shapefile(self.shapefile_src)
        self.receiver_block_gpd = self.read_shapefile(self.shapefile_rcv)

        if self.shapefile_rough:
            self.rough_gpd = self.read_shapefile(self.shapefile_rough)

        else:
            self.rough_gpd = None

        if self.shapefile_facilities:
            self.facilities_gpd = self.read_shapefile(self.shapefile_facilities)

            try:
                self.facilities_gpd = overlay(
                    self.facilities_gpd, self.rough_gpd, how='difference'
                )
            except AttributeError:
                pass

        else:
            self.facilities_gpd = None

        if self.shapefile_dune:
            self.dunes_gpd = self.read_shapefile(self.shapefile_dune
            )
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

        if self.shapefile_sabkha:
            self.sabkha_gpd = self.read_shapefile(self.shapefile_sabkha)

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

        if self.shapefile_infill:
            self.infill_gpd = self.read_shapefile(self.shapefile_infill)

        else:
            self.infill_gpd = None

    def read_shapefile(self, file_name):
        ''' read a shape file and converts crs to UTM PSD93 Zone 40
            Arguments:
                file_name: string, full name of the shapefile with the
                           extension .shp
            Returns:
                geopandas dataframe with the shapefile data
        '''
        shapefile_gpd = gpd.read_file(file_name)
        shapefile_gpd.to_crs(f'EPSG:{self.EPSG}')
        return shapefile_gpd[shapefile_gpd['geometry'].notnull()]


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




