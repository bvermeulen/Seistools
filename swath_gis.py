import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
import geopandas as gpd
from geopandas import GeoDataFrame, GeoSeries, overlay
from swath_settings import Config

FIG_SIZE = (6, 6)
xy = tuple[float, float]

class Gis:
    ''' GIS geopandas methods for swath stastics
    '''
    def __init__(self, cfg: Config) -> None:
        self.EPSG = cfg.EPSG
        self.shapefile_src = cfg.shapefile_src
        self.shapefile_rcv = cfg.shapefile_rcv
        self.shapefile_cs1 = cfg.shapefile_cs1
        self.shapefile_cs2 = cfg.shapefile_cs2
        self.shapefile_rough = cfg.shapefile_rough
        self.shapefile_facilities = cfg.shapefile_facilities
        self.shapefile_dune = cfg.shapefile_dune
        self.shapefile_sabkha = cfg.shapefile_sabkha
        self.shapefile_rcv_infill = cfg.shapefile_rcv_infill
        self.shapefile_src_infill = cfg.shapefile_src_infill
        _, self.ax = plt.subplots(figsize=FIG_SIZE)
        self.create_gp_dataframes()

    def create_gp_dataframes(self):
        ''' create geopandas dataframes by reading the shapefiles
            terrain types will be ordered: facilities, rough, dunes, sabkha
        '''
        # create the geopandas data frames
        self.receiver_block_gpd = self.read_shapefile(self.shapefile_rcv)
        self.rcv_infill_gpd = self.read_shapefile(sf) if (sf := self.shapefile_rcv_infill) else None
        self.source_block_gpd = self.read_shapefile(self.shapefile_src)
        self.src_cs1_gpd = self.read_shapefile(sf) if (sf := self.shapefile_cs1) else None
        self.src_cs2_gpd = self.read_shapefile(sf) if (sf := self.shapefile_cs2) else None
        self.src_infill_gpd = self.read_shapefile(sf) if (sf := self.shapefile_src_infill) else None

        self.facilities_gpd = (
            self.read_shapefile(self.shapefile_facilities) if self.shapefile_facilities else None
        )

        if self.shapefile_rough:
            self.rough_gpd = self.read_shapefile(self.shapefile_rough)

            try:
                self.rough_gpd = overlay(
                    self.rough_gpd, self.facilities_gpd, how='difference'
                )
            except AttributeError:
                pass

        else:
            self.rough_gpd = None

        if self.shapefile_dune:
            self.dunes_gpd = self.read_shapefile(self.shapefile_dune
            )
            try:
                self.dune_gpd = overlay(
                    self.dune_gpd, self.rough_gpd, how='difference')

            except AttributeError:
                pass

            try:
                self.dune_gpd = overlay(
                    self.dune_gpd, self.facilities_gpd, how='difference')
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
                    self.sabkha_gpd, self.rough_gpd, how='difference')

            except AttributeError:
                pass

            try:
                self.sabkha_gpd = overlay(
                    self.sabkha_gpd, self.facilities_gpd, how='difference')

            except AttributeError:
                pass

        else:
            self.sabkha_gpd = None

    def read_shapefile(self, file_name: str) -> GeoDataFrame:
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

    @staticmethod
    def get_bounds(area_gpd: GeoDataFrame) -> list:
        bounds = area_gpd.bounds.iloc[0].to_list()
        return bounds

    def create_sw_gpd(
                self, cornerpoints: tuple[xy, xy, xy, xy],
                overlay_gpd: GeoDataFrame
            ) -> GeoDataFrame:
        swath_gpd =  GeoDataFrame(
            crs=self.EPSG, geometry=GeoSeries(Polygon(cornerpoints)))
        return overlay(overlay_gpd, swath_gpd, how='intersection')

    def plot_gpd(self, shape_gpd: GeoDataFrame, color:str='black') -> None:
        shape_gpd.plot(ax=self.ax, facecolor='none', edgecolor=color, linewidth=0.5)

    def difference(self, main_layer: GeoDataFrame, layers: list[GeoDataFrame]) -> GeoDataFrame:
        main_layer = main_layer.rename(columns={'LAYER':'LAYERi'})
        for layer in layers:
            if layer is None or layer.empty:
                continue

            try:
                main_layer = overlay(main_layer, layer, how='difference')

            except IndexError:
                pass

        return main_layer

    def intersection(self, layer1: GeoDataFrame, layer2: GeoDataFrame) -> GeoDataFrame:
        # to avoid duplicate layer warning
        layer1 = layer1.rename(columns={'LAYER':'LAYERi'})
        try:
            return overlay(layer1, layer2, how='intersection')

        except (AttributeError, IndexError, KeyError):
            return

    def calc_area_and_plot(self, area_gpd: GeoDataFrame, color: str|None) -> float:
        area = 0.0
        if area_gpd is not None:
            area = sum(area_gpd.geometry.area.to_list())/ 1e6
            if color and area > 0 and area_gpd['geometry'].all():
                self.plot_gpd(area_gpd, color)

        return area

    @staticmethod
    def plot() -> None:
        plt.show()
