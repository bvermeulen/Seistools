from shapely.geometry.polygon import Polygon
import geopandas as gpd
from geopandas import GeoDataFrame, GeoSeries, overlay


class Gis:
    # GIS geopandas methods

    def __init__(self, cfg, ax):
        self.EPSG = cfg.EPSG
        self.shapefile_src = cfg.shapefile_src
        self.shapefile_rcv = cfg.shapefile_rcv
        self.shapefile_rough = cfg.shapefile_rough
        self.shapefile_facilities = cfg.shapefile_facilities
        self.shapefile_dune = cfg.shapefile_dune
        self.shapefile_sabkha = cfg.shapefile_sabkha
        self.shapefile_infill = cfg.shapefile_infill
        self.ax = ax
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

    @staticmethod
    def get_bounds(area_gpd) -> list:
        bounds = area_gpd.bounds.iloc[0].to_list()
        return bounds

    def create_sw_gpd(self, cornerpoints, overlay_gpd):
        swath_gpd =  GeoDataFrame(
            crs=self.EPSG, geometry=GeoSeries(Polygon(cornerpoints)))
        return overlay(overlay_gpd, swath_gpd, how='intersection')

    def plot_gpd(self, shape_gpd, color='black') -> None:
        shape_gpd.plot(ax=self.ax, facecolor='none', edgecolor=color, linewidth=0.5)

    def swath_intersection(self, swath_gpd, terrain_gpd, color) -> float:
        # to avoid duplicate layer warning
        swath_gpd = swath_gpd.rename(columns={'LAYER':'LAYERi'})

        try:
            terrain_gpd = overlay(swath_gpd, terrain_gpd, how='intersection')
            terrain_area = sum(terrain_gpd.geometry.area.to_list())/ 1e6
            if terrain_area > 0 and terrain_gpd['geometry'].all():
                self.plot_gpd(terrain_gpd, color)

        except (AttributeError, IndexError, KeyError):
            terrain_area = 0

        return terrain_area