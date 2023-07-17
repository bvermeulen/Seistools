""" Example project settings Project_Name Client
    Change name to: swath_settings.py
"""
import datetime
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    rls_flat: float = 100.0
    rps_flat: float = 25.0
    rls_sand: float = 100.0
    rps_sand: float = 25.0
    sls_flat: float = 25.0
    sps_flat: float = 25.0
    sls_cs1: float = 25.0
    sps_cs1: float = 25.0
    cs_cs1: float = 0.75
    sls_cs2: float = 25.0
    sps_cs2: float = 25.0
    cs_cs2: float = 0.50
    sls_sand: float = 200.0
    sps_sand: float = 25.0
    cs_sand: float = 1.0
    rls_infill: float = 1
    rps_infill: float = 1
    sls_infill: float = 1
    sps_infill: float = 1
    cs_infill: float = 1.0
    access_spacing: float = 1000.0
    project_azimuth: float = 0.0
    repeat_factor: int = 1
    swath_length: float = 100_000.0
    swath_1: int = 100
    dozer_buffer: float = 5000
    active_lines: int = 40
    nodes_assigned: int = 30_000
    nodes_spare: int = 500
    nodes_sand_advance_days: float = 1
    swath_reverse: bool = False
    source_on_receivers: bool = False
    rl_dozed: bool = False
    access_dozed: bool = True
    sweep_time: float = 9.0
    move_up_time: float = (
        19.0  # This is an estimated weighted average for 3 spacings 25, 50 and 75 meter
    )
    number_vibes: int = 10
    flat_terrain: float = 0.85
    rough_terrain: float = 0.60
    facilities_terrain: float = 0.55
    dunes_terrain: float = 0.60
    sabkha_terrain: float = 0.60
    flat_skip_perc: float = 0.00  # 750 meter offset skip compensation
    rough_skip_perc: float = 0.00  # 750 meter offset skip compensation
    facilities_skip_perc: float = 0.00  # 750 meter offset skip compensation
    dunes_skip_perc: float = 0.00
    sabkha_skip_perc: float = 0.00
    hours_day: float = 24.0
    prod_cap: dict[tuple, float | None] = field(
        default_factory=lambda: {(100, 1100): None}
    )
    ctm_constant: float = field(init=False)
    lead_receiver: int = field(init=False)
    lead_dozer: int = field(init=False)
    excel_file: str = "./swath_project.xlsx"
    title_chart: str = "Project"
    start_date: datetime.date = datetime.date(2023, 12, 15)
    EPSG: int = 3440  # PSD93_UTM40
    project_base_folder: Path = Path(
        "D:/OneDrive/Work/Client/Project/6 Mapping/4 shape files"
    )
    shapefile_src: Path = field(init=False)
    shapefile_rcv: Path = field(init=False)
    shapefile_cs1: Path = field(init=False)
    shapefile_cs2: Path = field(init=False)
    shapefile_dune: Path | None = field(init=False)
    shapefile_rough: Path | None = field(init=False)
    shapefile_facilities: Path | None = field(init=False)
    shapefile_sabkha: Path | None = field(init=False)
    shapefile_rcv_infill: Path | None = field(init=False)
    shapefile_src_infill: Path | None = field(init=False)

    def __post_init__(self) -> None:
        self.ctm_constant = (
            3600
            / (self.sweep_time + self.move_up_time)
            * self.hours_day
            * self.number_vibes
        )
        self.lead_receiver = int(self.active_lines * self.repeat_factor / 2)
        self.lead_dozer = self.lead_receiver + int(self.dozer_buffer / self.rls_flat)
        self.shapefile_rcv = (
            self.project_base_folder / "boundaries/project boundary.shp"
        )
        self.shapefile_src = (
            self.project_base_folder / "boundaries/project boundary.shp"
        )
        self.shapefile_cs1 = (
            self.project_base_folder / "boundaries/project boundary.shp"
        )
        self.shapefile_cs2 = None
        self.shapefile_rcv_infill = None
        self.shapefile_src_infill = None
        self.shapefile_facilities = None
        self.shapefile_rough = None
        self.shapefile_dune = self.project_base_folder / "terrain/dune_medium.shp"
        self.shapefile_sabkha = None
