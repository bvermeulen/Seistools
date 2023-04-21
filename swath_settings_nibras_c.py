''' project settings Nibras for block C
'''
import datetime
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    rls_flat: float = 100.0
    rps_flat: float = 75.0
    rls_sand: float = 1
    rps_sand: float = 1
    sls_flat: float = 25.0
    sps_flat: float = 25.0
    sls_cs1: float = 25.0
    sps_cs1: float = 25.0
    cs_cs1: float = 0.75
    sls_cs2: float = 25.0
    sps_cs2: float = 25.0
    cs_cs2: float = 0.50
    sls_sand: float = 1
    sps_sand: float = 1
    cs_sand: float = 1.0
    rls_infill: float = 1
    rps_infill: float = 1
    sls_infill: float = 1
    sps_infill: float = 1
    cs_infill: float = 1.0
    access_spacing: float = 0
    project_azimuth: float = 0.0
    repeat_factor: int = 1
    swath_length: float = 35_000.0
    swath_1: int = 284
    dozer_buffer: float = 0
    active_lines: int = 90
    nodes_assigned: int = 30_000
    nodes_spare: int = 500
    nodes_sand_advance_days: float = 1
    swath_reverse: bool = True
    source_on_receivers: bool = False
    rl_dozed: bool = False
    access_dozed: bool = False
    sweep_time: float = 9.0
    move_up_time: float = 19.0
    number_vibes: int = 10
    flat_terrain: float = 0.85
    rough_terrain: float = 0.60
    facilities_terrain: float = 0.55
    dunes_terrain: float = 0.60
    sabkha_terrain: float = 0.60
    flat_skip_perc: float = 0.0
    rough_skip_perc: float = 0.01
    facilities_skip_perc: float = 0.05
    dunes_skip_perc: float = 0.02
    sabkha_skip_perc: float = 0.10
    hours_day: float = 24.0
    prod_cap: dict[tuple, float|None] = field(default_factory= lambda: {(100, 1100): None})
    ctm_constant: float = field(init=False)
    lead_receiver: int = field(init=False)
    lead_dozer: int = field(init=False)
    excel_file: str = './swath_nibras_c.xlsx'
    title_chart: str = 'Nibras - Block C'
    start_date: datetime.date = datetime.date(2023, 6, 4)
    EPSG: int = 3440  # PSD93_UTM40
    project_base_folder: Path = Path('D:/OneDrive/Work/PDO/Nibras 2022/6 Mapping/4 shape files')
    shapefile_src: Path = field(init=False)
    shapefile_rcv: Path = field(init=False)
    shapefile_cs1: Path = field(init=False)
    shapefile_cs2: Path = field(init=False)
    shapefile_dune: Path|None = field (init=False)
    shapefile_rough: Path|None = field(init=False)
    shapefile_facilities: Path|None = field(init=False)
    shapefile_sabkha: Path|None = field(init=False)
    shapefile_rcv_infill: Path|None = field(init=False)
    shapefile_src_infill: Path|None = field(init=False)

    def __post_init__(self) -> None:
        self.ctm_constant = 3600 / (
            self.sweep_time + self.move_up_time) * self.hours_day * self.number_vibes
        self.lead_receiver = int(self.active_lines * self.repeat_factor / 2)
        self.lead_dozer = self.lead_receiver + int(self.dozer_buffer / self.rls_flat)
        self.shapefile_rcv = (
            self.project_base_folder / 'boundaries/nibras_block_c_rcv.shp'
        )
        self.shapefile_src = (
            self.project_base_folder / 'boundaries/nibras_block_c_src.shp'
        )
        self.shapefile_cs1 = (
            self.project_base_folder / 'boundaries/block_c_75.shp'
        )
        self.shapefile_cs2 = (
            self.project_base_folder / 'boundaries/block_c_50.shp'
        )
        self.shapefile_rcv_infill = None
        self.shapefile_src_infill = None
        self.shapefile_rough = (
            self.project_base_folder / 'terrain/rough_c.shp'
        )
        self.shapefile_facilities = (
            self.project_base_folder / 'terrain/facilities_c.shp'
        )
        self.shapefile_dune = None
        self.shapefile_sabkha = None
