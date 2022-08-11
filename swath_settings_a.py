''' project settings Central Oman - Block A
'''
import datetime
from dataclasses import dataclass, field
from pathlib import Path


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
    sls_infill: float = 375
    sps_infill: float = 25.0
    access_spacing: float = 1000.0
    project_azimuth: float = 0.0
    repeat_factor: int = 1
    swath_length: float = 30_000.0
    swath_1: int = 100
    active_lines: int = 40
    dozer_buffer: float = 5000.0
    nodes_assigned: int = 48_100
    nodes_spare: int = 500
    nodes_sand_advance_days: float = 1.6
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
    prod_cap: dict[tuple, float] = field(default_factory=lambda: {(100, 800): None})
    ctm_constant: float = field(init=False)
    lead_receiver: int = field(init=False)
    lead_dozer: int = field(init=False)
    excel_file: str = './swath_stats_central_oman_a_new.xlsx'
    title_chart: str = 'Central Oman - Block A'
    start_date: datetime.date = datetime.date(2022, 5, 8)
    EPSG: int = 3440  # PSD93_UTM40
    project_base_folder: Path = Path('D:/OneDrive/Work/PDO/Central Oman 2022/6 Mapping/4 shape files')
    shapefile_src: Path = field(init=False)
    shapefile_rcv: Path = field(init=False)
    shapefile_rough: Path = field(init=False)
    shapefile_facilities: Path = field(init=False)
    shapefile_dune: Path = field (init=False)
    shapefile_sabkha: Path = field(init=False)
    shapefile_rcv_infill: Path = field(init=False)
    shapefile_src_infill: Path = field(init=False)

    def __post_init__(self):
        self.ctm_constant = 3600 / (
            self.sweep_time + self.move_up_time) * self.hours_day * self.number_vibes
        self.lead_receiver = int(self.active_lines * self.repeat_factor / 2)
        self.lead_dozer = self.lead_receiver + int(self.dozer_buffer / self.rls_flat)
        self.shapefile_src = (
            self.project_base_folder / 'boundaries/Central Oman Block_A_S.shp'
        )
        self.shapefile_rcv = (
            self.project_base_folder / 'boundaries/Central Oman Block_A_R.shp'
        )
        self.shapefile_rcv_infill = (
            self.project_base_folder / 'dunes/dune_infill_final.shp'
        )
        self.shapefile_src_infill = None #(
            #self.project_base_folder / 'terrain/src_infill_a.shp'
        #)
        self.shapefile_dune = (
            self.project_base_folder / 'terrain/dunes_a_v2.shp'
        )
        self.shapefile_rough = (
            self.project_base_folder / 'terrain/rough_a.shp'
        )
        self.shapefile_facilities = (
            self.project_base_folder / 'terrain/facilities_a.shp'
        )
        self.shapefile_sabkha = None
